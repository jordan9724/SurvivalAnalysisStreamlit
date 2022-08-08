import streamlit as st

from utils.credentials import check_password
from utils.graphs import get_survival_plotly_fig
from utils.mongo import get_account_ids, get_graph_df


def app():
    # Security check
    if not check_password():
        return

    # Runs App
    st.title("Risk Forecast")

    # Loads accounts
    account_id = st.selectbox("Account", get_account_ids())

    # Prints graph
    graph_df = get_graph_df(account_id)
    fig = get_survival_plotly_fig(
        graph_df=graph_df,
        x=graph_df["survival_duration"],
        y=(1 - graph_df["estimated_surviving_percent"]),
        # These are reversed since y is reversed
        y_upper=(1 - graph_df["confidence_lower"]),
        y_lower=(1 - graph_df["confidence_upper"]),
        n_subscriptions=graph_df["all_at_risk"].iloc[0]
    )
    st.plotly_chart(fig)


if __name__ == "__main__":
    app()
