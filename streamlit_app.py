import os
import sys
import streamlit as st

SCRIPT_DIR = os.path.join(os.path.dirname(__file__), ".agent", "skills", "custom-seo", "scripts")
if SCRIPT_DIR not in sys.path:
    sys.path.append(SCRIPT_DIR)

from seo_core import analyze_single_url

st.set_page_config(page_title="Seorax AI", layout="wide")
st.title("🚀 Seorax - AI SEO Auditor")
st.markdown("Apni website ka SEO check karein.")

url = st.text_input("Website URL:", placeholder="https://example.com")

if st.button("🔍 Analyze", type="primary"):
    if url and url.startswith("http"):
        with st.spinner("🤖 AI Analysis chal raha hai..."):
            try:
                result = analyze_single_url(url)
                st.success("✅ Audit Complete!")
                col1, col2 = st.columns(2)
                col1.metric("Overall Score", result.get("overall_score", "N/A"))
                col2.metric("Status", result.get("status", "N/A"))
                st.subheader("📊 Full Report")
                st.json(result)
            except Exception as e:
                st.error(f"Error: {str(e)}")
    else:
        st.warning("Please valid URL daalein (https://)")