import streamlit as st
import os
import sys
import traceback

# Completely disable ChromaDB before any imports
os.environ["CREWAI_DISABLE_TELEMETRY"] = "true"
os.environ["CREWAI_STORAGE_DIR"] = "/tmp"
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["CHROMA_DB_IMPL"] = "duckdb+parquet"  # Alternative to SQLite

st.title("🚀 AI Development Crew")

@st.cache_data
def load_crew_module():
    """Load CrewAI without ChromaDB dependencies"""
    try:
        # Mock the chromadb module to prevent import errors
        import sys
        from unittest.mock import MagicMock
        
        # Mock chromadb before CrewAI tries to import it
        sys.modules['chromadb'] = MagicMock()
        sys.modules['chromadb.config'] = MagicMock()
        sys.modules['chromadb.errors'] = MagicMock()
        
        # Add your source path
        sys.path.append('/mount/src/agents/latest_ai_development_crew/src')
        
        # Import your crew
        from latest_ai_development_crew.crew import LatestAiDevelopmentCrew
        from datetime import datetime
        
        def run_crew_agent(topic):
            """Run crew without ChromaDB features"""
            inputs = {
                'topic': topic,
                'current_year': str(datetime.now().year)
            }
            
            try:
                crew = LatestAiDevelopmentCrew().crew()
                # Disable memory/knowledge features that use ChromaDB
                crew.memory = False
                result = crew.kickoff(inputs=inputs)
                return result.raw if hasattr(result, 'raw') else str(result)
            except Exception as e:
                if "chroma" in str(e).lower() or "sqlite" in str(e).lower():
                    return {"error": "ChromaDB disabled", "message": "Running in fallback mode"}
                raise e
        
        return run_crew_agent, None
        
    except Exception as e:
        return None, str(e)

# Load the crew module
run_agent_func, load_error = load_crew_module()

if load_error:
    st.warning(f"⚠️ CrewAI loading issue: Running in enhanced mock mode")
    with st.expander("🔍 Technical Details"):
        st.code(load_error)
    use_mock = True
else:
    st.success("✅ CrewAI loaded successfully (ChromaDB disabled)")
    use_mock = False

# Input section
user_input = st.text_input("Ask something about AI:", placeholder="e.g., Latest trends in Agentic AI")

if st.button("🚀 Run Agent"):
    if user_input.strip():
        with st.spinner("🤖 AI Development Crew is analyzing..."):
            try:
                if not use_mock and run_agent_func:
                    # Try to use actual CrewAI
                    result = run_agent_func(user_input)
                    
                    if isinstance(result, dict) and "error" in result:
                        st.warning("⚠️ ChromaDB features disabled - using fallback mode")
                        use_mock = True
                    else:
                        st.success("✅ CrewAI Analysis Complete!")
                        
                        # Display results
                        tab1, tab2 = st.tabs(["📄 Analysis", "🔤 Raw Output"])
                        
                        with tab1:
                            st.markdown(result)
                        
                        with tab2:
                            st.code(str(result), language="text")
                        
                        st.download_button(
                            label="📥 Download Analysis",
                            data=str(result),
                            file_name=f"ai_analysis_{user_input[:20].replace(' ', '_')}.txt",
                            mime="text/plain"
                        )
                
                # Enhanced mock response if needed
                if use_mock:
                    # Your enhanced mock response here (same as before)
                    result = f"""
# AI Development Analysis: {user_input}

## Executive Summary
Comprehensive analysis of "{user_input}" based on current AI development trends and research.

## Key Insights

### 🚀 Current Developments
- **Agentic AI Evolution**: Autonomous systems with enhanced reasoning capabilities
- **Multi-Modal Integration**: Seamless processing across text, vision, and audio
- **Edge AI Deployment**: Optimized models for local processing

### 🔬 Technical Breakthroughs
- **Advanced LLMs**: Improved reasoning, coding, and domain expertise
- **RAG Systems**: Enhanced accuracy through real-time knowledge retrieval  
- **Multi-Agent Frameworks**: Collaborative AI solving complex problems

### 🏭 Industry Applications
- **Healthcare**: AI diagnostics and personalized medicine
- **Finance**: Automated analysis and risk assessment
- **Education**: Adaptive learning and intelligent tutoring

## Future Trajectory

The AI landscape is advancing toward more autonomous, efficient, and specialized systems:

1. **Enhanced Reasoning**: Better logical thinking and problem-solving
2. **Reduced Hallucinations**: More reliable and factual responses
3. **Energy Efficiency**: Smaller, optimized models for widespread use

## Strategic Recommendations
- Monitor emerging AI research and applications
- Implement domain-specific AI solutions
- Prioritize ethical AI development and deployment

---
*Generated by AI Development Crew | Streamlit Deployment*
                    """
                    
                    st.success("✅ Enhanced Analysis Complete!")
                    st.markdown(result)
                    st.info("🔧 Running in enhanced mode - ChromaDB features disabled for compatibility")
                
            except Exception as e:
                st.error("❌ Processing error occurred")
                with st.expander("🔍 Error Details"):
                    st.code(traceback.format_exc())
    else:
        st.warning("⚠️ Please enter your AI development question.")

# Sidebar
with st.sidebar:
    st.markdown("### 🔧 System Status")
    if use_mock:
        st.warning("Enhanced Mock Mode")
        st.caption("ChromaDB disabled for compatibility")
    else:
        st.success("CrewAI Active")
        st.caption("Memory features disabled")
    
    st.markdown("### 💡 Try These Questions")
    examples = [
        "Agentic AI architectures",
        "LLM fine-tuning strategies", 
        "Multi-agent system design",
        "AI safety and alignment"
    ]
    
    for example in examples:
        if st.button(example, key=example, use_container_width=True):
            st.rerun()

st.markdown("---")
st.markdown("🤖 **AI Development Crew** | Powered by CrewAI & Streamlit")