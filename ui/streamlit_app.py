"""
MVP Streamlit UI for lawdz.
Run: streamlit run ui/streamlit_app.py
It calls the Django backend API.
"""

import streamlit as st
import requests
import os

st.set_page_config(page_title="Lawdz - Algerian Law Assistant", page_icon="⚖️")
st.title("⚖️ Lawdz — Algerian Law Chatbot (MVP)")

st.caption("Answers are based on Algerian legislation. This is NOT legal advice.")

API_URL = os.getenv("DJANGO_API_URL", "http://localhost/api/chat/")

query = st.text_area("Describe your legal problem or ask a question (FR or AR)", height=100)

lang = st.selectbox("Preferred answer language", ["auto", "fr", "ar"], index=0)

if st.button("Ask", type="primary") and query.strip():
    with st.spinner("Searching the law..."):
        try:
            payload = {"query": query.strip()}
            if lang != "auto":
                payload["lang"] = lang

            resp = requests.post(API_URL, json=payload, timeout=60)
            data = resp.json()

            st.markdown("### Answer")
            st.write(data.get("answer", "No answer."))

            if data.get("citations"):
                st.markdown("### Sources")
                for c in data["citations"]:
                    st.markdown(f"- **{c.get('code', '?')}** — {c.get('article', '')}  \n  {c.get('source_url', '')}")

            st.warning(data.get("disclaimer", "This is not legal advice."))

        except Exception as e:
            st.error(f"Error contacting backend: {e}")
            st.info("Make sure Django is running (docker compose or runserver) and API is reachable.")

st.divider()
st.markdown("""
**Disclaimer**: Informational use only. Verify with official Journal Officiel (joradp.dz) and consult a lawyer.

[GitHub](https://github.com/) | Sources: JORADP
""")
