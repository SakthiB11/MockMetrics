import streamlit as st
import pandas as pd
import numpy as np
from config_manager import load_config, get_target_percentile

from datetime import datetime, timedelta

import plotly.express as px
import plotly.graph_objects as go


from database import get_session, engine
from models import Test, Subject


def show_analytics():
    session = get_session()
    config = load_config()
    st.markdown(f"<div class='app-header'><div class='app-title'>📊 Analytics Hub</div><div class='app-subtitle'>Deep insights to guide your study strategy</div></div>", unsafe_allow_html=True)

    TARGET_AIR = config["target_rank"]
    TARGET_PERCENTILE = (1 - TARGET_AIR / config["total_candidates"]) * 100

    tests = session.query(Test).all()
    if not tests:
        st.warning("⚠️ No test data available yet.")
    else:
        df = pd.read_sql(session.query(Test).statement, engine)
        df["date"] = pd.to_datetime(df["date"])
        
        try:
            subj_df = pd.read_sql(session.query(Subject).statement, engine)
        except:
            subj_df = pd.DataFrame()
        
        tabs = st.tabs(["🎯 Performance Insights", "📚 Subject Analysis", "🔮 Predictions", "📋 Detailed Stats", "💾 Export Data"])
        
        # TAB 1: Performance Insights (PERCENTILE-FOCUSED)
        with tabs[0]:
            st.subheader("🎯 Key Performance Insights")
            
            df_sorted = df.sort_values("date")
            
            # Recent vs Old Performance
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 📊 Recent Performance (Last 5 Tests)")
                recent_5 = df_sorted.tail(5)
                
                metrics_recent = {
                    "Avg Percentile": f"{recent_5['percentile'].mean():.2f}%",
                    "Best Percentile": f"{recent_5['percentile'].max():.2f}%",
                    "Latest Percentile": f"{recent_5.iloc[-1]['percentile']:.2f}%",
                    "Avg Accuracy": f"{recent_5['accuracy'].mean():.1f}%"
                }
                
                for label, value in metrics_recent.items():
                    st.markdown(f"""
                    <div class='insight-card'>
                        <div class='insight-title'>{label}</div>
                        <div class='insight-text' style='font-size: 18px; font-weight: 700; color: #667eea;'>{value}</div>
                    </div>
                    """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("#### 🔄 Overall Performance")
                
                metrics_overall = {
                    "Total Tests": f"{len(df)}",
                    "Overall Avg Percentile": f"{df['percentile'].mean():.2f}%",
                    "Best Ever Percentile": f"{df['percentile'].max():.2f}%",
                    "Percentile Range": f"{df['percentile'].min():.2f}% - {df['percentile'].max():.2f}%"
                }
                
                for label, value in metrics_overall.items():
                    st.markdown(f"""
                    <div class='insight-card' style='border-left-color: #764ba2;'>
                        <div class='insight-title'>{label}</div>
                        <div class='insight-text' style='font-size: 18px; font-weight: 700; color: #764ba2;'>{value}</div>
                    </div>
                    """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Improvement Analysis (PERCENTILE-BASED)
            st.markdown("#### 📈 Improvement Analysis")
            
            if len(df) >= 2:
                df_sorted['percentile_change'] = df_sorted['percentile'].diff()
                best_improvement = df_sorted.loc[df_sorted['percentile_change'].idxmax()] if df_sorted['percentile_change'].notna().any() else None
                
                col_imp1, col_imp2 = st.columns(2)
                
                with col_imp1:
                    if best_improvement is not None and pd.notna(best_improvement['percentile_change']):
                        st.markdown(f"""
                        <div class='insight-card' style='background: linear-gradient(135deg, #48bb78, #38a169);'>
                            <div class='insight-title' style='color: white;'>🚀 Biggest Percentile Jump</div>
                            <div class='insight-text' style='color: white; font-weight: 600;'>
                                {best_improvement['name']}<br>
                                +{best_improvement['percentile_change']:.2f}% improvement!
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                
                with col_imp2:
                    # Consistency Score (PERCENTILE-BASED)
                    std_dev = df['percentile'].std()
                    consistency_pct = max(0, 100 - (std_dev * 2))  # Adjusted formula for percentile
                    st.markdown(f"""
                    <div class='insight-card' style='background: linear-gradient(135deg, #4299e1, #3182ce);'>
                        <div class='insight-title' style='color: white;'>🎯 Consistency Score</div>
                        <div class='insight-text' style='color: white; font-weight: 600;'>
                            {consistency_pct:.1f}%<br>
                            {'Excellent consistency!' if consistency_pct > 90 else 'Keep working on it!' if consistency_pct > 75 else 'Focus on steady performance'}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Performance Scatter (PERCENTILE vs ACCURACY)
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("#### 🔥 Performance Analysis")
            
            fig_scatter = go.Figure(data=go.Scatter(
                x=df_sorted['date'],
                y=df_sorted['accuracy'],
                mode='markers',
                marker=dict(
                    size=df_sorted['accuracy'] / 5,  # Size by accuracy
                    color=df_sorted['percentile'],
                    colorscale='Viridis',
                    showscale=True,
                    colorbar=dict(title="Percentile"),
                    line=dict(width=1, color='white')
                ),
                text=[f"{row['name']}<br>Percentile: {row['percentile']:.2f}%<br>Accuracy: {row['accuracy']:.1f}%" for _, row in df_sorted.iterrows()],
                hovertemplate='%{text}<extra></extra>'
            ))
            
            fig_scatter.update_layout(
                title="Test Performance (Size = Accuracy, Color = Percentile)",
                xaxis_title="Date",
                yaxis_title="Accuracy",
                template='plotly_dark',
                height=400,
                plot_bgcolor='#1a1f3a',
                paper_bgcolor='#1a1f3a'
            )
            
            st.plotly_chart(fig_scatter, use_container_width=True)
        
        # TAB 2: Subject Analysis (PERCENTILE-FOCUSED)
        with tabs[1]:
            if subj_df.empty:
                st.info("📚 Add subject-wise scores to see detailed subject analysis!")
            else:
                merged = subj_df.merge(df[["id", "name", "date"]], left_on="test_id", right_on="id", suffixes=("_subject", "_test"))
                
                st.subheader("📚 Subject Performance Breakdown")
                
                # Subject averages (PERCENTILE-BASED)
                subject_avg = merged.groupby('name_subject').agg({
                    'accuracy': 'mean',
                    'score': 'mean',
                    'percentage': 'mean',
                    'total_marks': 'first'
                }).reset_index()
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # CHANGED: Percentile bar chart
                    fig_subj_bar = px.bar(
                        subject_avg,
                        x='name_subject',
                        y='percentage',
                        color='percentage',
                        color_continuous_scale='RdYlGn',
                        title="Average Score by Subject"
                    )
                    fig_subj_bar.update_layout(template='plotly_dark', plot_bgcolor='#1a1f3a', paper_bgcolor='#1a1f3a')
                    st.plotly_chart(fig_subj_bar, use_container_width=True)
                
                with col2:
                    # Radar chart for latest test (PERCENTILE-BASED)
                    latest_test_id = df.sort_values('date', ascending=False).iloc[0]['id']
                    latest_subjects = merged[merged['test_id'] == latest_test_id]
                    
                    if not latest_subjects.empty:
                        fig_radar = go.Figure()
                        
                        categories = latest_subjects['name_subject'].tolist()
                        values = latest_subjects['percentage'].tolist()
                        
                        fig_radar.add_trace(go.Scatterpolar(
                            r=values + [values[0]],
                            theta=categories + [categories[0]],
                            fill='toself',
                            name='Score',
                            line=dict(color='#667eea', width=2)
                        ))
                        
                        fig_radar.update_layout(
                            polar=dict(
                                radialaxis=dict(visible=True, range=[0, 100]),
                                bgcolor='#1a1f3a'
                            ),
                            showlegend=False,
                            title="Latest Test Subject Score Profile",
                            template='plotly_dark',
                            paper_bgcolor='#1a1f3a'
                        )
                        
                        st.plotly_chart(fig_radar, use_container_width=True)
                
                
                # Subject Progress Over Time (PERCENTILE-BASED)
                st.markdown("<br>", unsafe_allow_html=True)
                st.subheader("📈 Subject-wise Percentage Progress")
                
                fig_subj_timeline = px.line(
                    merged.sort_values('date'),
                    x='date',
                    y='percentage',
                    color='name_subject',
                    markers=True,
                    title="Percentage Trends by Subject"
                )
                fig_subj_timeline.update_layout(
                    template='plotly_dark',
                    height=400,
                    plot_bgcolor='#1a1f3a',
                    paper_bgcolor='#1a1f3a',
                    hovermode='x unified'
                )
                st.plotly_chart(fig_subj_timeline, use_container_width=True)
        
        # TAB 3: Predictions (PERCENTILE-FOCUSED)
        with tabs[2]:
            st.subheader("🔮 Performance Predictions & Goal Tracking")
            
            df_sorted = df.sort_values("date")
            
            if len(df_sorted) >= 3:
                # Linear regression forecast (PERCENTILE-FOCUSED)
                recent_10 = df_sorted.tail(10)
                
                x_days = (recent_10['date'] - recent_10['date'].min()).dt.days.values
                y_percentiles = recent_10['percentile'].values
                
                # Percentile prediction
                percentile_coeffs = np.polyfit(x_days, y_percentiles, 1)
                
                # Future predictions
                days_ahead = 30  # Predict 30 days ahead
                future_days = np.arange(x_days[-1], x_days[-1] + days_ahead, 3)
                future_dates = [recent_10['date'].min() + timedelta(days=int(d)) for d in future_days]
                
                predicted_percentiles = percentile_coeffs[0] * future_days + percentile_coeffs[1]

                target_percentile = get_target_percentile()
                # Percentile prediction chart
                fig_pred_pct = go.Figure()
                
                fig_pred_pct.add_trace(go.Scatter(
                    x=recent_10['date'],
                    y=recent_10['percentile'],
                    mode='lines+markers',
                    name='Actual Percentile',
                    line=dict(color='#667eea', width=3)
                ))
                
                fig_pred_pct.add_trace(go.Scatter(
                    x=future_dates,
                    y=predicted_percentiles,
                    mode='lines+markers',
                    name='Predicted Percentile',
                    line=dict(color='#48bb78', dash='dash', width=2)
                ))
                
                # Add target line
                fig_pred_pct.add_trace(go.Scatter(
                    x=recent_10['date'].tolist() + future_dates,
                    y=[target_percentile] * (len(recent_10) + len(future_dates)),
                    mode='lines',
                    name='Target',
                    line=dict(color='#fc466b', dash='dot', width=2)
                ))
                
                fig_pred_pct.update_layout(
                    title="Percentile Forecast (Next 30 Days)",
                    template='plotly_dark',
                    height=500,
                    plot_bgcolor='#1a1f3a',
                    paper_bgcolor='#1a1f3a',
                    yaxis_title="Percentile (%)"
                )
                
                st.plotly_chart(fig_pred_pct, use_container_width=True)
                
                # Goal Progress
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("#### 🎯 Goal Achievement Tracker")
                
                current_avg_percentile = recent_10.tail(3)['percentile'].mean()
                progress = min(100, (current_avg_percentile / target_percentile) * 100)
                
                col_goal1, col_goal2 = st.columns([2, 1])
                
                with col_goal1:
                    st.markdown(f"""
                    <div class='insight-card'>
                        <div class='insight-title'>Progress to Target: Rank {config['target_rank']} at {config['target_institution']}</div>
                        <div class='progress-container'>
                            <div class='progress-bar' style='width: {progress}%;'></div>
                        </div>
                        <div class='insight-text'>Current: {current_avg_percentile:.2f}%ile | Target: {target_percentile:.2f}%ile
                    </div>
                    """, unsafe_allow_html=True)
                
                with col_goal2:
                    # Estimated tests to goal
                    if percentile_coeffs[0] > 0:
                        tests_needed = max(0, (target_percentile - current_avg_percentile) / (percentile_coeffs[0] * 3))
                        st.markdown(f"""
                        <div class='metric-card' style='text-align: center;'>
                            <div class='metric-label'>Est. Tests to Goal</div>
                            <div class='metric-value' style='font-size: 36px;'>~{int(tests_needed)}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.warning("⚠️ Current trend is flat/declining. Revise strategy!")
                
                # Actionable Insights (PERCENTILE-BASED)
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("#### 💡 AI-Powered Insights")
                
                improvement_rate = percentile_coeffs[0]
                
                insights = []
                
                if improvement_rate > 0.5:
                    insights.append(("🚀 Excellent Trajectory", f"You're improving at {improvement_rate:.2f}%ile per test. Keep this momentum!"))
                elif improvement_rate > 0:
                    insights.append(("📈 Steady Growth", f"You're improving at {improvement_rate:.2f}%ile per test. Consider intensifying prep to accelerate."))
                else:
                    insights.append(("⚠️ Needs Attention", "Your percentile trend is flat or declining. Review your study strategy and identify weak areas."))
                
                if current_avg_percentile >= target_percentile:
                    insights.append(("🎯 Goal Achieved!", f"You're at {current_avg_percentile:.2f}%ile. Maintain this level!"))
                elif progress > 80:
                    insights.append(("🔥 Almost There!", f"You're {100-progress:.1f}% away from your target. Final push!"))
                else:
                    gap = target_percentile - current_avg_percentile
                    insights.append(("💪 Keep Pushing", f"Gap to target: {gap:.2f}%ile points. Stay consistent!"))
                
                for title, text in insights:
                    st.markdown(f"""
                    <div class='insight-card'>
                        <div class='insight-title'>{title}</div>
                        <div class='insight-text'>{text}</div>
                    </div>
                    """, unsafe_allow_html=True)
            
            else:
                st.info("📊 Add at least 3 tests to see predictions and forecasts!")
        
        # TAB 4: Detailed Stats (PERCENTILE-FOCUSED)
        with tabs[3]:
            st.subheader("📋 Comprehensive Statistics")
            
            df_sorted = df.sort_values("date", ascending=False)
            
            # Summary statistics (PERCENTILE-FOCUSED)
            st.markdown("#### 📊 Statistical Summary")
            
            summary_stats = {
                "Total Tests": len(df),
                "Mean Percentile": f"{df['percentile'].mean():.2f}%",
                "Median Percentile": f"{df['percentile'].median():.2f}%",
                "Std Deviation": f"{df['percentile'].std():.2f}%",
                "Min Percentile": f"{df['percentile'].min():.2f}%",
                "Max Percentile": f"{df['percentile'].max():.2f}%",
                "Percentile Range": f"{df['percentile'].max() - df['percentile'].min():.2f}%",
                "Coefficient of Variation": f"{(df['percentile'].std() / df['percentile'].mean() * 100):.2f}%"
            }
            
            col1, col2, col3, col4 = st.columns(4)
            for idx, (label, value) in enumerate(summary_stats.items()):
                with [col1, col2, col3, col4][idx % 4]:
                    st.metric(label, value)
            
            # Distribution plot (PERCENTILE-FOCUSED)
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("#### 📊 Percentile Distribution")
            
            fig_dist = go.Figure()
            
            fig_dist.add_trace(go.Histogram(
                x=df['percentile'],
                nbinsx=20,
                name='Percentile Distribution',
                marker=dict(color='#667eea', line=dict(color='white', width=1))
            ))
            
            fig_dist.update_layout(
                title="Percentile Frequency Distribution",
                xaxis_title="Percentile (%)",
                yaxis_title="Frequency",
                template='plotly_dark',
                height=400,
                plot_bgcolor='#1a1f3a',
                paper_bgcolor='#1a1f3a'
            )
            
            st.plotly_chart(fig_dist, use_container_width=True)
            
            # Detailed table
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("#### 📋 All Tests (Detailed View)")
            
            display_df = df_sorted[['name', 'date', 'percentile', 'rank', 'total_participants', 'score', 'total_marks', 'accuracy']].copy()
            display_df['date'] = display_df['date'].dt.strftime('%Y-%m-%d')
            display_df = display_df.rename(columns={
                'name': 'Test Name',
                'date': 'Date',
                'percentile': 'Percentile (%)',
                'rank': 'Rank',
                'total_participants': 'Total',
                'score': 'Score',
                'total_marks': 'Max Score',
                'accuracy': 'Accuracy (%)'
            })
            
            st.dataframe(display_df, use_container_width=True, hide_index=True)
        
        # TAB 5: Export
        with tabs[4]:
            st.subheader("💾 Export Your Data")
            
            st.markdown("""
            Download your performance data for external analysis, backup, or sharing with mentors.
            """)
            
            # Test data export
            csv_tests = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Test Data (CSV)",
                data=csv_tests,
                file_name=f"{config['exam_name']}_tests_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )
            
            # Subject data export
            if not subj_df.empty:
                csv_subjects = subj_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Download Subject Data (CSV)",
                    data=csv_subjects,
                    file_name=f"{config['exam_name']}_subjects_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            
            st.markdown("<br>", unsafe_allow_html=True)
            st.info("💡 **Tip**: Import this data into Excel or Google Sheets for custom analysis!")
