import pandas as pd
import pymongo
import streamlit as st
import plotly.graph_objs as go
import psycopg2

# Loads mongo credentials
client = pymongo.MongoClient(host=st.secrets["mongo"]["host"], port=st.secrets["mongo"]["port"])
db = client[st.secrets["mongo"]["db"]]
collection = db[st.secrets["mongo"]["collection"]]


# Loads postgres credentials
@st.experimental_singleton
def init_connection():
    return psycopg2.connect(**st.secrets["postgres"])


conn = init_connection()


# Performs query
# Uses st.experimental_memo to only rerun when the query changes or after 10 min.
@st.experimental_memo(ttl=600)
def run_query(query):
    with conn.cursor() as cur:
        cur.execute(query)
        return cur.fetchall()


# Loads the baseline graph from mongo and stores as a dataframe
@st.cache
def load_graph(account_id: str):
    graphs = list(
        collection.find({"account_id": account_id, "survival_type": "days", "category_name": None, "month": None})
    )
    if len(graphs) != 1:
        print(len(graphs))
        return
    baseline_graph = graphs[0]
    return pd.DataFrame(baseline_graph["data"])


# Begin App
st.title("Risk Forecast")

# Loads accounts
all_account_ids = collection.distinct("account_id")
all_account_ids_fmt = "('{}')".format("', '".join(all_account_ids))
account_name_map = dict(list(run_query(f"SELECT a.id, a.name FROM \"Account\" a WHERE a.id IN {all_account_ids_fmt}")))

account_id = st.selectbox(
    "Account",
    all_account_ids,
    format_func=lambda _account_id: f"{account_name_map[_account_id]} ({_account_id[:6]}...)"
)

# Prints graph
graph_df = load_graph(account_id)
x = graph_df["survival_duration"]
y = 1 - graph_df["estimated_surviving_percent"]
# These are reversed since y is reversed
y_upper = 1 - graph_df["confidence_lower"]
y_lower = 1 - graph_df["confidence_upper"]
fig = go.Figure([
    go.Scatter(
        name='Churn Risk',
        x=x,
        y=y,
        mode='lines',
        line=dict(color='rgb(31, 119, 180)'),
    ),
    go.Scatter(
        name='Upper Confidence',
        x=x,
        y=y_upper,
        mode='lines',
        marker=dict(color="#444"),
        line=dict(width=0),
        showlegend=False
    ),
    go.Scatter(
        name='Lower Confidence',
        x=x,
        y=y_lower,
        marker=dict(color="#444"),
        line=dict(width=0),
        mode='lines',
        fillcolor='rgba(68, 68, 68, 0.3)',
        fill='tonexty',
        showlegend=False
    )
])
fig.update_layout(yaxis_range=[0, 1])
fig.update_layout(
    yaxis_title='Churn Risk',
    yaxis_tickformat='.1%',
    xaxis_title="Days",
    title=f'Baseline - Ran on {graph_df["all_at_risk"].iloc[0]} Subscriptions',
    hovermode="x"
)
st.plotly_chart(fig)
