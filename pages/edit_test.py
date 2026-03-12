import streamlit as st
from datetime import datetime
from config_manager import load_config
from database import get_session
from models import Test, Subject


def show_edit_test(predict_rank):
    session = get_session()
    config = load_config()

    st.markdown("""
        <div class='app-header'>
            <div class='app-title'>✏️ Edit Test</div>
            <div class='app-subtitle'>Update your test details and subject scores</div>
        </div>
    """, unsafe_allow_html=True)

    tests = session.query(Test).all()
    if not tests:
        st.warning("⚠️ No tests found. Add a test first!")
        return

    # ── TEST SELECTOR ─────────────────────────────────────────────
    test_options = [f"{t.id} - {t.name} ({t.date})" for t in tests]
    selected = st.selectbox("🔍 Select Test to Edit", test_options)
    selected_test_id = int(selected.split(" - ")[0])

    test = session.query(Test).get(selected_test_id)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── EDIT TEST FORM ────────────────────────────────────────────
    st.markdown("#### 📝 Test Details")
    with st.form("edit_test_form"):
        col1, col2 = st.columns(2)

        with col1:
            name = st.text_input("📝 Test Name", value=test.name)
            date_val = st.date_input("📅 Test Date", value=test.date)
            score = st.number_input("📊 Your Score", min_value=0.0, step=0.5, value=float(test.score))
            total_marks = st.number_input("📈 Total Marks", min_value=1, value=int(test.total_marks))

        with col2:
            accuracy = st.number_input("🎯 Accuracy (%)", min_value=0.0, max_value=100.0, step=0.1, value=float(test.accuracy))
            rank = st.number_input("🏆 Your Rank", min_value=1, value=int(test.rank))
            total_participants = st.number_input("👥 Total Participants", min_value=1, value=int(test.total_participants))

        # recalculate percentile preview
        percentile = 100 * (1 - (rank - 1) / total_participants) if total_participants > 0 else 0
        predicted_air = predict_rank(percentile, config["total_candidates"])

        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.metric("Recalculated Percentile", f"{percentile:.2f}")
        with col_b:
            st.metric("Predicted AIR", f"~{predicted_air}")
        with col_c:
            delta = config["target_rank"] - predicted_air
            st.metric("Gap to Target", f"{abs(delta)}", delta=f"{'✅' if delta >= 0 else '⚠️'}")

        save_test = st.form_submit_button("💾 Save Test Changes", use_container_width=True)

        if save_test:
            test.name = name
            test.date = date_val
            test.score = score
            test.total_marks = total_marks
            test.accuracy = accuracy
            test.rank = rank
            test.total_participants = total_participants
            test.percentile = percentile
            session.commit()
            st.success(f"✅ Test '{name}' updated successfully!")
            st.rerun()

    # ── EDIT SUBJECTS ─────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### 📚 Subject Scores")

    subjects = session.query(Subject).filter(Subject.test_id == selected_test_id).all()

    if not subjects:
        st.info("📭 No subject scores recorded for this test.")
    else:
        for subject in subjects:
            with st.expander(f"📖 {subject.name}"):
                with st.form(f"edit_subject_form_{subject.id}"):
                    sub_name = st.text_input(
                        "📖 Subject Name",
                        value=subject.name,
                        key=f"name_{subject.id}"
                    )

                    col1, col2 = st.columns(2)

                    with col1:
                        sub_score = st.number_input(
                            "📊 Score", min_value=0.0, step=0.5,
                            value=float(subject.score),
                            key=f"score_{subject.id}"
                        )
                        sub_total = st.number_input(
                            "📈 Total Marks", min_value=1,
                            value=int(subject.total_marks),
                            key=f"total_{subject.id}"
                        )

                    with col2:
                        sub_accuracy = st.number_input(
                            "🎯 Accuracy (%)", min_value=0.0, max_value=100.0, step=0.1,
                            value=float(subject.accuracy),
                            key=f"acc_{subject.id}"
                        )

                    save_sub = st.form_submit_button(f"💾 Save {subject.name}", use_container_width=True)

                    if save_sub:
                        subject.name = sub_name
                        subject.score = sub_score
                        subject.total_marks = sub_total
                        subject.accuracy = sub_accuracy
                        subject.percentage = (sub_score / sub_total) * 100 if sub_total else 0
                        session.commit()
                        st.success(f"✅ {sub_name} updated!")
                        st.rerun()
