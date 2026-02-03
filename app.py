import streamlit as st
import pandas as pd
from data import questions
from utils import calculate_results, create_bar_chart, generate_summary

# --- 1. SET PAGE CONFIG TO WIDE ---
st.set_page_config(page_title="Psychological Health Assessment", page_icon="🌿", layout="wide")

# --- CSS Styles ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Kanit:wght@300;500;600&display=swap');

    /* Global Text Color Enforcement */
    .stApp { background: linear-gradient(135deg, #e0f2f1 0%, #fff9c4 100%); font-family: 'Kanit', sans-serif; }
    h1, h2, h3, h4, h5, h6 { color: #000000 !important; font-weight: 600; }
    p, span, div, li, label, .stMarkdown { color: #000000 !important; }

    /* Constraint Container for Wide Mode */
    .main-container {
        max-width: 1200px;
        margin: 0 auto;
        padding-top: 2rem;
    }

    /* Card Styles */
    .content-card { background: white; padding: 3rem; border-radius: 20px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); margin-bottom: 1rem; }
    .side-card { background: rgba(255,255,255,0.6); padding: 2rem; border-radius: 20px; text-align: center; }

    .strength-card { background-color: #E8F5E9; border-left: 5px solid #2E7D32; padding: 15px; border-radius: 10px; margin-bottom: 10px; }

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
    }

    .stButton>button[kind="primary"] {
        background: linear-gradient(90deg, #2ECC71, #27AE60) !important;
        color: white !important; border-radius: 50px !important; border: None !important;
        box-shadow: 0 4px 15px rgba(46, 204, 113, 0.4);
        font-size: 1.2rem !important;
        padding: 0.8rem 2rem !important;
    }

    /* Secondary/Back Button Styling */
    .stButton>button[kind="secondary"] {
        background-color: #FFFFFF !important;
        color: #2E7D32 !important;
        border: 2px solid #2E7D32 !important;
        border-radius: 50px !important;
        padding: 0.8rem 2rem !important;
    }
    .stButton>button[kind="secondary"]:hover {
        background-color: #E8F5E9 !important;
    }

    div[data-testid="stRadio"] label p { color: #000000 !important; font-size: 1.2rem; }
    </style>
""", unsafe_allow_html=True)

# --- State ---
if 'step' not in st.session_state: st.session_state.step = 'landing'
if 'q_idx' not in st.session_state: st.session_state.q_idx = 0
if 'answers' not in st.session_state: st.session_state.answers = {}


# --- Helper for layout centering ---
def centered_container():
    col1, col2, col3 = st.columns([1, 2, 1])
    return col2


# --- Landing ---
if st.session_state.step == 'landing':
    with centered_container():
        st.markdown("<br><br>", unsafe_allow_html=True)  # Spacing
        st.markdown(
            "<div class='content-card' style='text-align:center;'><h1>🌿 New Holistic Health Check</h1><p style='font-size:1.3rem;'>แบบประเมินสุขภาพกายและใจฉบับปรับปรุง (20 ข้อ)<br>เน้นวิเคราะห์จุดแข็งและจุดที่ควรปรับปรุงของคุณ</p></div>",
            unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        col_start, _, _ = st.columns(
            [1, 0.1, 0.1])  # Trick to align button center in the col2 container if needed, or just standard
        if st.button("เริ่มทำแบบประเมิน", type="primary", use_container_width=True):
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

    # --- TOP HEADER: Progress & Category Info ---
    # Centered Header Info
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        icon = "💪" if current_q.category == 'Physical' else "🧠"
        progress = (q_idx + 1) / len(questions)
        st.markdown(f"""
            <div style='text-align: center; margin-bottom: 20px;'>
                <h2 style='margin:0;'>{icon} {current_q.category} Part</h2>
                <p style='font-size: 1.1rem; color: #555;'>ข้อที่ {q_idx + 1} จาก {len(questions)}</p>
            </div>
        """, unsafe_allow_html=True)
        st.progress(progress)

    st.markdown("<br>", unsafe_allow_html=True)

    # --- CENTERED QUESTION CARD ---
    # Use columns to constrain width in the center
    col_left, col_center, col_right = st.columns([1, 2, 1])

    with col_center:
        st.markdown(f"<div class='content-card'><h3 style='text-align:center;'>{current_q.text}</h3></div>",
                    unsafe_allow_html=True)

        # Centered Choices
        options = [c['text'] for c in current_q.choices]
        choice = st.radio("เลือกคำตอบ:", options, key=f"q_{current_q.id}")

        st.markdown("<br>", unsafe_allow_html=True)

        # Navigation Buttons (Centered)
        b_col1, b_col2 = st.columns([1, 1])
        if q_idx > 0:
            if b_col1.button("⬅️ ย้อนกลับ", type="secondary", use_container_width=True):
                st.session_state.q_idx -= 1
                st.rerun()
        else:
            b_col1.write("")  # Spacer if no back button

        btn_text = "ดูผลลัพธ์ ✅" if q_idx == len(questions) - 1 else "ข้อถัดไป ➡️"
        if b_col2.button(btn_text, type="primary", use_container_width=True):
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

    from utils import generate_summary

    results, strengths, gaps = calculate_results(st.session_state.answers)

    # Layout: [ Chart (1) | Summary (1) ]
    r_col1, r_col2 = st.columns([1, 1])

    with r_col1:
        st.markdown("<div class='content-card' style='padding: 1rem;'>", unsafe_allow_html=True)
        st.subheader("ระดับคะแนน (Scores)")
        st.plotly_chart(create_bar_chart(results), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with r_col2:
        # Recommendations
        st.subheader("🛠️ สิ่งที่ควรปรับปรุง (Areas for Improvement)")
        summary_text = generate_summary(gaps)
        st.markdown(f"<div class='summary-box'>{summary_text}</div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Strengths
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
    if st.button("🔄 ทำแบบประเมินใหม่", type="primary", use_container_width=True):
        st.session_state.clear()
        st.rerun()
