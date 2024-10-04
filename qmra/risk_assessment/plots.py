from plotly import graph_objects as go
from plotly.offline import plot
from plotly import express as px
import pandas as pd


def risk_plots(risk_assessment_results):
    infection_prob_fig = go.Figure()
    dalys_fig = go.Figure()
    for r in risk_assessment_results:
        infection_prob_fig.add_trace(go.Box(
            x=["Minimum LRV", "Maximum LRV"],
            lowerfence=[r.infection_minimum_lrv_min, r.infection_maximum_lrv_min],
            upperfence=[r.infection_minimum_lrv_max, r.infection_maximum_lrv_max],
            q1=[r.infection_minimum_lrv_q1, r.infection_maximum_lrv_q1],
            q3=[r.infection_minimum_lrv_q3, r.infection_maximum_lrv_q3],
            median=[r.infection_minimum_lrv_median, r.infection_maximum_lrv_median],
            name=r.pathogen,
        ))
        dalys_fig.add_trace(go.Box(
            x=["Minimum LRV", "Maximum LRV"],
            lowerfence=[r.dalys_minimum_lrv_min, r.dalys_maximum_lrv_min],
            upperfence=[r.dalys_minimum_lrv_max, r.dalys_maximum_lrv_max],
            q1=[r.dalys_minimum_lrv_q1, r.dalys_maximum_lrv_q1],
            q3=[r.dalys_minimum_lrv_q3, r.dalys_maximum_lrv_q3],
            median=[r.dalys_minimum_lrv_median, r.dalys_maximum_lrv_median],
            name=r.pathogen,
        ))

    infection_prob_fig.update_layout(
        boxmode='group',
        # font_family="Helvetica Neue, Helvetica, Arial, sans-serif",
        font_color="black",
        # plot_bgcolor=bgcolor,
        xaxis_title="",
        yaxis_title="Probability of infection per year",
        margin=dict(l=0, r=0, t=0, b=0),
        legend=dict(
            orientation="h",
            yanchor="top",
            xanchor="center",
            x=0.5,
        )
    )
    infection_prob_fig.update_yaxes(type="log")
    infection_prob_fig.add_hline(y=0.0001, line_dash="dashdot",
                                 # line=dict(color=lcolor, width=3)
                                 )
    infection_prob_fig.update_traces(
        marker_size=8
    )

    dalys_fig.update_layout(
        boxmode='group',
        # font_family="Helvetica Neue, Helvetica, Arial, sans-serif",
        font_color="black",
        # plot_bgcolor=bgcolor,
        xaxis_title="",
        yaxis_title="DALYs pppy",
        margin=dict(l=0, r=0, t=0, b=0),
        legend=dict(
            orientation="h",
            yanchor="top",
            xanchor="center",
            x=0.5,
        )
    )
    dalys_fig.update_yaxes(type="log")
    dalys_fig.add_hline(y=0.000001, line_dash="dashdot",
                        # line=dict(color=lcolor, width=3)
                        )
    dalys_fig.update_traces(
        marker_size=8
    )

    return plot(infection_prob_fig, output_type="div", config={'displayModeBar': False}, include_plotlyjs=False), \
        plot(dalys_fig, output_type="div", config={'displayModeBar': False}, include_plotlyjs=False)


def inflows_plot(inflows):
    df = pd.DataFrame.from_records([i.__dict__ for i in inflows])
    # print(df.head())
    # reshaping dataframe for plotting
    df_inflow2 = pd.melt(
        df,
        ("pathogen",), value_vars=("min", "max")
    )

    df_inflow2 = df_inflow2.rename(
        columns={"pathogen": "Pathogen", "variable": ""}
    )
    fig2 = px.bar(
        df_inflow2,
        x="",
        y="value",
        log_y=True,
        facet_col="Pathogen",
        barmode="group",
        # color_discrete_sequence=risk_colors_extended,
    )

    fig2.for_each_annotation(
        lambda a: a.update(
            text=a.text.split("=")[-1], font=dict(size=10, color="black"),
        )
    )

    fig2.update_layout(
        # font_family="Helvetica Neue, Helvetica, Arial, sans-serif",
        font_color="black",
        yaxis_title="Source water concentrations in N/L",
        margin=dict(l=0, r=0, t=40, b=0),
    )

    return plot(fig2, output_type="div", config={'displayModeBar': False}, include_plotlyjs=False)


def treatments_plot(treatments):
    # reshaping
    df = pd.DataFrame.from_records([i.__dict__ for i in treatments])
    # print(df.head().loc[:, ["bacteria_min", "name", "viruses_max"]])
    df = pd.melt(df,
                 ("name",), value_vars=(
            "bacteria_min", "bacteria_max", "viruses_min", "viruses_max", "protozoa_min", "protozoa_max"
        ),
                 var_name="metric"
                 )
    splitted = df.metric.str.split("_", expand=True)
    df["Pathogen Group"] = splitted[0]
    df[""] = splitted[1]
    df = df.rename(
        columns={
            "name": "Treatment",
        }
    )
    # print(df.head())
    fig = px.bar(
        df,
        x="",
        y="value",
        color="Treatment",
        facet_col="Pathogen Group",
        category_orders={"Pathogen Group": ["viruses", "bacteria", "protozoa"]},
        # color_discrete_sequence=risk_colors_extended,
    )

    fig.for_each_annotation(
        lambda a: a.update(text=a.text.split("=")[-1], font=dict(size=13))
    )
    fig.update_layout(
        margin=dict(l=0, r=0, t=20, b=0),
        legend=dict(orientation="h", yanchor="top",
                    xanchor="center",
                    x=0.5, ),
        # font_family="Helvetica Neue, Helvetica, Arial, sans-serif",
        font_color="black",
        yaxis_title="Logremoval of individual treatment step",
    )

    return plot(fig, output_type="div", config={'displayModeBar': False}, include_plotlyjs=False)
