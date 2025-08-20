# app.py
import streamlit as st
from crewai_agent import respond
import os

st.set_page_config(page_title="CrewAI", layout="wide")
st.title("CrewAI — Web UI")

if "history" not in st.session_state:
    st.session_state.history = []

with st.form("prompt_form", clear_on_submit=True):
    prompt = st.text_area("Prompt", height=160, placeholder="Type something for CrewAI...")
    submitted = st.form_submit_button("Send")

if submitted:
    if not prompt.strip():
        st.warning("Please type a prompt.")
    else:
        with st.spinner("CrewAI is thinking..."):
            try:
                result = respond(prompt)
            except Exception as e:
                result = f"[Error while calling agent] {e}"
        st.session_state.history.append({"prompt": prompt, "response": result})

st.markdown("### Conversation (most recent first)")
for turn in reversed(st.session_state.history[-30:]):
    st.markdown(f"**User:** {turn['prompt']}")
    st.markdown(f"**CrewAI:** {turn['response']}")
