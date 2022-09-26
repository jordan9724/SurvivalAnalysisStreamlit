import urllib

import certifi
import pandas as pd
import pymongo
import streamlit as st

ca = certifi.where()


# Loads mongo credentials
def get_mongo_client(host, username=None, password=None):
    if host in ["host.docker.internal", "localhost"]:
        return pymongo.MongoClient(
            host if bool(username) is False
            else f"mongodb://{username}:{password}@{host}"
        )
    else:
        return pymongo.MongoClient(
            f"mongodb+srv://{username}:{urllib.parse.quote(password)}@{host}",
            tlsCAFile=ca,
        )


client = get_mongo_client(**st.secrets["mongo"])
db = client[st.secrets["mongo-access"]["db"]]
collection = db[st.secrets["mongo-access"]["collection"]]


# Loads the baseline graph from mongo and stores as a dataframe
@st.cache
def get_graph_df(account_id: str, survival_type: str, month):
    graphs = list(
        collection.find({"account_id": account_id, "survival_type": survival_type, "category_name": None, "month": month})
    )
    # print(account_id, survival_type, month)
    if len(graphs) != 1:
        print(len(graphs))
        return
    baseline_graph = graphs[0]
    graph_df = pd.DataFrame(baseline_graph["data"])
    graph_df.name = str(month.date()) if month else ""
    return graph_df


def get_months(account_id: str, survival_type: str):
    return list(collection.find({"account_id": account_id, "survival_type": survival_type}).distinct("month"))


def get_account_ids():
    return collection.distinct("account_id")
