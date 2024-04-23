import plotly.express as px
import plotly.graph_objs as go
from django_pandas.io import read_frame

def plot_comparison(df, df2):
    fig = px.box(
        df,
        x="Assessment",
        y="value",
        color="pathogen",
        log_y=True,
        labels={"pathogen": "Reference pathogen"},
        title="Risk as probability of infection per year",
        color_discrete_sequence=[
            "#78BEF9",
            "#8081F1",
            "#5F60B3",
            "#3D3E73",
            "#F29C99",
            "#7375D9",
            "#CBCCF4",
        ],
    )

    fig.add_traces(
        list(
            px.box(
                df2,
                x="Assessment",
                y="value",
                color="pathogen",
                log_y=True,
                # labels={
                #  "pathogen": "Reference pathogen"
                #  },
                title="Risk as probability of infection per year",
                color_discrete_sequence=["#7375D9", "#7375D9", "#7375D9", "#7375D9"],
            ).select_traces()
        )
    )

    fig.update_layout(
        font_family="Helvetica Neue, Helvetica, Arial, sans-serif",
        font_color="black",
        title={"text": "Risk assessment as probability of infection per year"},
        yaxis_title="Probability of infection per year",
        annotations=[
            go.Annotation(
                y=-4,
                x=1.2,
                text="Tolerable risk level of 1/10000 infections pppy",
                bgcolor="#0003e2",
                bordercolor="white",
                borderpad=5,
                font=dict(color="white"),
            )
        ]
        # markersize= 12,
    )

    fig.update_layout(
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.2,
            xanchor="left",
            x=0,
            font=dict(family="Courier", size=14, color="black"),
            bgcolor="white",
            bordercolor="#007c9e",
            borderwidth=0,
        )
    )

    fig.add_hline(
        y=0.0001,
        line_dash="dashdot",
        line=dict(color="#0003e2", width=3),
    )

    fig.update_traces(
        marker_size=8, hovertemplate=None, hoverinfo="skip", line=dict(width=0)
    )
    return fig



def simulate_risk(ra):
    # Selecting inflow concentration based in source water type
    df_inflow = read_frame(
        Inflow.objects.filter(water_source=ra.source).values(
            "min", "max", "pathogen__pathogen", "water_source__water_source_name"
        )
    )
    df_inflow = df_inflow[
        df_inflow["pathogen__pathogen"].isin(
            ["Rotavirus", "Campylobacter jejuni", "Cryptosporidium parvum"]
        )
    ]
    # Querying dose response parameters based on pathogen inflow
    dr_models = read_frame(
        DoseResponse.objects.filter(
            pathogen__in=Pathogen.objects.filter(
                pathogen__in=df_inflow["pathogen__pathogen"]
            )
        )
    )

    # Querying for Logremoval based on selected treatments
    df_treatment = read_frame(
        LogRemoval.objects.filter(treatment__in=ra.treatment.all()).values(
            "min", "max", "treatment__name", "pathogen_group__pathogen_group"
        )
    )

    # Summarizing treatment to treatment max and treatment min
    # df_treatment_summary=df_treatment.groupby(["pathogen_group__pathogen_group"]).sum().reset_index()
    df_treatment_summary = (
        df_treatment.groupby(["pathogen_group__pathogen_group"])[["min", "max"]]
        .apply(lambda x: x.sum())
        .reset_index()
    )

    results = pd.DataFrame()

    for index, row in df_inflow.iterrows():
        d = df_inflow.loc[df_inflow["pathogen__pathogen"] == row["pathogen__pathogen"]]
        dr = dr_models.loc[dr_models["pathogen"] == row["pathogen__pathogen"]]

        if row["pathogen__pathogen"] == "Rotavirus":
            selector = "Viruses"
        elif row["pathogen__pathogen"] == "Cryptosporidium parvum":
            selector = "Protozoa"
        else:
            selector = "Bacteria"
        # result.append(selector)

        df_treat = df_treatment_summary[
            df_treatment_summary["pathogen_group__pathogen_group"] == selector
        ]

        risk_df = pd.DataFrame(
            {
                "inflow": np.random.normal(
                    loc=(
                        np.log10(float(d["min"]) + 10 ** (-8))
                        + np.log10(float(d["max"]))
                    )
                    / 2,
                    scale=(
                        np.log10(float(d["max"]))
                        - np.log10(float(d["min"]) + 10 ** (-8))
                    )
                    / 4,
                    size=10000,
                ),
                "LRV": np.random.uniform(
                    low=df_treat["min"], high=df_treat["min"], size=10000
                ),
                "LRVmax": np.random.uniform(
                    low=df_treat["max"], high=df_treat["max"], size=10000
                ),
            }
        )
        risk_df["outflow"] = risk_df["inflow"] - risk_df["LRV"]
        risk_df["outflow_min"] = risk_df["inflow"] - risk_df["LRVmax"]

        risk_df["dose"] = (10 ** risk_df["outflow"]) * float(
            ra.exposure.volume_per_event
        )
        risk_df["dose_min"] = (10 ** risk_df["outflow_min"]) * float(
            ra.exposure.volume_per_event
        )

        if selector != "Protozoa":
            risk_df["probs"] = 1 - (
                1 + (risk_df["dose"]) * (2 ** (1 / float(dr.alpha)) - 1) / float(dr.n50)
            ) ** -float(dr.alpha)
            risk_df["probs_min"] = 1 - (
                1
                + (risk_df["dose_min"])
                * (2 ** (1 / float(dr.alpha)) - 1)
                / float(dr.n50)
            ) ** -float(dr.alpha)

        else:
            risk_df["probs"] = 1 - np.exp(-float(dr.k) * (risk_df["dose"]))
            risk_df["probs_min"] = 1 - np.exp(-float(dr.k) * (risk_df["dose_min"]))

        results[row["pathogen__pathogen"] + "_MinimumLRV"] = [
            annual_risk(int(ra.exposure.events_per_year), risk_df["probs"])
            for _ in range(1000)
        ]
        results[row["pathogen__pathogen"] + "_MaximumLRV"] = [
            annual_risk(int(ra.exposure.events_per_year), risk_df["probs_min"])
            for _ in range(1000)
        ]

    results_long = pd.melt(results)
    results_long["log probability"] = np.log10(results_long["value"])
    return results_long
