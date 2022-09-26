import streamlit as st
import psycopg2


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


def get_account_name_map(account_ids):
    all_account_ids_fmt = "('{}')".format("', '".join(account_ids))
    return dict(list(
        run_query(f"SELECT a.id, a.name FROM \"Account\" a WHERE a.id IN {all_account_ids_fmt}")
    ))

