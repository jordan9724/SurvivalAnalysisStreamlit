import plotly.graph_objs as go
import numpy as np


def get_survival_plotly_graphs(graph_df, x, y, y_upper, y_lower, color, show_lines_only):
    survival_line = go.Scatter(
        name=f'Churn Risk {graph_df.name or "Baseline"}',
        x=x,
        y=y,
        mode='lines',
        line=dict(color=color),
        line_shape="hv",
    )
    if show_lines_only:
        return [survival_line]

    confidence_upper = go.Scatter(
        name='Upper Confidence',
        x=x,
        y=y_upper,
        mode='lines',
        marker=dict(color="#444"),
        line=dict(width=0),
        showlegend=False,
        line_shape="hv",
    )
    confidence_lower = go.Scatter(
        name='Lower Confidence',
        x=x,
        y=y_lower,
        marker=dict(color="#444"),
        line=dict(width=0),
        mode='lines',
        fillcolor='rgba(68, 68, 68, 0.3)',
        fill='tonexty',
        showlegend=False,
        line_shape="hv",
    )
    active_customers = go.Scatter(
        name="Active Customer Volume",
        mode="markers",
        x=x,
        y=y,
        hovertemplate="%{text}",
        text=graph_df["active_at_risk"],
        marker=dict(color="rgba(31, 119, 180, 1)", line=dict(width=0), size=(graph_df["active_at_risk"] / np.max(graph_df["active_at_risk"])) * 19 + 1),
    )
    censored_customers = go.Scatter(
        name="Censored Customers",
        mode="markers",
        x=x,
        y=y,
        hovertemplate="%{text}",
        text=graph_df["censored"],
        marker=dict(color="rgba(124, 144, 163, 1)", line=dict(width=0), size=(graph_df["censored"] / np.max(graph_df["censored"])) * 19 + 1),
    )
    churned_customers = go.Scatter(
        name="Churned Customers",
        mode="markers",
        x=x,
        y=y,
        hovertemplate="%{text}",
        text=graph_df["observed"],
        marker=dict(color="rgba(227, 115, 111, 1)", line=dict(width=0), size=(graph_df["observed"] / np.max(graph_df["observed"])) * 19 + 1),
    )

    return [
        confidence_upper,
        confidence_lower,
        churned_customers,
        censored_customers,
        active_customers,
        survival_line,
    ]


def get_survival_plotly_fig(graph_dfs: list, survival_type, show_lines_only) -> go.Figure:
    colors = [
        "rgb(34, 124, 157)",
        "rgb(23, 195, 178)",
        "rgb(255, 203, 119)",
        "rgb(254, 109, 115)",
    ]

    all_traces = []
    for i, graph_df in enumerate(graph_dfs):
        if graph_df is None:
            continue
        x = graph_df["survival_duration"]
        y = (1 - graph_df["estimated_surviving_percent"])
        # These are reversed since y is reversed
        y_upper = (1 - graph_df["confidence_lower"])
        y_lower = (1 - graph_df["confidence_upper"])
        all_traces += get_survival_plotly_graphs(graph_df, x, y, y_upper, y_lower, colors[i%len(colors)], show_lines_only)

    fig = go.Figure(all_traces)

    fig.update_traces(hoverlabel={"namelength" :-1})

    n_subscriptions = graph_dfs[0]["all_at_risk"].iloc[0]
    fig.update_layout(title=f'Ran on {n_subscriptions} Subscriptions')
    fig.update_layout(xaxis_title=survival_type.title().replace("_", " "))
    fig.update_layout(yaxis_title='Churn Risk', yaxis_range=[-.05, 1.05], yaxis_tickformat='.1%')
    fig.update_layout(hovermode="x")

    return fig
