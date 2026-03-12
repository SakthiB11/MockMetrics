import streamlit as st
from datetime import datetime
from config_manager import load_config
from database import get_session
from models import Test


def show_add_test(predict_rank):
    session = get_session()
    config = load_config()
    st.markdown(f"<div class='app-header'><div class='app-title'>➕ Add New Test</div><div class='app-subtitle'>Record your performance and track progress</div></div>", unsafe_allow_html=True)
    
    with st.form("add_test_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("📝 Test Name", placeholder="e.g., Mock Test 15")
            date_str = st.date_input("📅 Test Date", value=datetime.now())
            score = st.number_input("📊 Your Score", min_value=0.0, step=0.5)
            total_marks = st.number_input("📈 Total Marks", min_value=1, value= config["total_marks"])
        
        with col2:
            accuracy = st.number_input("🎯 Accuracy (%)", min_value=0.0, max_value=100.0, step=0.1)
            rank = st.number_input("🏆 Your Rank", min_value=1, value=1)
            total_participants = st.number_input("👥 Total Participants", min_value=1, value=1000)
        
        percentile = 100 * (1 - (rank - 1) / total_participants) if total_participants > 0 else 0
        predicted_air = predict_rank(percentile,config["total_candidates"])
        
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.metric("Calculated Percentile", f"{percentile:.2f}")
        with col_b:
            st.metric("Predicted AIR", f"~{predicted_air}")
        with col_c:
            delta = config["target_rank"] - predicted_air
            st.metric("Gap to Target", f"{abs(delta)}", delta=f"{'✅' if delta >= 0 else '⚠️'}")
        
        submit = st.form_submit_button("✨ Add Test", use_container_width=True)
        
        if submit and name and score is not None:
            test = Test(
                name=name,
                date=date_str,
                score=score,
                total_marks=total_marks,
                accuracy=accuracy,
                rank=rank,
                total_participants=total_participants,
                percentile=percentile
            )
            session.add(test)
            session.commit()
            st.success(f"✅ Test '{name}' added successfully! Percentile: {percentile:.2f}% 🚀")
            st.balloons()
