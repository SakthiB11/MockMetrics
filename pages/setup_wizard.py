import streamlit as st
from config_manager import save_config

def show_setup_wizard():
    st.markdown("""
        <div class='app-header'>
            <div class='app-title'>⚙️ Welcome! Let's get you set up</div>
            <div class='app-subtitle'>This only takes a minute. You can change everything later in Profile.</div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    with st.form("setup_form"):
        st.markdown("#### 🎯 Exam Details")
        col1, col2 = st.columns(2)

        with col1:
            exam_name = st.text_input("Exam Name", placeholder="e.g. NIMCET, GATE, CAT")
            target_rank = st.number_input("Target Rank", min_value=1, value=100)
            target_institution = st.text_input("Target Institution", placeholder="e.g. NIT Trichy, IIT Bombay")
            exam_date = st.date_input("Exam Date")

        with col2:
            total_candidates = st.number_input("Total Candidates (approx)", min_value=100, value=50000, step=100)
            total_marks = st.number_input("Total Marks", min_value=1, value=600)
            
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### 📚 Subjects")
        st.caption("Enter your exam subjects separated by commas")
        subjects_input = st.text_input(
            "Subjects",
            placeholder="e.g. Mathematics, Analytical Ability, Computer Awareness"
        )

        st.markdown("<br>", unsafe_allow_html=True)
        submit = st.form_submit_button("🚀 Start Tracking", use_container_width=True)

        if submit:
            if not exam_name:
                st.error("❌ Exam name is required.")
            elif not subjects_input:
                st.error("❌ Please enter at least one subject.")
            elif not target_institution:
                st.error("❌ Target institution is required.")
            else:
                subjects = [s.strip() for s in subjects_input.split(",") if s.strip()]
                
                config = {
                    "exam_name": exam_name,
                    "target_rank": int(target_rank),
                    "target_institution": target_institution,
                    "total_candidates": int(total_candidates),
                    "exam_date": str(exam_date),
                    "total_marks": int(total_marks),
                    "subjects": subjects
                }

                save_config(config)
                st.success(f"✅ All set! Tracking your journey to {target_institution}.")
                st.rerun()
