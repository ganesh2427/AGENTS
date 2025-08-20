import streamlit as st
import os
import tempfile
import traceback
from runner import run_agent_wrapper


os.environ["CREWAI_DISABLE_TELEMETRY"] = "true"
os.environ["CREWAI_STORAGE_DIR"] = "/tmp/crewai_storage"



# Initialize storage directory for ChromaDB before anything else
if "CREWAI_STORAGE_DIR" not in os.environ:
    temp_dir = tempfile.mkdtemp()
    os.environ["CREWAI_STORAGE_DIR"] = temp_dir

st.set_page_config(
    page_title="AI Development Crew", 
    page_icon="🤖", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sidebar Settings
st.sidebar.title("⚙️ Settings")
st.sidebar.markdown("---")

# Model Selection
model_choice = st.sidebar.selectbox(
    "🧠 Choose AI Model", 
    ["gpt-4", "gpt-3.5-turbo", "gpt-4-turbo"],
    index=0,
    help="Select the AI model for your crew"
)

# Temperature Control
temperature = st.sidebar.slider(
    "🌡️ Temperature", 
    min_value=0.0, 
    max_value=1.0, 
    value=0.7, 
    step=0.1,
    help="Controls creativity: Lower = more focused, Higher = more creative"
)

# Additional Settings
st.sidebar.markdown("### 🔧 Advanced Options")
max_tokens = st.sidebar.number_input(
    "Max Tokens", 
    min_value=100, 
    max_value=4000, 
    value=2000,
    help="Maximum length of the response"
)

enable_memory = st.sidebar.checkbox(
    "Enable Memory", 
    value=True,
    help="Allow the crew to remember previous conversations"
)

# Sidebar Info
st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Session Info")
st.sidebar.info(f"Model: {model_choice}\nTemperature: {temperature}\nMax Tokens: {max_tokens}")

# Main App
st.title("🚀 Latest AI Development Crew")
st.markdown("Ask questions about AI development, trends, and technologies!")

# Input Section
col1, col2 = st.columns([3, 1])
with col1:
    user_input = st.text_input(
        "💬 Ask something about AI:", 
        placeholder="e.g., Latest trends in Agentic AI, Machine Learning advancements...",
        help="Enter your question about AI development"
    )
with col2:
    st.markdown("<br>", unsafe_allow_html=True)  # Add spacing
    run_button = st.button("🚀 Run Agent", type="primary", use_container_width=True)

# Example Questions
st.markdown("### 💡 Example Questions")
example_cols = st.columns(3)
with example_cols[0]:
    if st.button("🤖 Agentic AI Trends", use_container_width=True):
        user_input = "Latest trends in Agentic AI"
with example_cols[1]:
    if st.button("🧠 LLM Developments", use_container_width=True):
        user_input = "Recent developments in Large Language Models"
with example_cols[2]:
    if st.button("🔬 AI Research", use_container_width=True):
        user_input = "Cutting-edge AI research breakthroughs"

# Process Input
if run_button or user_input:
    if user_input.strip():
        # Show settings being used
        with st.expander("🔍 Current Settings", expanded=False):
            st.json({
                "model": model_choice,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "memory_enabled": enable_memory
            })
        
        # Progress and execution
        with st.spinner(f"🤖 Running AI crew with {model_choice}..."):
            try:
                # Pass settings to your crew (you'll need to modify runner.py to accept these)
                result = run_agent_wrapper(user_input)
                
                if isinstance(result, dict) and "error" in result:
                    st.warning(f"⚠️ {result['message']}")
                    st.info("App running in fallback mode - knowledge features disabled but core functionality works.")
                    
                    # Show error details in expander
                    with st.expander("🔍 Error Details"):
                        st.code(result['error'])
                else:
                    st.success("✅ Agent completed successfully!")
                    
                    # Enhanced Output Display with Tabs
                    tab1, tab2, tab3 = st.tabs(["📄 Formatted Result", "🔤 Raw Output", "📊 Analysis"])
                    
                    with tab1:
                        st.markdown("### 🎯 AI Development Insights")
                        if isinstance(result, str):
                            # Format the result nicely
                            st.markdown(result)
                        else:
                            st.write(result)
                    
                    with tab2:
                        st.markdown("### 📝 Raw Output")
                        st.code(str(result), language="text")
                    
                    with tab3:
                        st.markdown("### 📊 Response Analysis")
                        if isinstance(result, str):
                            word_count = len(result.split())
                            char_count = len(result)
                            
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Word Count", word_count)
                            with col2:
                                st.metric("Character Count", char_count)
                            with col3:
                                st.metric("Model Used", model_choice)
                        
                        # Add download button
                        st.download_button(
                            label="📥 Download Result",
                            data=str(result),
                            file_name=f"ai_crew_result_{user_input[:20]}.txt",
                            mime="text/plain"
                        )
                        
            except Exception as e:
                st.error("❌ An error occurred!")
                with st.expander("🔍 Full Error Details"):
                    st.code(traceback.format_exc())
    else:
        st.warning("⚠️ Please enter a question about AI.")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        🤖 Powered by CrewAI | Built with Streamlit
    </div>
    """, 
    unsafe_allow_html=True
)

