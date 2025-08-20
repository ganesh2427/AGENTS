import streamlit as st
import os
import tempfile
from runner import run_agent_wrapper

# Initialize storage directory for ChromaDB before anything else
if "CREWAI_STORAGE_DIR" not in os.environ:
    temp_dir = tempfile.mkdtemp()
    os.environ["CREWAI_STORAGE_DIR"] = temp_dir

st.set_page_config(page_title="AI Development Crew", page_icon="🤖", layout="wide")

st.title("🚀 Latest AI Development Crew")

user_input = st.text_input("Ask something about AI:", "")

if st.button("Run Agent"):
    if user_input.strip():
        try:
            result = run_agent_wrapper(user_input)
            
            if isinstance(result, dict) and "error" in result:
                st.warning(f"⚠️ {result['message']}")
                st.info("App running in fallback mode - knowledge features disabled but core functionality works.")
            else:
                st.success("✅ Agent Result")
                st.write(result)
                
        except Exception as e:
            if "chromadb" in str(e).lower():
                st.warning("Knowledge features disabled. App running in fallback mode.")
                st.info("Retrying without ChromaDB...")
                # Retry the operation
                try:
                    result = run_agent_wrapper(user_input)
                    st.success("✅ Agent Result (Fallback Mode)")
                    st.write(result)
                except Exception as retry_error:
                    st.error(f"Error: {str(retry_error)}")
            else:
                st.error(f"Error: {str(e)}")
    else:
        st.warning("Please enter a question about AI.")