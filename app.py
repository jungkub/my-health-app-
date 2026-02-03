import streamlit as st
import pandas as pd
from data import questions
from utils import calculate_results, create_bar_chart, generate_summary

# --- 1. SET PAGE CONFIG TO WIDE ---
st.set_page_config(page_title="Psychological Health Assessment", page_icon="🌿", layout="wide")

# --- CSS Styles ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Prompt:wght@300;400;500;600&display=swap');

    /* Global Text Color Enforcement & Font Change */
    .stApp { background: linear-gradient(135deg, #e0f2f1 0%, #fff9c4 100%); font-family: 'Prompt', sans-serif; }
    h1, h2, h3, h4, h5, h6 { color: #000000 !important; font-weight: 600; font-family: 'Prompt', sans-serif; }
    p, span, div, li, label, .stMarkdown { color: #000000 !important; font-family: 'Prompt', sans-serif; }

    /* Responsive & Mobile-First CSS */

    /* 1. Main Container Logic */
    /* Mobile by default (or small screens) */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 5rem !important;
        max-width: 100% !important;
    }

    /* PC / Large Screens */
    @media (min-width: 900px) {
        .block-container {
            max-width: 900px !important; /* Perfect 'Document' width */
            padding-top: 4rem !important;
            margin: 0 auto;
        }
    }

    /* 2. Card Styles */
    .content-card { 
        background: white; 
        padding: 2rem; 
        border-radius: 24px; 
        box-shadow: 0 8px 30px rgba(0,0,0,0.08); 
        margin-bottom: 2rem; 
        text-align: center;
    }

    .strength-card { background-color: #E8F5E9; border-left: 5px solid #2E7D32; padding: 15px; border-radius: 10px; margin-bottom: 10px; text-align: left; }

    /* Summary Box */
    .summary-box {
        background-color: #FFF3E0; 
        border: 2px solid #FF9800;
        border-radius: 15px; 
        padding: 25px; 
        margin-top: 10px;
        color: #000000 !important;
        font-size: 1.1rem;
        line-height: 1.8;
        text-align: left;
    }

    /* 3. Chunky Buttons (Fixed Size Issue) */
    .stButton > button {
        width: 100%;
        border-radius: 16px !important; /* Slightly more square/modern */
        padding: 1rem 1rem !important; /* CHUNKY Padding */
        font-family: 'Prompt', sans-serif !important;
        font-size: 1.3rem !important; /* Larger Text */
        font-weight: 500 !important;
        letter-spacing: 0.5px;
        transition: all 0.2s ease;
    }

    .stButton > button:active {
        transform: scale(0.98);
    }

    /* Primary Button Override */
    .stButton > button[kind="primary"], 
    .stButton > button[data-testid="baseButton-primary"] {
        background: linear-gradient(135deg, #2ECC71 0%, #27AE60 100%) !important;
        color: white !important; 
        border: None !important;
        box-shadow: 0 10px 20px rgba(46, 204, 113, 0.3);
    }

    /* Secondary Button Override */
    .stButton > button[kind="secondary"],
    .stButton > button[data-testid="baseButton-secondary"],
    .stButton > button:not([kind="primary"]):not([data-testid="baseButton-primary"]) {
        background-color: white !important;
        color: #2E7D32 !important;
        border: 2px solid #E0E0E0 !important; /* Softer border initially */
    }

    /* Hover Effects */
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 15px rgba(0,0,0,0.1);
    }

    div[data-testid="stRadio"] label p { color: #000000 !important; font-size: 1.15rem; }
    div[data-testid="stRadio"] { background-color: rgba(255,255,255,0.5); padding: 10px; border-radius: 10px; }

    </style>
""", unsafe_allow_html=True)

# --- State ---
if 'step' not in st.session_state: st.session_state.step = 'landing'
if 'q_idx' not in st.session_state: st.session_state.q_idx = 0
if 'answers' not in st.session_state: st.session_state.answers = {}

# --- Landing ---
if st.session_state.step == 'landing':
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("""
        <div class='content-card'>
            <h1>🌿 New Holistic Health Check</h1>
            <p style='font-size:1.3rem; margin-top: 10px;'>
                แบบประเมินสุขภาพกายและใจฉบับปรับปรุง (20 ข้อ)<br>
                วิเคราะห์จุดแข็งและจุดที่ควรปรับปรุง
            </p>
        </div>
    """, unsafe_allow_html=True)

    if st.button("🌱 เริ่มทำแบบประเมิน", type="primary"):
        st.session_state.step = 'assessment'
        st.rerun()

# --- Assessment ---
elif st.session_state.step == 'assessment':
    q_idx = st.session_state.q_idx
    try:
        current_q = questions[q_idx]
    except IndexError:
        st.session_state.step = 'results'
        st.rerun()

    # --- Header Information ---
    icon = "💪" if current_q.category == 'Physical' else "🧠"
    progress = (q_idx + 1) / len(questions)

    st.markdown(f"""
        <div style='text-align: center; margin-bottom: 10px;'>
            <h2 style='margin:0; font-size: 1.8rem;'>{icon} {current_q.category} Part</h2>
            <p style='font-size: 1rem; color: #666;'>ข้อที่ {q_idx + 1}/{len(questions)}</p>
        </div>
    """, unsafe_allow_html=True)
    st.progress(progress)
    st.markdown("<br>", unsafe_allow_html=True)

    # --- Question Card (Native Width) ---
    st.markdown(f"<div class='content-card' style='text-align: center;'><h3>{current_q.text}</h3></div>",
                unsafe_allow_html=True)

    # Choices
    options = [c['text'] for c in current_q.choices]
    choice = st.radio("เลือกคำตอบ:", options, key=f"q_{current_q.id}")

    st.markdown("<br>", unsafe_allow_html=True)

    # Buttons (Responsive Columns)
    c1, c2 = st.columns(2)

    with c1:
        if q_idx > 0:
            if st.button("⬅️ ย้อนกลับ"):
                st.session_state.q_idx -= 1
                st.rerun()
        else:
            st.write("")  # Spacer

    with c2:
        btn_text = "ดูผลลัพธ์ ✅" if q_idx == len(questions) - 1 else "ข้อถัดไป ➡️"
        if st.button(btn_text, type="primary"):
            for i, c in enumerate(current_q.choices):
                if c['text'] == choice:
                    st.session_state.answers[current_q.id] = i
                    break
            if q_idx < len(questions) - 1:
                st.session_state.q_idx += 1
            else:
                st.session_state.step = 'results'
            st.rerun()

# --- Results ---
elif st.session_state.step == 'results':
    st.balloons()
    st.markdown("<h1 style='text-align: center;'>📊 ผลวิเคราะห์เจาะลึก</h1>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    results, strengths, gaps = calculate_results(st.session_state.answers)

    # 1. Chart Section
    st.markdown("<div class='content-card' style='padding: 1rem;'>", unsafe_allow_html=True)
    st.subheader("ระดับคะแนน (Scores)")
    st.plotly_chart(create_bar_chart(results), use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # 2. Recommendations
    st.subheader("🛠️ สิ่งที่ควรปรับปรุง (Areas for Improvement)")
    summary_text = generate_summary(gaps)
    st.markdown(f"<div class='summary-box'>{summary_text}</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # 3. Strengths
    st.subheader("🌟 สิ่งที่คุณทำได้ดีแล้ว (Strengths)")
    if not strengths:
        st.warning("พยายามอีกนิดนะครับ!")
    else:
        for item in strengths:
            st.markdown(f"""
                <div class='strength-card'>
                    <b>✅ {item['topic']}</b><br>
                    <span style='color: #1B5E20;'>{item['advice']}</span>
                </div>
            """, unsafe_allow_html=True)

    st.markdown("<br><hr><br>", unsafe_allow_html=True)
    if st.button("🔄 ทำแบบประเมินใหม่", type="primary"):
        st.session_state.clear()
        st.rerun()
