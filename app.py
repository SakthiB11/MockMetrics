import streamlit as st
from datetime import datetime

from database import engine, Base, get_session
from models import Test, Subject
from styles import load_styles
from pages.dashboard import show_dashboard
from pages.add_test import show_add_test
from pages.add_subject import show_add_subject
from pages.analytics_hub import show_analytics
from pages.mock_analysis import show_mock_analysis
from pages.delete_test import show_delete_test
from pages.profile import show_profile
from pages.edit_test import show_edit_test

from config_manager import config_exists, load_config
from pages.setup_wizard import show_setup_wizard

# runs before anything else
if not config_exists():
    load_styles()
    show_setup_wizard()
    st.stop()

# load config for rest of app
if config_exists():
    config = load_config()
else:
    st.stop()

Base.metadata.create_all(engine)



#STREAMLIT CONFIG
st.set_page_config(
    page_title=f"{config['exam_name']} Ace Analytics",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("<style> [data-testid='stSidebarNav'] {display: none;} </style>", unsafe_allow_html=True)

#CSS
load_styles()

#HELPER FUNCTIONS
def calculate_days_to_exam():
    """Calculate days remaining to NIMCET (typically in June)"""
    exam_date = datetime.strptime(config["exam_date"], "%Y-%m-%d")
    return(exam_date - datetime.now()).days


def predict_rank(percentile,total_candidates = None):
    """Estimatingg AIR based on percentile (log based  approximation)"""
    if total_candidates is None:
        total_candidates = config["total_candidates"]
    if percentile <= 0:
        return total_candidates
    elif percentile >= 100:
        return 1
    rank = total_candidates * (1 - percentile /100)
    return max(1,int(rank))

#SIDEBAR
with st.sidebar:
    st.markdown(f"<div style='text-align: center; padding: 16px;'><h2 style='margin:0; color: #667eea;'>🎯 {config['exam_name']} Ace</h2><p style='color: #a0aec0; font-size: 12px; margin-top: 6px;'>Your path to {config['target_institution']}</p></div>", unsafe_allow_html=True)
    
    days_left = calculate_days_to_exam()
    if days_left > 0:
        st.info(f"⏰ **{days_left} days** until {config['exam_name']}")
    
    st.markdown("---")
    menu = st.radio("📂 Navigation", [
    "🏠 Dashboard",
    "➕ Add Test",
    "📚 Add Subject",
    "✏️ Edit Test",
    "🔍 Mock Analysis",
    "📊 Analytics Hub",
    "❌ Delete Test",
    "👤 Profile"        
])

    st.markdown("---")
    st.markdown("<p style='font-size: 11px; color: #718096; text-align: center;'>Track • Analyze • Excel</p>", unsafe_allow_html=True)
    

#ADD TEST
if menu == "➕ Add Test":
    show_add_test( predict_rank)
#ADD SUBJECT
elif menu == "📚 Add Subject":
    show_add_subject()

elif menu == "✏️ Edit Test":
    show_edit_test(predict_rank)

    
#DASHBOARD
elif menu == "🏠 Dashboard":
    show_dashboard(predict_rank)
#ANALYTICS HUB
elif menu == "📊 Analytics Hub":
    show_analytics()
    
#MOCK ANALYSIS
elif menu == "🔍 Mock Analysis":
    show_mock_analysis()

#DELETE A TEST
elif menu == "❌ Delete Test":
    show_delete_test()

elif menu == "👤 Profile":
    show_profile()
#FOOTER
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown(f"""
<div style='text-align: center; padding: 20px; color: #718096; font-size: 12px; border-top: 1px solid #2d3748;'>
    <p style='margin: 0;'>🎯 <b>{config['exam_name']} Tracker</b> | Tracking your journey to {config['target_institution']}</p>
    <p style='margin: 6px 0 0 0;'>Stay consistent. Analyze deeply. Excel remarkably.</p>
</div>
""", unsafe_allow_html=True)
