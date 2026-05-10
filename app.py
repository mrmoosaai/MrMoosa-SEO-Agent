import streamlit as st
import sys
import os
import importlib.util
from datetime import datetime

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Safely load module despite hyphen in folder name
module_path = os.path.join(os.path.dirname(__file__), ".agent", "skills", "custom-seo", "scripts", "seo_core.py")
if not os.path.isfile(module_path):
    raise FileNotFoundError(f"SEO core module not found: {module_path}")

spec = importlib.util.spec_from_file_location("seo_core", module_path)
if spec is None or spec.loader is None:
    raise ImportError(f"Cannot load seo_core module from path: {module_path}")

# Ensure the seo_core script folder is on the import path so internal imports like
# `from ai_insights import AIInsights` work correctly.
script_dir = os.path.dirname(module_path)
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

seo_core = importlib.util.module_from_spec(spec)
spec.loader.exec_module(seo_core)

# Assign function to a variable for easy use
analyze_single_url = seo_core.analyze_single_url
generate_pdf_report = seo_core.generate_pdf_report

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

            if result.get('error'):
                st.error(f"❌ Analysis failed: {result.get('error')}")
                st.info("💡 Tip: Make sure the URL starts with http:// or https://")
            else:
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

                # Generate PDF in memory and show download button
                pdf_bytes = None
                try:
                    pdf_bytes = generate_pdf_report(result)
                except Exception as e:
                    st.warning("⚠️ PDF report generation failed. Please check dependencies or retry.")
                    if hasattr(st, 'debug'):
                        st.debug(str(e))

                if pdf_bytes:
                    st.download_button(
                        label="📥 Download Professional PDF Report",
                        data=pdf_bytes,
                        file_name=f"MrMoosa_SEO_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                        mime="application/pdf",
                        key="pdf_report_download"
                    )
                else:
                    st.warning("⚠️ PDF report could not be generated. Make sure reportlab is installed and the app can create the file in memory.")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            st.info("💡 Tip: Make sure the URL starts with http:// or https://")

st.sidebar.title("About")
st.sidebar.info("**Built by Mr Moosa Ai**\nDigital Artist & SEO Specialist")