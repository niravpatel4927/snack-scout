import os
import psycopg2
from dotenv import load_dotenv
import streamlit as st

load_dotenv()

st.title("Snack Scout")

conn = psycopg2.connect(os.environ["DATABASE_URL"])
cur = conn.cursor()
cur.execute("SELECT id, name, category, why_it_matches_you, source_url, feedback FROM findings ORDER BY date_found DESC")
rows = cur.fetchall()

for row_id, name, category, why, url, feedback in rows:
    col1, col2, col3 = st.columns([4, 1, 1])
    with col1:
        st.markdown(f"**{name}** ({category}) — {why}\n\n[source]({url})")
    with col2:
        if st.button("👍", key=f"up-{row_id}"):
            cur.execute("UPDATE findings SET feedback='up' WHERE id=%s", (row_id,))
            conn.commit()
    with col3:
        if st.button("👎", key=f"down-{row_id}"):
            cur.execute("UPDATE findings SET feedback='down' WHERE id=%s", (row_id,))
            conn.commit()