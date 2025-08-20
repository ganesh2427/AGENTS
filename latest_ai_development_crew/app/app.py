import streamlit as st
from runner import run_agent_wrapper

st.set_page_config(page_title="CrewAI Agent", page_icon="🤖")

st.title("🤖 CrewAI Agent")
st.write("Ask me anything about the latest AI developments!")

user_input = st.text_area("Your question:", "")

if st.button("Run Agent"):
    if user_input.strip():
        with st.spinner("Running agent..."):
            result = run_agent_wrapper(user_input)
        st.success("✅ Done!")
        st.write(result)
    else:
        st.warning("Please enter a question before running the agent.")
