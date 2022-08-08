import plotly.graph_objs as go
import numpy as np


def get_survival_plotly_fig(graph_df, x, y, y_upper, y_lower, n_subscriptions) -> go.Figure:
    survival_line = go.Scatter(
        name='Churn Risk',
        x=x,
        y=y,
        mode='lines',
        line=dict(color='rgb(31, 119, 180)'),
        line_shape="hv",
    )
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

    fig = go.Figure([
        survival_line,
        confidence_upper,
        confidence_lower,
        active_customers,
        censored_customers,
        churned_customers,
    ])

    fig.update_traces(hoverlabel={"namelength" :-1})

    fig.update_layout(title=f'Baseline - Ran on {n_subscriptions} Subscriptions')
    fig.update_layout(xaxis_title="Days")
    fig.update_layout(yaxis_title='Churn Risk', yaxis_range=[0, 1], yaxis_tickformat='.1%')
    fig.update_layout(hovermode="x")

    return fig
