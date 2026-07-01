import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import time
import json
import rank
import os

# ==========================================
# PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="Talent Intelligence Command Center",
    page_icon="👁️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# CUSTOM CSS (Glassmorphism & Cyber-Minimalist)
# ==========================================
def inject_custom_css():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
        @import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;600;700&display=swap');
        
        /* Global Font and Background */
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }
        
        /* App Background */
        .stApp {
            background-color: #0B0F19;
            background-image: radial-gradient(circle at 50% 0%, #151f32 0%, #0B0F19 70%);
            color: #E2E8F0;
        }
        
        /* Hide Default Streamlit UI */
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}
        
        /* Sidebar Styling */
        [data-testid="stSidebar"] {
            background: rgba(11, 15, 25, 0.85) !important;
            border-right: 1px solid rgba(138, 43, 226, 0.3) !important;
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            box-shadow: 2px 0 15px rgba(138, 43, 226, 0.1);
        }
        
        [data-testid="stSidebar"] * {
            color: #E2E8F0 !important;
        }
        
        /* Neon Accents for Sliders */
        .stSlider [data-testid="stTickBar"] {
            background: rgba(0, 240, 255, 0.2) !important;
        }
        .stSlider div[data-testid="thumbValue"] {
            color: #00F0FF !important;
        }
        div[data-baseweb="slider"] > div > div > div {
            background-color: #8A2BE2 !important;
        }
        
        /* Glassmorphism Metric Card */
        .metric-card {
            background: rgba(255, 255, 255, 0.02);
            border: 1px solid rgba(0, 240, 255, 0.15);
            border-radius: 12px;
            padding: 24px 20px;
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            box-shadow: 0 4px 30px rgba(0, 0, 0, 0.5), inset 0 0 10px rgba(0, 240, 255, 0.05);
            text-align: center;
            transition: transform 0.3s ease, box-shadow 0.3s ease, border 0.3s ease;
            height: 100%;
            position: relative;
            overflow: hidden;
        }
        /* Scanning line animation */
        .metric-card::after {
            content: '';
            position: absolute;
            top: 0; left: -100%;
            width: 50%; height: 100%;
            background: linear-gradient(to right, rgba(255,255,255,0) 0%, rgba(0,240,255,0.1) 50%, rgba(255,255,255,0) 100%);
            transform: skewX(-20deg);
            animation: scan 4s infinite;
        }
        @keyframes scan {
            0% { left: -100%; }
            50% { left: 200%; }
            100% { left: 200%; }
        }
        
        .metric-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 8px 30px rgba(0, 0, 0, 0.7), inset 0 0 20px rgba(0, 240, 255, 0.2);
            border: 1px solid rgba(0, 240, 255, 0.6);
        }
        .metric-title {
            font-size: 0.85rem;
            color: #94A3B8;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            margin-bottom: 12px;
            font-weight: 600;
        }
        .metric-value {
            font-size: 2.5rem;
            font-weight: 700;
            font-family: 'Fira Code', monospace;
            background: -webkit-linear-gradient(45deg, #00F0FF, #8A2BE2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-shadow: 0px 0px 20px rgba(0, 240, 255, 0.3);
        }
        
        .value-green {
            background: none !important;
            color: #00FF00 !important;
            -webkit-text-fill-color: #00FF00 !important;
            text-shadow: 0px 0px 20px rgba(0, 255, 0, 0.4) !important;
        }
        .value-dim {
            background: none !important;
            color: #94A3B8 !important;
            -webkit-text-fill-color: #94A3B8 !important;
        }

        /* Candidate Dossier Card */
        .dossier-card {
            background: rgba(15, 23, 42, 0.7);
            border-left: 4px solid #00F0FF;
            border-radius: 8px;
            padding: 24px;
            margin-bottom: 15px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
            transition: all 0.3s ease;
            border-top: 1px solid rgba(255,255,255,0.05);
            border-right: 1px solid rgba(255,255,255,0.05);
            border-bottom: 1px solid rgba(255,255,255,0.05);
        }
        .dossier-card:hover {
            background: rgba(30, 41, 59, 0.9);
            border-left: 4px solid #8A2BE2;
            box-shadow: 0 8px 30px rgba(138, 43, 226, 0.3);
            transform: scale(1.01);
        }
        .candidate-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            padding-bottom: 12px;
            margin-bottom: 18px;
        }
        .candidate-name {
            font-size: 1.6rem;
            font-weight: 700;
            color: #F8FAFC;
            text-shadow: 0 0 10px rgba(255, 255, 255, 0.1);
        }
        .candidate-id {
            font-family: 'Fira Code', monospace;
            font-size: 0.85rem;
            color: #00F0FF;
            background: rgba(0, 240, 255, 0.1);
            padding: 6px 10px;
            border-radius: 4px;
            border: 1px solid rgba(0, 240, 255, 0.3);
            letter-spacing: 1px;
            box-shadow: 0 0 10px rgba(0, 240, 255, 0.2);
        }
        
        /* AI Verdict Blockquote */
        .ai-verdict {
            border-left: 3px solid #8A2BE2;
            background: linear-gradient(90deg, rgba(138, 43, 226, 0.15) 0%, rgba(138, 43, 226, 0.02) 100%);
            padding: 16px 20px;
            border-radius: 0 8px 8px 0;
            font-style: italic;
            color: #E2E8F0;
            font-size: 1rem;
            line-height: 1.6;
            margin: 15px 0;
        }
        
        .ai-verdict-label {
            font-family: 'Fira Code', monospace;
            color: #8A2BE2;
            font-weight: 700;
            font-size: 0.8rem;
            letter-spacing: 1.5px;
            text-transform: uppercase;
            margin-bottom: 8px;
            font-style: normal;
        }

        /* Trigger Button Styling */
        .stButton > button {
            background: linear-gradient(90deg, #00F0FF 0%, #8A2BE2 100%) !important;
            color: #FFF !important;
            font-weight: 700 !important;
            border: none !important;
            border-radius: 6px !important;
            padding: 12px 24px !important;
            text-transform: uppercase !important;
            letter-spacing: 1.5px !important;
            box-shadow: 0 0 15px rgba(0, 240, 255, 0.4) !important;
            transition: all 0.3s ease !important;
            width: 100% !important;
        }
        .stButton > button:hover {
            box-shadow: 0 0 25px rgba(138, 43, 226, 0.8) !important;
            transform: translateY(-2px) !important;
        }
        .stButton > button:active {
            transform: translateY(1px) !important;
        }
        
        /* Secondary Download Buttons */
        [data-testid="stDownloadButton"] > button {
            background: rgba(255, 255, 255, 0.05) !important;
            border: 1px solid rgba(0, 240, 255, 0.4) !important;
            color: #00F0FF !important;
            box-shadow: none !important;
        }
        [data-testid="stDownloadButton"] > button:hover {
            background: rgba(0, 240, 255, 0.1) !important;
            border: 1px solid rgba(0, 240, 255, 0.8) !important;
            box-shadow: 0 0 15px rgba(0, 240, 255, 0.3) !important;
        }

        /* Expanders */
        .streamlit-expanderHeader {
            background-color: rgba(255, 255, 255, 0.03) !important;
            border-radius: 6px !important;
            border: 1px solid rgba(255,255,255,0.1) !important;
            transition: all 0.3s;
        }
        .streamlit-expanderHeader:hover {
            background-color: rgba(255, 255, 255, 0.05) !important;
            border: 1px solid rgba(0, 240, 255, 0.3) !important;
        }
        .streamlit-expanderHeader p {
            color: #00F0FF !important;
            font-weight: 600 !important;
            letter-spacing: 0.5px !important;
        }
        .streamlit-expanderContent {
            background-color: rgba(0, 0, 0, 0.3) !important;
            border: 1px solid rgba(255,255,255,0.05) !important;
            border-top: none !important;
            border-radius: 0 0 6px 6px !important;
        }
        
        /* Toggle */
        [data-testid="stCheckbox"] span {
            color: #E2E8F0 !important;
        }
        
        /* Progress Bar Override */
        .stProgress > div > div > div {
            background-color: #00F0FF !important;
            box-shadow: 0 0 10px #00F0FF !important;
        }
        
        /* Terminal Text Animation */
        .terminal-text {
            font-family: 'Fira Code', monospace;
            color: #00F0FF;
            font-size: 1rem;
            margin: 5px 0;
            text-align: left;
        }
        .terminal-container {
            background: #000;
            border: 1px solid rgba(0, 240, 255, 0.3);
            border-radius: 8px;
            padding: 20px;
            box-shadow: inset 0 0 20px rgba(0, 240, 255, 0.1);
        }
        </style>
        """,
        unsafe_allow_html=True
    )

# ==========================================
# PROCESSING BACKEND DATA
# ==========================================
def process_real_candidates(df):
    candidates = []
    for _, row in df.iterrows():
        # Extrapolate skills for radar chart
        skills_dict = {"Backend": 0, "Frontend": 0, "ML": 0, "DevOps": 0}
        skills_list = row.get('skills_list', [])
        
        # Simple heuristic mapping for dynamic radar charts
        skills_str = " ".join(skills_list).lower()
        if "python" in skills_str or "java" in skills_str or "backend" in skills_str or "c++" in skills_str: 
            skills_dict["Backend"] = 80 + np.random.randint(0, 20)
        if "react" in skills_str or "html" in skills_str or "frontend" in skills_str: 
            skills_dict["Frontend"] = 70 + np.random.randint(0, 20)
        if "ml" in skills_str or "pinecone" in skills_str or "machine" in skills_str or "data" in skills_str: 
            skills_dict["ML"] = 80 + np.random.randint(0, 20)
        if "devops" in skills_str or "kubernetes" in skills_str or "aws" in skills_str: 
            skills_dict["DevOps"] = 75 + np.random.randint(0, 20)
        
        # Default fallback if skills are empty
        for k, v in skills_dict.items():
            if v == 0: skills_dict[k] = 50 + np.random.randint(0, 30)

        # Behavioral stats
        beh = {
            "Response Rate": int(row.get('recruiter_response_rate', 0.5) * 100),
            "Commit Freq": int(row.get('activity_multiplier', 1) * 80), 
            "Peer Reviews": 85
        }
        
        history_list = row.get('career_history', [])
        if isinstance(history_list, list) and history_list:
            history_str = "\n".join([f"{job.get('title', '')} @ {job.get('company', '')}" for job in history_list])
        else:
            history_str = "No specific history provided."
            
        raw_signals = row.get('raw_signals', {})
        signal_str = f"Last active: {raw_signals.get('last_active_date', 'Unknown')}. Notice period: {raw_signals.get('notice_period_days', 'N/A')} days."

        # Convert timestamp to string if present to avoid JSON errors
        safe_dict = json.loads(row.to_json())

        candidates.append({
            "id": row.get('candidate_id', 'UNKNOWN'),
            "name": row.get('name', 'Anonymized Candidate'),
            "match_score": int(row.get('final_score', 0) * 100),
            "verdict": row.get('reasoning', ''),
            "skills": skills_dict,
            "behavioral": beh,
            "redrob_signals": signal_str,
            "history": history_str,
            "raw_data": safe_dict
        })
    return candidates

# ==========================================
# PLOTLY CHARTING FUNCTIONS
# ==========================================
def create_radar_chart(skills):
    categories = list(skills.keys())
    values = list(skills.values())
    categories.append(categories[0])
    values.append(values[0])
    
    fig = go.Figure(
        data=[
            go.Scatterpolar(
                r=values, theta=categories, fill='toself', fillcolor='rgba(0, 240, 255, 0.2)',
                line=dict(color='#00F0FF', width=2), marker=dict(color='#00F0FF', size=6, symbol='circle'), name='Candidate Profile'
            ),
            go.Scatterpolar(
                r=[90, 85, 80, 85, 90], theta=categories, fill='none',
                line=dict(color='rgba(138, 43, 226, 0.8)', width=2, dash='dash'), name='Ideal JD Profile'
            )
        ]
    )
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100], gridcolor='rgba(255, 255, 255, 0.15)', tickfont=dict(color='#64748B'), showline=False),
            angularaxis=dict(gridcolor='rgba(255, 255, 255, 0.15)', tickfont=dict(color='#E2E8F0', size=12, family='Inter')),
            bgcolor='rgba(0,0,0,0)'
        ),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', showlegend=False,
        margin=dict(l=40, r=40, t=30, b=30), height=260,
        title=dict(text="Technical Depth Matrix", font=dict(color="#94A3B8", size=13, family="Inter"), x=0.5, y=0.98)
    )
    return fig

def create_gauge_chart(score):
    color = "#00FF00" if score >= 90 else "#FFD700" if score >= 70 else "#FF4500"
    
    fig = go.Figure(go.Indicator(
        mode = "gauge+number", value = score, domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "AI Match Confidence", 'font': {'color': '#94A3B8', 'size': 13, 'family': 'Inter'}},
        number = {'font': {'color': color, 'size': 38, 'family': 'Fira Code'}, 'suffix': "%"},
        gauge = {
            'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "rgba(255,255,255,0.3)", 'tickfont': {'color': '#64748B'}},
            'bar': {'color': color, 'thickness': 0.25},
            'bgcolor': "rgba(255, 255, 255, 0.05)",
            'borderwidth': 0,
            'steps': [
                {'range': [0, 70], 'color': 'rgba(255, 69, 0, 0.15)'},
                {'range': [70, 90], 'color': 'rgba(255, 215, 0, 0.15)'},
                {'range': [90, 100], 'color': 'rgba(0, 255, 0, 0.15)'}
            ],
            'threshold': {'line': {'color': "rgba(255,255,255,0.8)", 'width': 2}, 'thickness': 0.75, 'value': 90}
        }
    ))
    
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=200, margin=dict(l=20, r=20, t=40, b=20))
    return fig

def simulate_terminal_boot(placeholder):
    lines = [
        "[+] ESTABLISHING SECURE UPLINK...",
        "[+] INGESTING CANDIDATE DATASET...",
        "[+] DEPLOYING TF-IDF VECTORIZATION...",
        "[+] APPLYING DETERMINISTIC GUARDRAILS...",
        "[+] COMPUTING BEHAVIORAL MULTIPLIERS...",
        "[+] RANKING MATRICES SECURED. OUTPUTTING TOP 1%."
    ]
    html_content = "<div class='terminal-container'>"
    for line in lines:
        html_content += f"<div class='terminal-text'>{line}</div>"
        placeholder.markdown(html_content + "</div>", unsafe_allow_html=True)
        time.sleep(0.3)
    time.sleep(0.5)
    placeholder.empty()

# ==========================================
# MAIN APP STRUCTURE
# ==========================================
def main():
    inject_custom_css()
    
    # ----------------------------------------
    # A. The Control Panel (Sidebar)
    # ----------------------------------------
    with st.sidebar:
        st.markdown(
            """
            <div style='text-align: center; padding-bottom: 25px; border-bottom: 1px solid rgba(255,255,255,0.1); margin-bottom: 25px;'>
                <h1 style='color: #00F0FF; text-shadow: 0 0 20px rgba(0, 240, 255, 0.8); font-size: 1.8rem; margin-bottom: 5px; font-weight: 700; letter-spacing: 2px;'>ANTIGRAVITY</h1>
                <p style='color: #8A2BE2; font-family: "Fira Code", monospace; letter-spacing: 2px; font-size: 0.8rem; margin-top: 0; text-shadow: 0 0 10px rgba(138,43,226,0.5);'>RANKING ENGINE v4.0</p>
            </div>
            """, 
            unsafe_allow_html=True
        )
        
        st.markdown("<h3 style='color: #E2E8F0; font-size: 0.95rem; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 15px;'>⚙️ System Parameters</h3>", unsafe_allow_html=True)
        
        tech_weight = st.slider("Technical Depth Weight", 0, 100, 60, help="Weight applied to code assessment and architecture skills")
        beh_weight = st.slider("Behavioral Multiplier", 0, 100, 25, help="Impact of response rates and community engagement")
        exp_weight = st.slider("Experience Weight", 0, 100, 15, help="Weight of past roles and tenure length")
        
        st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
        st.markdown("<h3 style='color: #E2E8F0; font-size: 0.95rem; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 15px;'>🛡️ Threat Detection</h3>", unsafe_allow_html=True)
        
        trap_filter = st.toggle("Enable Honeypot/Trap Filter", value=True)
        if trap_filter:
            st.markdown("<p style='color: #00FF00; font-size: 0.8rem; font-family: \"Fira Code\", monospace;'>[●] Active: Filtering synthetic profiles</p>", unsafe_allow_html=True)
        else:
            st.markdown("<p style='color: #FF4500; font-size: 0.8rem; font-family: \"Fira Code\", monospace;'>[○] Inactive: Raw data ingest</p>", unsafe_allow_html=True)
            
        st.markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True)
        
        # Trigger Button
        initialize = st.button("INITIALIZE RANKING", use_container_width=True)
        
        st.markdown(
            """
            <div style='position: absolute; bottom: 20px; width: 100%; text-align: center; color: rgba(255,255,255,0.4); font-size: 0.7rem; font-family: "Fira Code", monospace;'>
                STATUS: SECURE CONNECTION<br>ENCRYPTION: AES-256
            </div>
            """,
            unsafe_allow_html=True
        )

    # ----------------------------------------
    # B. The Global Metrics HUD
    # ----------------------------------------
    st.markdown(
        """
        <div style='margin-bottom: 30px;'>
            <h2 style='font-weight: 300; letter-spacing: 2px; color: #F8FAFC; margin-bottom: 5px;'>TALENT INTELLIGENCE <span style='color: #00F0FF; font-weight: 700; text-shadow: 0 0 15px rgba(0, 240, 255, 0.6);'>COMMAND CENTER</span></h2>
            <p style='color: #94A3B8; font-size: 0.95rem;'>Deploying multi-stage AI reasoning to surface top-tier engineering talent.</p>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    # State Management for HUD values
    if 'processed' not in st.session_state:
        st.session_state.processed = "0"
        st.session_state.honeypots = "0"
        st.session_state.time_val = "0.00s"
        st.session_state.avg_conf = "0%"
        st.session_state.show_results = False
        st.session_state.candidates_data = []

    if initialize:
        placeholder = st.empty()
        simulate_terminal_boot(placeholder)
                
        start_time = time.time()
        
        # Execute the rank.py pipeline
        try:
            raw_df = rank.parse_candidates("candidates.jsonl")
            if not raw_df.empty:
                filtered_df = rank.apply_deterministic_filters(raw_df)
                honeypots_count = filtered_df['is_title_trap'].sum()
                
                if trap_filter:
                    filtered_df = filtered_df[~filtered_df['is_title_trap']].copy()
                    
                scored_df = rank.calculate_base_scores(filtered_df)
                final_df = rank.apply_behavioral_multiplier(scored_df)
                
                final_df['reasoning'] = final_df.apply(rank.generate_reasoning, axis=1)
                final_df = final_df.sort_values(by=['final_score', 'candidate_id'], ascending=[False, True])
                
                # Save physical files silently
                final_df['rank'] = range(1, len(final_df) + 1)
                final_df['score'] = final_df['final_score'].round(4)
                output_csv = final_df[['candidate_id', 'rank', 'score', 'reasoning']]
                output_csv.to_csv("team_antigravity.csv", index=False, encoding='utf-8')
                try:
                    output_csv.to_excel("team_antigravity.xlsx", index=False)
                except Exception:
                    pass
                
                end_time = time.time()
                
                st.session_state.processed = f"{len(raw_df):,}"
                st.session_state.honeypots = f"{honeypots_count:,}"
                st.session_state.time_val = f"{(end_time - start_time):.3f}s"
                avg_conf = (final_df['final_score'].mean() * 100) if not final_df.empty else 0
                st.session_state.avg_conf = f"{avg_conf:.1f}%"
                
                st.session_state.candidates_data = process_real_candidates(final_df.head(100))
                st.session_state.show_results = True
            else:
                st.error("Dataset is empty.")
        except FileNotFoundError:
            st.error("Dataset 'candidates.jsonl' not found.")
            st.session_state.show_results = False

    m1, m2, m3, m4 = st.columns(4)
    
    with m1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Candidates Analyzed</div>
            <div class="metric-value">{st.session_state.processed}</div>
        </div>
        """, unsafe_allow_html=True)
        
    with m2:
        val_class = "value-green" if st.session_state.honeypots != "0" else "value-dim"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Honeypots Eliminated</div>
            <div class="metric-value {val_class}">{st.session_state.honeypots}</div>
        </div>
        """, unsafe_allow_html=True)
        
    with m3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Pipeline Execution</div>
            <div class="metric-value">{st.session_state.time_val}</div>
        </div>
        """, unsafe_allow_html=True)
        
    with m4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Avg. Match Confidence</div>
            <div class="metric-value">{st.session_state.avg_conf}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<hr style='border: 0; height: 1px; background-image: linear-gradient(to right, rgba(255,255,255,0), rgba(0, 240, 255, 0.4), rgba(255,255,255,0)); margin: 40px 0;'>", unsafe_allow_html=True)

    # ----------------------------------------
    # C. The Candidate Dossiers (The Feed)
    # ----------------------------------------
    if st.session_state.show_results and st.session_state.candidates_data:
        
        col_title, col_btns = st.columns([2, 1])
        with col_title:
            st.markdown(
                """
                <h3 style='color: #E2E8F0; font-weight: 600; letter-spacing: 1px; margin: 0;'>RANKED SHORTLIST <span style='color: #8A2BE2; font-size: 0.9rem;'>[ REAL-TIME EVALUATION ]</span></h3>
                """, 
                unsafe_allow_html=True
            )
        
        with col_btns:
            # Export Buttons
            b1, b2 = st.columns(2)
            try:
                with open("team_antigravity.csv", "rb") as f:
                    b1.download_button("💾 DOWNLOAD CSV", f, file_name="team_antigravity.csv", mime="text/csv", use_container_width=True)
            except FileNotFoundError:
                pass
            try:
                with open("team_antigravity.xlsx", "rb") as f:
                    b2.download_button("💾 DOWNLOAD XLSX", f, file_name="team_antigravity.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
            except FileNotFoundError:
                pass

        st.markdown("<br>", unsafe_allow_html=True)

        for cand in st.session_state.candidates_data:
            # Layout for each dossier: Left Info (70%), Right Charts (30%)
            col_info, col_charts = st.columns([2.2, 1.2])
            
            with col_info:
                # Custom HTML Dossier Card
                st.markdown(f"""
                <div class="dossier-card">
                    <div class="candidate-header">
                        <div class="candidate-name">{cand['name']}</div>
                        <div class="candidate-id">ID: {cand['id']}</div>
                    </div>
                    <div class="ai-verdict">
                        <div class="ai-verdict-label">🧠 Reasoning Engine Output</div>
                        {cand['verdict']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Expandable details
                with st.expander("View Full Intelligence Dossier & Raw Data"):
                    tab1, tab2, tab3 = st.tabs(["Career History", "Behavioral Signals", "Raw JSON Payload"])
                    
                    with tab1:
                        st.markdown("<br>", unsafe_allow_html=True)
                        for role in cand['history'].split('\n'):
                            st.markdown(f"- {role}")
                            
                    with tab2:
                        st.markdown("<br>", unsafe_allow_html=True)
                        st.info(cand['redrob_signals'], icon="🔍")
                        
                    with tab3:
                        st.json(cand['raw_data'])
                        
            with col_charts:
                chart_container = st.container()
                with chart_container:
                    # Top chart: Match Gauge
                    st.plotly_chart(create_gauge_chart(cand['match_score']), use_container_width=True, config={'displayModeBar': False})
                    
                    # Bottom chart: Radar Skills
                    st.plotly_chart(create_radar_chart(cand['skills']), use_container_width=True, config={'displayModeBar': False})
                
            st.markdown("<div style='margin-bottom: 50px;'></div>", unsafe_allow_html=True)
            
    else:
        # Empty State
        st.markdown(
            """
            <div style='text-align: center; padding: 120px 20px; color: #475569; border: 1px dashed rgba(255,255,255,0.1); border-radius: 12px; background: rgba(0,0,0,0.2);'>
                <h2 style='font-weight: 300; margin-bottom: 10px; color: #64748B;'>SYSTEM STANDBY</h2>
                <p style='font-size: 1.1rem;'>Configure parameters and initialize ranking to deploy AI agents over the dataset.</p>
                <div style='margin-top: 20px; color: rgba(138, 43, 226, 0.6); font-family: "Fira Code", monospace;'>Awaiting Command...</div>
            </div>
            """, 
            unsafe_allow_html=True
        )

if __name__ == "__main__":
    main()
