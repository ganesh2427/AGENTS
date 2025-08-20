import streamlit as st
from runner import run_agent_wrapper

st.set_page_config(page_title="AI Development Crew", page_icon="🤖", layout="wide")

st.title("🚀 Latest AI Development Crew")

user_input = st.text_input("Ask something about AI:", "")

if st.button("Run Agent"):
    if user_input.strip():
        result = run_agent_wrapper(user_input)

        if isinstance(result, dict) and "error" in result:
            st.error(f"⚠️ {result['message']}\n\nDetails: {result['error']}")
        else:
            st.success("✅ Agent Result")
            st.write(result)
