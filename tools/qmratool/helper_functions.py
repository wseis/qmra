import plotly.express as px
from plotly.offline import plot
import plotly.graph_objs as go

def plot_comparison(df, df2):
    fig = px.box(df, x="Assessment", y="value", 
                    color="pathogen", 

                    log_y =True, 
                    labels={
                     "pathogen": "Reference pathogen"
                     },
                    title="Risk as probability of infection per year",
                    color_discrete_sequence=["#004254", "#007c9e", "#a3d1ec","#3494ae","#00B8eb"])

    fig.add_traces(
    list(px.box(df2, x="Assessment", y="value", 
                    color="pathogen", 

                    log_y =True, 
                   # labels={
                   #  "pathogen": "Reference pathogen"
                   #  },
                    title="Risk as probability of infection per year",
                    color_discrete_sequence=["#00566E", "#00566E", "#00566E","#00566E","#00566E"]).select_traces()
    ))


    fig.update_layout(
        font_family="Helvetica Neue, Helvetica, Arial, sans-serif",
        font_color="black",
        title = {'text':'Risk assessment as probability of infection per year'},

        yaxis_title = "Probability of infection per year",
        annotations=[go.Annotation(y = -4, x =1.2,
                text = "Tolerable risk level of 1/10000 infections pppy",
                bgcolor = "#007c9f",
                bordercolor= "white",
                borderpad = 5,
                font = dict(color = "white"))]

        #markersize= 12,
        )

    fig.update_layout(legend=dict(
                    orientation="h",
                    yanchor="top",
                    y=-.2,
                    xanchor="left",
                    x=0,
                       font=dict(
                        family="Courier",
                        size=14,
                        color="black"
                    ),
                    bgcolor="white",
                    bordercolor="#007c9e",
                    borderwidth=0))


    fig.add_hline(y=0.0001, line_dash="dashdot", line=dict(color="#007c9f", width = 3),

     )

    fig.update_traces(marker_size = 8,hovertemplate=None, hoverinfo="skip",
         line=dict(width=0))
    return fig
