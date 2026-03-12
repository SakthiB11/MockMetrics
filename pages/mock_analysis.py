import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from config_manager import load_config
from database import get_session

from models import Test, Question

def show_mock_analysis():
    session = get_session()

    st.markdown("""
        <div class='app-header'>
            <div class='app-title'>🔍 Mock Analysis</div>
            <div class='app-subtitle'>Question by question breakdown</div>
        </div>
    """, unsafe_allow_html=True)

    tabs = st.tabs(["➕ Add Questions", "📊 Analysis"])

    # ── TAB 1: ADD QUESTIONS ──────────────────────────────────────
    with tabs[0]:
        tests = session.query(Test).all()
        if not tests:
            st.warning("⚠️ No tests found. Add a test first!")
            return

        test_options = [f"{t.id} - {t.name} ({t.date})" for t in tests]
        selected = st.selectbox("🔍 Select Test", test_options)
        selected_test_id = int(selected.split(" - ")[0])

        # get subjects for this test to populate dropdown
        selected_test = session.query(Test).get(selected_test_id)
        config = load_config()
        subject_names = [s.name for s in selected_test.subjects] if selected_test.subjects else config["subjects"]
        st.markdown("#### ➕ Add a Question Entry")

        with st.form("add_question_form", clear_on_submit=True):
            col1, col2 = st.columns(2)

            with col1:
                question_number = st.number_input("Question No.", min_value=1, step=1)
                subject = st.selectbox("Subject", subject_names)
                topic = st.text_input("Topic / Concept", placeholder="e.g. Calculus, Sorting Algorithms")

            with col2:
                difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"])
                status = st.selectbox("Status", ["Correct", "Wrong", "Skipped"])
                time_taken_sec = st.number_input("Time Taken (seconds)", min_value=0, step=5)
                marks_awarded = st.number_input("Marks Awarded", step=0.25)

            submit = st.form_submit_button("✨ Add Question", use_container_width=True)

            if submit:
                q = Question(
                    question_number=question_number,
                    subject=subject,
                    topic=topic,
                    difficulty=difficulty,
                    status=status,
                    time_taken_sec=time_taken_sec,
                    marks_awarded=marks_awarded,
                    test_id=selected_test_id
                )
                session.add(q)
                session.commit()
                st.success(f"✅ Question {question_number} added!")

    # ── TAB 2: ANALYSIS ──────────────────────────────────────────
    with tabs[1]:
        questions = session.query(Question).all()
        if not questions:
            st.info("📭 No question data yet. Add questions in the first tab!")
            return

        df = pd.DataFrame([{
            "test_id":          q.test_id,
            "question_number":  q.question_number,
            "subject":          q.subject,
            "topic":            q.topic,
            "difficulty":       q.difficulty,
            "status":           q.status,
            "time_taken_sec":   q.time_taken_sec,
            "marks_awarded":    q.marks_awarded,
        } for q in questions])

        # pull test names for display
        test_map = {t.id: t.name for t in session.query(Test).all()}
        df["test_name"] = df["test_id"].map(test_map)

        # ── FILTERS ──────────────────────────────────────────────
        st.markdown("#### 🔽 Filters")
        col1, col2, col3 = st.columns(3)

        with col1:
            test_filter = st.multiselect("Test", options=df["test_name"].unique().tolist(), default=df["test_name"].unique().tolist())
        with col2:
            subject_filter = st.multiselect("Subject", options=df["subject"].unique().tolist(), default=df["subject"].unique().tolist())
        with col3:
            difficulty_filter = st.multiselect("Difficulty", options=["Easy", "Medium", "Hard"], default=["Easy", "Medium", "Hard"])

        filtered = df[
            df["test_name"].isin(test_filter) &
            df["subject"].isin(subject_filter) &
            df["difficulty"].isin(difficulty_filter)
        ]

        if filtered.empty:
            st.warning("No data matches your filters.")
            return

        st.markdown("<br>", unsafe_allow_html=True)

        # ── KEY METRICS ──────────────────────────────────────────
        st.markdown("#### 📊 Key Metrics")
        col1, col2, col3, col4 = st.columns(4)

        total = len(filtered)
        correct = len(filtered[filtered["status"] == "Correct"])
        wrong = len(filtered[filtered["status"] == "Wrong"])
        skipped = len(filtered[filtered["status"] == "Skipped"])
        avg_time = filtered["time_taken_sec"].mean()

        with col1:
            st.markdown(f"""<div class='metric-card'>
                <div class='metric-label'>Accuracy</div>
                <div class='metric-value'>{(correct/total*100):.1f}%</div>
            </div>""", unsafe_allow_html=True)
        with col2:
            st.markdown(f"""<div class='metric-card'>
                <div class='metric-label'>Correct / Wrong / Skipped</div>
                <div class='metric-value' style='font-size:20px;'>{correct} / {wrong} / {skipped}</div>
            </div>""", unsafe_allow_html=True)
        with col3:
            st.markdown(f"""<div class='metric-card'>
                <div class='metric-label'>Avg Time / Question</div>
                <div class='metric-value'>{avg_time:.0f}s</div>
            </div>""", unsafe_allow_html=True)
        with col4:
            st.markdown(f"""<div class='metric-card'>
                <div class='metric-label'>Total Marks</div>
                <div class='metric-value'>{filtered['marks_awarded'].sum():.1f}</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ── CHARTS ───────────────────────────────────────────────
        col_left, col_right = st.columns(2)

        with col_left:
            st.markdown("#### 🎯 Status by Subject")
            status_subject = filtered.groupby(["subject", "status"]).size().reset_index(name="count")
            fig1 = go.Figure()
            for s, color in [("Correct", "#48bb78"), ("Wrong", "#f56565"), ("Skipped", "#ed8936")]:
                d = status_subject[status_subject["status"] == s]
                fig1.add_trace(go.Bar(x=d["subject"], y=d["count"], name=s, marker_color=color))
            fig1.update_layout(
                barmode="group", template="plotly_dark",
                plot_bgcolor="#1a1f3a", paper_bgcolor="#1a1f3a", height=350
            )
            st.plotly_chart(fig1, use_container_width=True)

        with col_right:
            st.markdown("#### ⏱️ Avg Time by Difficulty")
            time_diff = filtered.groupby("difficulty")["time_taken_sec"].mean().reset_index()
            fig2 = go.Figure(go.Bar(
                x=time_diff["difficulty"],
                y=time_diff["time_taken_sec"],
                marker_color=["#48bb78", "#ed8936", "#f56565"]
            ))
            fig2.update_layout(
                template="plotly_dark",
                plot_bgcolor="#1a1f3a", paper_bgcolor="#1a1f3a", height=350
            )
            st.plotly_chart(fig2, use_container_width=True)

        # ── WEAK TOPICS ──────────────────────────────────────────
        st.markdown("#### 🔴 Weak Topics (Most Wrong Answers)")
        weak = filtered[filtered["status"] == "Wrong"].groupby("topic").size().reset_index(name="wrong_count")
        weak = weak.sort_values("wrong_count", ascending=False).head(10)
        if not weak.empty:
            fig3 = go.Figure(go.Bar(
                x=weak["wrong_count"], y=weak["topic"],
                orientation="h", marker_color="#f56565"
            ))
            fig3.update_layout(
                template="plotly_dark",
                plot_bgcolor="#1a1f3a", paper_bgcolor="#1a1f3a", height=350
            )
            st.plotly_chart(fig3, use_container_width=True)
        else:
            st.success("🎉 No wrong answers in selected filters!")

        # ── SPEED vs ACCURACY ────────────────────────────────────
        st.markdown("#### ⚡ Speed vs Accuracy (by Topic)")
        topic_stats = filtered.groupby("topic").agg(
            accuracy=("status", lambda x: (x == "Correct").mean() * 100),
            avg_time=("time_taken_sec", "mean"),
            count=("status", "count")
        ).reset_index()

        fig4 = go.Figure(go.Scatter(
            x=topic_stats["avg_time"],
            y=topic_stats["accuracy"],
            mode="markers+text",
            text=topic_stats["topic"],
            textposition="top center",
            marker=dict(
                size=topic_stats["count"] * 3,
                color=topic_stats["accuracy"],
                colorscale="RdYlGn",
                showscale=True,
                colorbar=dict(title="Accuracy %")
            )
        ))
        fig4.update_layout(
            xaxis_title="Avg Time (sec)",
            yaxis_title="Accuracy (%)",
            template="plotly_dark",
            plot_bgcolor="#1a1f3a", paper_bgcolor="#1a1f3a", height=400
        )
        st.plotly_chart(fig4, use_container_width=True)

        # ── RAW TABLE ────────────────────────────────────────────
        st.markdown("#### 📋 Raw Question Data")
        st.dataframe(
            filtered[["test_name", "question_number", "subject", "topic", "difficulty", "status", "time_taken_sec", "marks_awarded"]].rename(columns={
                "test_name": "Test", "question_number": "Q No.",
                "subject": "Subject", "topic": "Topic",
                "difficulty": "Difficulty", "status": "Status",
                "time_taken_sec": "Time (s)", "marks_awarded": "Marks"
            }),
            use_container_width=True, hide_index=True
        )
