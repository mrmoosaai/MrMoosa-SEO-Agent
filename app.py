import streamlit as st
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

st.set_page_config(page_title="Mr Moosa SEO Agent", layout="wide")

st.title("🔍 Mr Moosa AI — Free SEO Audit Tool")
st.markdown("**Professional SEO Analysis with AI Recommendations**")

url = st.text_input("Enter Website URL", "https://example.com")

if st.button("🚀 Analyze Now", type="primary"):
    with st.spinner("Auditing your website... This may take 1-2 minutes."):
        try:
            from .agent.skills.custom-seo.scripts.seo_core import analyze_single_url
            
            result = analyze_single_url(url)
            
            # Display Score
            col1, col2, col3 = st.columns(3)
            overall = result.get('ai_recommendations', {}).get('overall_score', 'N/A')
            mobile = result.get('mobile_friendly', {}).get('score', 'N/A')
            speed = result.get('page_speed', {}).get('performance_score', 'N/A')
            
            col1.metric("Overall Score", f"{overall}/100")
            col2.metric("Mobile Friendly", f"{mobile}/100")
            col3.metric("Page Speed", f"{speed}/100")
            
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
st.sidebar.info("""
**Built by Mr Moosa Ai**

Digital Artist & Designer  
Creative AI Masterpieces

🔗 [Etsy Shop](https://mrmoosaai.etsy.com)
""")

st.sidebar.markdown("---")
st.sidebar.markdown("**Features:**")
st.sidebar.markdown("- ✅ Complete SEO Audit")
st.sidebar.markdown("- ✅ Mobile-Friendly Check")
st.sidebar.markdown("- ✅ Page Speed Analysis")
st.sidebar.markdown("- ✅ AI Recommendations")
st.sidebar.markdown("- ✅ Professional Reports")