import streamlit as st
from config_manager import load_config
from database import get_session
from models import Test, Subject

def show_add_subject():
    session = get_session()
    config = load_config()

    st.markdown(f"<div class='app-header'><div class='app-title'>📚 Add Subject Score</div><div class='app-subtitle'>Break down performance by subject</div></div>", unsafe_allow_html=True)
    
    tests = session.query(Test).all()
    if not tests:
        st.warning("⚠️ No tests found. Add a test first!")
    else:
        test_names = [f"{t.id} - {t.name} ({t.date})" for t in tests]
        selected = st.selectbox("🔍 Select Test", test_names)
        selected_test_id = int(selected.split(" - ")[0])
        
        with st.form("add_subject_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                subject_options = config["subjects"] + ["Other"]
                name = st.selectbox("📖 Subject", subject_options)
                if name == "Other":
                    name = st.text_input("Custom Subject Name")
                score = st.number_input("📊 Score", min_value=0.0, step=0.5)
            
            with col2:
                total_marks = st.number_input("📈 Total Marks", min_value=1, value=200)
                accuracy = st.number_input("🎯 Accuracy (%)", min_value=0.0, max_value=100.0, step=0.1)            
            submit = st.form_submit_button("✨ Add Subject", use_container_width=True)
            
            if submit and name and score is not None:

                sub = Subject(
                    name=name,
                    score=score,
                    total_marks=total_marks,
                    accuracy=accuracy,
                    percentage=(score / total_marks) * 100 if total_marks else 0, 
                    test_id=selected_test_id
                )
                session.add(sub)
                session.commit()
                st.success(f"✅ Subject '{name}' added successfully!")
