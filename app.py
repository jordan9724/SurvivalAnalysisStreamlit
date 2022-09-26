import streamlit as st

st.set_page_config(page_title="Baseline Graphs", layout="wide")

from utils.credentials import check_password
from utils.graphs import get_survival_plotly_fig
from utils.mongo import get_account_ids, get_graph_df, get_months
# from utils.postgres import get_account_name_map


def app():
    # Security check
    if not check_password():
        return

    # Runs App
    st.title("Risk Forecast")

    # Set up columns
    col1, col2, col3 = st.columns(3)

    # Account Select
    account_ids = get_account_ids()
    # account_name_map = get_account_name_map(account_ids)
    account_name_map = st.secrets.get("account-name-map", {})
    account_id = col1.selectbox(
        "Account",
        account_ids,
        format_func=lambda _account_id: f"{account_name_map[_account_id]} ({_account_id[:6]}...)" if _account_id in account_name_map.keys() else _account_id
    )

    # Survival Type Select
    survival_type = col2.selectbox(
        "Survival Type",
        ["days", "lifetime_value"],
        format_func=lambda s_type: s_type.title().replace("_", " "),
    )

    # Month Select
    months = get_months(account_id, survival_type)
    month = col3.selectbox(
        "Month",
        ["all"] + months,
        format_func=lambda _month: "All" if _month == "all" else str(_month.date()) if _month else "Baseline",
    )

    # Show only lines
    only_lines = st.checkbox("Only show churn lines", True)
    st.markdown(f"### {account_id}")

    # Prints graph
    if month == "all":
        graph_dfs = [
            get_graph_df(account_id, survival_type, month)
            for month in months
        ]
    else:
        graph_dfs = [get_graph_df(account_id, survival_type, month)]
    fig = get_survival_plotly_fig(
        graph_dfs=graph_dfs,
        survival_type=survival_type,
        show_lines_only=only_lines,
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("""
    * **Churn Risk**: Estimated % of subscriptions churning at X days
    * **Confidence** (Greyed area): Most likely range of the real churn risk %
    * **Active Customer Volume**: Total subscriptions who are active after X days
    * **Censored Customers**: Total subscriptions who are active at X days
    * **Churned Customers**: Total subscriptions who churned at X days
    """)


if __name__ == "__main__":
    app()
