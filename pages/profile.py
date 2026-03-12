import streamlit as st
from config_manager import load_config, save_config, reset_config

def show_profile():
    config = load_config()

    st.markdown("""
        <div class='app-header'>
            <div class='app-title'>👤 Profile</div>
            <div class='app-subtitle'>Update your exam details anytime</div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── SUMMARY CARD ─────────────────────────────────────────────
    from datetime import datetime
    exam_date = datetime.strptime(config["exam_date"], "%Y-%m-%d")
    days_left = (exam_date - datetime.now()).days

    st.markdown(f"""
    <div class='goal-banner'>
        <div class='goal-text'>📋 {config['exam_name']} | Target: Rank {config['target_rank']} | {config['target_institution']}</div>
        <div class='goal-subtext'>{'⏰ ' + str(days_left) + ' days to go' if days_left > 0 else '🎯 Exam day has passed'}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── EDIT FORM ─────────────────────────────────────────────────
    st.markdown("#### ✏️ Edit Details")

    with st.form("profile_form"):
        col1, col2 = st.columns(2)

        with col1:
            exam_name = st.text_input("Exam Name", value=config["exam_name"])
            target_rank = st.number_input("Target Rank", min_value=1, value=config["target_rank"])
            target_institution = st.text_input("Target Institution", value=config["target_institution"])
            exam_date_input = st.date_input(
                "Exam Date",
                value=datetime.strptime(config["exam_date"], "%Y-%m-%d").date()
            )

        with col2:
            total_candidates = st.number_input("Total Candidates", min_value=100, value=config["total_candidates"], step=100)
            total_marks = st.number_input("Total Marks", min_value=1, value=config["total_marks"])
            
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### 📚 Subjects")
        st.caption("Comma separated — changing this won't affect already recorded data")
        subjects_input = st.text_input(
            "Subjects",
            value=", ".join(config["subjects"])
        )

        st.markdown("<br>", unsafe_allow_html=True)
        save = st.form_submit_button("💾 Save Changes", use_container_width=True)

        if save:
            if not exam_name:
                st.error("❌ Exam name is required.")
            elif not subjects_input:
                st.error("❌ Please enter at least one subject.")
            elif not target_institution:
                st.error("❌ Target institution is required.")
            else:
                subjects = [s.strip() for s in subjects_input.split(",") if s.strip()]

                updated_config = {
                    "exam_name": exam_name,
                    "target_rank": int(target_rank),
                    "target_institution": target_institution,
                    "total_candidates": int(total_candidates),
                    "exam_date": str(exam_date_input),
                    "total_marks": int(total_marks),
                    "subjects": subjects
                }

                save_config(updated_config)
                st.success("✅ Profile updated successfully!")
                st.rerun()

    # ── DANGER ZONE ───────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### ⚠️ Danger Zone")

    with st.expander("🔴 Reset App Configuration"):
        st.warning("This will delete your config and show the setup wizard on next run. Your test data will NOT be deleted.")
        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button("🗑️ Reset Config", type="primary", use_container_width=True):
                reset_config()
                st.success("Config reset. Restarting...")
                st.rerun()
