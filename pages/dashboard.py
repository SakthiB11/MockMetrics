import streamlit as st
from config_manager import load_config, get_target_percentile
import pandas as pd
from database import get_session, engine
from models import Test
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def show_dashboard(predict_rank):
    session = get_session()
    config = load_config()
    
    st.markdown(f"<div class='app-header'><div class='app-title'>🏠 Performance Dashboard</div><div class='app-subtitle'>Your journey to {config['target_institution']} at a glance</div></div>", unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class='goal-banner'>
        <div class='goal-text'>🎯 TARGET: Rank {config['target_rank']} | {config['target_institution']}</div>
        <div class='goal-subtext'>Stay consistent. Every test brings you closer to your goal.</div>
    </div>
    """, unsafe_allow_html=True)
    
    tests = session.query(Test).all()
    if not tests:
        st.info("🌟 No data yet. Start by adding your first test to begin tracking!")
    else:
        df = pd.read_sql(session.query(Test).statement, engine)
        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values("date")
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            total_tests = len(df)
            st.markdown(f"""
            <div class='metric-card'>
                <div class='metric-label'>Total Tests</div>
                <div class='metric-value'>{total_tests}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            avg_percentile = df['percentile'].mean()
            recent_avg = df.tail(3)['percentile'].mean() if len(df) >= 3 else avg_percentile
            delta = recent_avg - df.head(3)['percentile'].mean() if len(df) >= 6 else 0
            delta_class = "delta-positive" if delta > 0 else "delta-negative"
            st.markdown(f"""
            <div class='metric-card'>
                <div class='metric-label'>Avg Percentile</div>
                <div class='metric-value'>{avg_percentile:.2f}%</div>
                <div class='metric-delta {delta_class}'>{'↑' if delta > 0 else '↓'} {abs(delta):.2f}%</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            latest_percentile = df.iloc[-1]['percentile']
            st.markdown(f"""
            <div class='metric-card'>
                <div class='metric-label'>Latest Percentile</div>
                <div class='metric-value'>{latest_percentile:.2f}%</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            best_percentile = df['percentile'].max()
            delta_from_best = latest_percentile - best_percentile
            delta_class_best = "delta-positive" if delta_from_best >= 0 else "delta-negative"
            st.markdown(f"""
            <div class='metric-card'>
                <div class='metric-label'>Best Percentile</div>
                <div class='metric-value'>{best_percentile:.2f}%</div>
                <div class='metric-delta {delta_class_best}'>{'✅ Current!' if delta_from_best >= 0 else f'Gap: {abs(delta_from_best):.2f}%'}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col5:
            predicted_rank = predict_rank(avg_percentile, config["total_candidates"])
            target_gap = config["target_rank"] - predicted_rank
            gap_text = f"✅ {abs(target_gap)} ahead!" if target_gap >= 0 else f"⚠️ {abs(target_gap)} to go"
            st.markdown(f"""
            <div class='metric-card'>
                <div class='metric-label'>Predicted Rank</div>
                <div class='metric-value'>~{predicted_rank}</div>
                <div class='metric-delta'>{gap_text}</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        df_sorted = df.sort_values("date")
        date_diffs = df_sorted["date"].diff().dt.days
        current_streak = 0
        for diff in reversed(date_diffs.dropna().tolist()):
            if diff <= 7:
                current_streak += 1
            else:
                break
        
        col_a, col_b = st.columns([2, 1])
        
        with col_a:
            st.subheader("📈 Percentile Progress Over Time")
            fig = make_subplots(
                rows=2, cols=1,
                subplot_titles=("Percentile Trend with Rolling Average", "Performance Consistency"),
                vertical_spacing=0.12,
                row_heights=[0.6, 0.4]
            )
            
            rolling_avg = df['percentile'].rolling(window=3, min_periods=1).mean()
            fig.add_trace(
                go.Scatter(x=df['date'], y=df['percentile'], mode='lines+markers',
                          name='Percentile', line=dict(color='#667eea', width=3),
                          marker=dict(size=8)),
                row=1, col=1
            )
            fig.add_trace(
                go.Scatter(x=df['date'], y=rolling_avg, mode='lines',
                          name='Rolling Avg (3)', line=dict(color='#48bb78', dash='dash', width=2)),
                row=1, col=1
            )
            fig.add_trace(
                go.Scatter(x=df['date'], y=[get_target_percentile()]*len(df), mode='lines',
                          name='Target', line=dict(color='#fc466b', dash='dot', width=2)),
                row=1, col=1
            )
            fig.add_trace(
                go.Scatter(x=df['date'], y=df['accuracy'], mode='lines+markers',
                          name='Accuracy', fill='tozeroy',
                          line=dict(color='#764ba2', width=2),
                          marker=dict(size=6)),
                row=2, col=1
            )
            
            fig.update_layout(
                height=600,
                showlegend=True,
                template='plotly_dark',
                hovermode='x unified',
                plot_bgcolor='#1a1f3a',
                paper_bgcolor='#1a1f3a'
            )
            fig.update_xaxes(showgrid=True, gridcolor='#2d3748')
            fig.update_yaxes(showgrid=True, gridcolor='#2d3748')
            fig.update_yaxes(title_text="Percentile", row=1, col=1)
            fig.update_yaxes(title_text="Accuracy (%)", row=2, col=1)
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col_b:
            st.subheader("🔥 Study Streak")
            st.markdown(f"""
            <div class='metric-card' style='text-align: center; padding: 30px 20px;'>
                <div style='font-size: 48px; margin-bottom: 10px;'>🔥</div>
                <div class='metric-value' style='font-size: 40px;'>{current_streak}</div>
                <div class='metric-label'>Test{'s' if current_streak != 1 else ''} in a Row</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.subheader("🎯 Quick Stats")
            best_test = df.loc[df['percentile'].idxmax()]
            worst_test = df.loc[df['percentile'].idxmin()]
            
            st.markdown(f"""
            <div class='study-card'>
                <div class='study-subject'>🏆 Best Performance</div>
                <div class='study-advice'>{best_test['name']}<br>Percentile: {best_test['percentile']:.2f}%</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class='study-card'>
                <div class='study-subject'>📉 Needs Improvement</div>
                <div class='study-advice'>{worst_test['name']}<br>Percentile: {worst_test['percentile']:.2f}%</div>
            </div>
            """, unsafe_allow_html=True)
            
            consistency = df['percentile'].std()
            st.markdown(f"""
            <div class='study-card'>
                <div class='study-subject'>📊 Consistency</div>
                <div class='study-advice'>Std Dev: {consistency:.2f}%<br>{'Excellent!' if consistency < 2 else 'Keep improving!' if consistency < 5 else 'Focus on consistency!'}</div>
            </div>
            """, unsafe_allow_html=True)
