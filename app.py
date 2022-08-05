import urllib

import pandas as pd
import pymongo
import streamlit as st
import plotly.graph_objs as go
import certifi

ca = certifi.where()


# Loads mongo credentials
def get_mongo_client(host, username=None, password=None):
    return pymongo.MongoClient(
        host if bool(username) is False
        else f"mongodb://{username}:{password}@{host}" if host == "host.docker.internal"
        else f"mongodb+srv://{username}:{urllib.parse.quote(password)}@{host}",
        tlsCAFile=ca,
    )


client = get_mongo_client(**st.secrets["mongo"])
db = client[st.secrets["mongo-access"]["db"]]
collection = db[st.secrets["mongo-access"]["collection"]]


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

account_id = st.selectbox(
    "Account",
    all_account_ids,
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
        name='Confidence Upper',
        x=x,
        y=y_upper,
        mode='lines',
        marker=dict(color="#444"),
        line=dict(width=0),
        showlegend=False
    ),
    go.Scatter(
        name='Confidence Lower',
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
