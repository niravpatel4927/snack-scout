import sqlite3
import streamlit as st

st.title("Snack Scout")

conn = sqlite3.connect("snack-scout.db")
rows = conn.execute("SELECT id, name, category, why_it_matches_you, source_url, feedback FROM findings ORDER BY date_found DESC"
).fetchall()

for row_id, name, category, why, url, feedback in rows:
    col1, col2, col3 = st.columns([4, 1, 1])
    with col1:
        st.markdown(f"**{name}** ({category}) - {why}\n\n[source]({url})")
    with col2:
        if st.button("👍", key=f"up-{row_id}"):
            conn.execute("UPDATE findings SET feedback = 'up' WHERE id = ?", (row_id,))
            conn.commit()
    with col3:
        if st.button("👎", key=f"down-{row_id}"):
            conn.execute("UPDATE findings SET feedback = 'down' WHERE id = ?", (row_id,))
            conn.commit()