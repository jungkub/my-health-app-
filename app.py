import streamlit as st
import pandas as pd
from data import questions
from utils import calculate_results, create_bar_chart, generate_summary, save_to_google_sheet

# --- 1. CONFIG & CONSTANTS ---
st.set_page_config(page_title="Psychological Health Assessment", page_icon="🌿", layout="wide")
SHEET_URL = "https://docs.google.com/spreadsheets/d/1ET8CJvJ2gq-lUfLP9NQNyNvy67JLd2NsjRwLuWAYLo4/edit?usp=sharing"

# --- 2. CSS STYLES ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Prompt:wght@300;400;500;600&display=swap');
    
    .stApp { background: linear-gradient(135deg, #e0f2f1 0%, #fff9c4 100%); font-family: 'Prompt', sans-serif; }
    h1, h2, h3, h4, h5, h6 { color: #000000 !important; font-weight: 600; font-family: 'Prompt', sans-serif; }
    p, span, div, li, label, .stMarkdown { color: #000000 !important; font-family: 'Prompt', sans-serif; }
    
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 5rem !important;
        max-width: 100% !important;
    }
    
    @media (max-width: 600px) {
        h1 { font-size: 1.5rem !important; line-height: 1.3 !important; }
        h2 { font-size: 1.3rem !important; }
        h3 { font-size: 1.1rem !important; }
        p, .stMarkdown p { font-size: 0.95rem !important; }
        .content-card { padding: 1.5rem !important; }
    }
    
    @media (min-width: 900px) {
        .block-container {
            max-width: 900px !important;
            padding-top: 4rem !important;
            margin: 0 auto;
        }
        h1 { font-size: 2.2rem !important; }
    }
    
    .content-card { 
        background: white; 
        padding: 2.5rem; 
        border-radius: 24px; 
        box-shadow: 0 8px 30px rgba(0,0,0,0.08); 
        margin-bottom: 2rem; 
        text-align: center;
    }

    .summary-box {
        background-color: #FFF3E0; 
        border: 2px solid #FF9800;
        border-radius: 15px; 
        padding: 25px; 
        margin-top: 10px;
        color: #000000 !important;
        font-size: 1.1rem;
        line-height: 1.7;
        text-align: left;
    }

    .stButton > button {
        width: 100%;
        border-radius: 16px !important;
        padding: 1rem 1rem !important;
        font-family: 'Prompt', sans-serif !important;
        font-size: 1.3rem !important;
        font-weight: 500 !important;
        transition: all 0.2s ease;
    }

    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #2ECC71 0%, #27AE60 100%) !important;
        color: white !important; 
        border: None !important;
        box-shadow: 0 10px 20px rgba(46, 204, 113, 0.3);
    }
    
    .stButton > button:not([kind="primary"]) {
        background-color: white !important;
        color: #2E7D32 !important;
        border: 2px solid #E0E0E0 !important; 
    }
    
    div[data-testid="stRadio"] label p { color: #000000 !important; font-size: 1.15rem; }
    div[data-testid="stRadio"] { background-color: rgba(255,255,255,0.5); padding: 10px; border-radius: 10px; }
    
    </style>
""", unsafe_allow_html=True)

# --- 3. SESSION STATE ---
if 'step' not in st.session_state: st.session_state.step = 'landing'
if 'q_idx' not in st.session_state: st.session_state.q_idx = 0
if 'answers' not in st.session_state: st.session_state.answers = {}
if 'weight' not in st.session_state: st.session_state.weight = 60.0
if 'height' not in st.session_state: st.session_state.height = 170.0

# --- 4. NAVIGATION LOGIC ---
def next_step():
    if st.session_state.step == 'landing': st.session_state.step = 'info'
    elif st.session_state.step == 'info': st.session_state.step = 'assessment'
    elif st.session_state.step == 'assessment':
        if st.session_state.q_idx < len(questions) - 1:
            st.session_state.q_idx += 1
        else:
            st.session_state.step = 'results'
    st.rerun()

def prev_step():
    if st.session_state.step == 'assessment':
        if st.session_state.q_idx > 0:
            st.session_state.q_idx -= 1
        else:
            st.session_state.step = 'info'
    elif st.session_state.step == 'info':
        st.session_state.step = 'landing'
    st.rerun()

# --- 5. PAGE CONTENT ---

if st.session_state.step == 'landing':
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("""
        <div class='content-card'>
            <h1>🌿 New Holistic Health Check</h1>
            <p style='margin-top: 10px; font-size: 1.2rem;'>
                แบบประเมินสุขภาพกายและใจฉบับปรับปรุง (20 ข้อ)<br>
                วิเคราะห์เจาะลึก พร้อมบันทึกผลทาง Google Sheets
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    if st.button("🌱 เริ่มต้นใช้งาน", type="primary"):
        next_step()

elif st.session_state.step == 'info':
    st.markdown("<div class='content-card'>", unsafe_allow_html=True)
    st.header("📋 ข้อมูลพื้นฐาน")
    st.write("กรุณาระบุข้อมูลเพื่อใช้คำนวณดัชนีมวลกาย (BMI)")
    
    col1, col2 = st.columns(2)
    with col1:
        st.session_state.weight = st.number_input("น้ำหนัก (kg)", value=st.session_state.weight, step=0.1)
    with col2:
        st.session_state.height = st.number_input("ส่วนสูง (cm)", value=st.session_state.height, step=0.1)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    with c1:
        if st.button("⬅️ ย้อนกลับ"): prev_step()
    with c2:
        if st.button("ถัดไป ➡️", type="primary"): next_step()

elif st.session_state.step == 'assessment':
    q_idx = st.session_state.q_idx
    current_q = questions[q_idx]

    icon = "💪" if current_q.category == 'Physical' else "🧠"
    progress = (q_idx + 1) / len(questions)

    st.markdown(f"<p style='text-align:center; font-size: 1.2rem; margin-bottom: 0;'>{icon} {current_q.category} Assessment</p>", unsafe_allow_html=True)
    st.progress(progress)
    st.markdown(f"<p style='text-align:center; color:#666;'>ข้อที่ {q_idx + 1} จาก {len(questions)}</p>", unsafe_allow_html=True)

    st.markdown(f"<div class='content-card'><h3>{current_q.text}</h3></div>", unsafe_allow_html=True)

    options = [c['text'] for c in current_q.choices]
    default_idx = st.session_state.answers.get(current_q.id, 0)
    choice_str = st.radio("เลือกคำตอบที่คุณรู้สึกว่าตรงกับตัวเองมากที่สุด:", options, index=default_idx, key=f"radio_{current_q.id}")
    
    for i, c in enumerate(current_q.choices):
        if c['text'] == choice_str:
            st.session_state.answers[current_q.id] = i
            break

    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        if st.button("⬅️ ย้อนกลับ"): prev_step()
    with c2:
        btn_txt = "ดูผลลัพธ์ ✅" if q_idx == len(questions)-1 else "ข้อถัดไป ➡️"
        if st.button(btn_txt, type="primary"): next_step()

elif st.session_state.step == 'results':
    st.balloons()
    st.markdown("<h1 style='text-align: center;'>📊 สรุปผลการประเมิน</h1>", unsafe_allow_html=True)
    
    results, strengths, gaps = calculate_results(
        st.session_state.answers, 
        weight=st.session_state.weight, 
        height=st.session_state.height
    )
    
    with st.spinner("กำลังบันทึกข้อมูลลงฐานข้อมูล..."):
        success, msg = save_to_google_sheet(
            st.session_state.weight, 
            st.session_state.height, 
            results, 
            st.session_state.answers,
            SHEET_URL
        )
        if success: st.success(msg)
        else: st.warning(msg)

    st.markdown("<div class='content-card' style='padding: 1.5rem;'>", unsafe_allow_html=True)
    st.subheader("ภาพรวมสุขภาพ (Score Overview)")
    fig = create_bar_chart(results)
    st.plotly_chart(fig, use_container_width=True, config={'staticPlot': True})
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.subheader("🛠️ ข้อแนะนำเพื่อการปรับปรุง")
    summary_html = generate_summary(gaps)
    st.markdown(f"<div class='summary-box'>{summary_html}</div>", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.subheader("🌟 จุดแข็งของคุณ")
    for item in strengths:
        st.markdown(f"""
            <div style='background: #E8F5E9; padding: 15px; border-radius: 12px; margin-bottom: 10px; border-left: 5px solid #2E7D32;'>
                <b>✅ {item['topic']}</b>: {item['advice']}
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)
    if st.button("🔄 ทำแบบประเมินใหม่", type="primary"):
        st.session_state.clear()
        st.rerun()
