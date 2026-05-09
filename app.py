import streamlit as st
import sys
import os
import importlib.util

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Safely load module despite hyphen in folder name
module_path = os.path.join(os.path.dirname(__file__), ".agent", "skills", "custom-seo", "scripts", "seo_core.py")
if not os.path.isfile(module_path):
    raise FileNotFoundError(f"SEO core module not found: {module_path}")

spec = importlib.util.spec_from_file_location("seo_core", module_path)
if spec is None or spec.loader is None:
    raise ImportError(f"Cannot load seo_core module from path: {module_path}")

seo_core = importlib.util.module_from_spec(spec)
spec.loader.exec_module(seo_core)

# Assign function to a variable for easy use
analyze_single_url = seo_core.analyze_single_url

# ──────────────────────────────────────────
# STREAMLIT UI CODE STARTS HERE
# ──────────────────────────────────────────
st.set_page_config(page_title="Mr Moosa SEO Agent", layout="wide")
st.title("🔍 Mr Moosa AI — Free SEO Audit Tool")
st.markdown("**Professional SEO Analysis with AI Recommendations**")

url = st.text_input("Enter Website URL", "https://example.com")

if st.button("🚀 Analyze Now", type="primary"):
    with st.spinner("Auditing your website... This may take 1-2 minutes."):
        try:
            result = analyze_single_url(url)
            
            # Display Score
            col1, col2, col3 = st.columns(3)
            col1.metric("Overall Score", f"{result.get('ai_recommendations', {}).get('overall_score', 'N/A')}/100")
            col2.metric("Mobile", f"{result.get('mobile_friendly', {}).get('score', 'N/A')}/100")
            col3.metric("Speed", f"{result.get('page_speed', {}).get('performance_score', 'N/A')}/100")
            
            # Show Recommendations
            st.subheader("🤖 AI Recommendations")
            for rec in result.get('ai_recommendations', {}).get('recommendations', []):
                priority = rec.get('priority', '')
                issue = rec.get('issue', '')
                fix = rec.get('fix', '')
                
                if 'HIGH' in priority:
                    st.error(f"**{priority}** - {issue}")
                elif 'MEDIUM' in priority:
                    st.warning(f"**{priority}** - {issue}")
                else:
                    st.info(f"**{priority}** - {issue}")
                
                st.markdown(f"*Fix: {fix}*")
            
            st.success("✅ Audit Complete!")
            
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            st.info("💡 Tip: Make sure the URL starts with http:// or https://")

st.sidebar.title("About")
st.sidebar.info("**Built by Mr Moosa Ai**\nDigital Artist & SEO Specialist")