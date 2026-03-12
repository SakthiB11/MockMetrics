import streamlit as st

def load_styles():

    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
        
        * {font-family: 'Inter', sans-serif;}
        
        :root {
            --bg-primary: #0a0e27;
            --bg-secondary: #111936;
            --bg-card: #1a1f3a;
            --border: #2d3748;
            --text-primary: #f7fafc;
            --text-secondary: #a0aec0;
            --accent-primary: #667eea;
            --accent-secondary: #764ba2;
            --success: #48bb78;
            --warning: #ed8936;
            --danger: #f56565;
            --info: #4299e1;
        }
        
        .main {
            background: linear-gradient(135deg, var(--bg-primary) 0%, #0f1429 100%);
            color: var(--text-primary);
        }
        
        /* Header */
        .app-header {
            background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
            padding: 24px 28px;
            border-radius: 16px;
            margin-bottom: 24px;
            box-shadow: 0 10px 40px rgba(102, 126, 234, 0.25);
        }
        
        .app-title {
            font-size: 32px;
            font-weight: 800;
            color: white;
            margin: 0;
            text-shadow: 0 2px 10px rgba(0,0,0,0.3);
        }
        
        .app-subtitle {
            font-size: 14px;
            color: rgba(255,255,255,0.85);
            margin-top: 6px;
        }
        
        /* Goal Banner */
        .goal-banner {
            background: linear-gradient(135deg, #fc466b, #3f5efb);
            padding: 20px 24px;
            border-radius: 12px;
            margin-bottom: 20px;
            text-align: center;
            box-shadow: 0 8px 32px rgba(252, 70, 107, 0.3);
        }
        
        .goal-text {
            font-size: 18px;
            font-weight: 700;
            color: white;
            margin: 0;
        }
        
        .goal-subtext {
            font-size: 13px;
            color: rgba(255,255,255,0.9);
            margin-top: 4px;
        }
        
        /* Metric Cards */
        .metric-card {
            background: linear-gradient(135deg, var(--bg-card), var(--bg-secondary));
            padding: 22px 20px;
            border-radius: 14px;
            border: 1px solid var(--border);
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
            transition: transform 0.2s, box-shadow 0.2s;
        }
        
        .metric-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 8px 30px rgba(102, 126, 234, 0.2);
        }
        
        .metric-value {
            font-size: 32px;
            font-weight: 800;
            background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .metric-label {
            font-size: 11px;
            color: var(--text-secondary);
            text-transform: uppercase;
            letter-spacing: 0.1em;
            font-weight: 600;
            margin-bottom: 8px;
        }
        
        .metric-delta {
            font-size: 13px;
            font-weight: 600;
            margin-top: 6px;
        }
        
        .delta-positive {color: var(--success);}
        .delta-negative {color: var(--danger);}
        
        /* Insights Cards */
        .insight-card {
            background: var(--bg-card);
            padding: 18px 20px;
            border-radius: 12px;
            border-left: 4px solid var(--accent-primary);
            margin-bottom: 14px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.2);
        }
        
        .insight-title {
            font-size: 14px;
            font-weight: 700;
            color: var(--accent-primary);
            margin-bottom: 6px;
        }
        
        .insight-text {
            font-size: 13px;
            color: var(--text-secondary);
            line-height: 1.6;
        }
        
        /* Study Recommendations */
        .study-card {
            background: linear-gradient(135deg, #1a1f3a, #252a48);
            padding: 16px 18px;
            border-radius: 10px;
            border: 1px solid var(--border);
            margin-bottom: 12px;
        }
        
        .study-subject {
            font-size: 15px;
            font-weight: 700;
            color: var(--text-primary);
            margin-bottom: 8px;
        }
        
        .study-advice {
            font-size: 13px;
            color: var(--text-secondary);
            line-height: 1.5;
            margin-left: 12px;
        }
        
        /* Progress Bar */
        .progress-container {
            background: var(--bg-secondary);
            border-radius: 10px;
            padding: 3px;
            margin-top: 10px;
        }
        
        .progress-bar {
            background: linear-gradient(90deg, var(--accent-primary), var(--accent-secondary));
            height: 8px;
            border-radius: 8px;
            transition: width 0.3s ease;
        }
        
        /* Buttons */
        .stButton>button {
            background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
            color: white;
            border: none;
            border-radius: 10px;
            font-weight: 600;
            padding: 10px 20px;
            transition: all 0.2s;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        }
        
        .stButton>button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
        }
        
        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            background-color: var(--bg-secondary);
            border-radius: 10px;
            padding: 6px;
        }
        
        .stTabs [data-baseweb="tab"] {
            border-radius: 8px;
            color: var(--text-secondary);
            font-weight: 600;
        }
        
        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
            color: white;
        }
        
        /* Sidebar */
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, var(--bg-secondary), var(--bg-primary));
            border-right: 1px solid var(--border);
        }
        
        /* Forms */
        .stTextInput>div>div>input, .stNumberInput>div>div>input, .stSelectbox>div>div>select {
            background-color: var(--bg-card);
            color: var(--text-primary);
            border: 1px solid var(--border);
            border-radius: 8px;
        }
        
        h1, h2, h3 {
            color: var(--text-primary);
        }
    </style>
    """, unsafe_allow_html=True)
