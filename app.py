import streamlit as st
import pandas as pd
from data import questions, references
from utils import calculate_scores, determine_profile, create_radar_chart

# --- 1. การตั้งค่าหน้าเว็บ ---
st.set_page_config(page_title="Psychological Health Assessment", page_icon="🌿", layout="centered")

# --- 2. CSS ทั้งหมด (แก้ไขเรื่องช่องว่างและสีปุ่ม) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Kanit:wght@300;500;600&display=swap');

    .stApp {
        background: linear-gradient(135deg, #e0f2f1 0%, #fff9c4 100%);
        font-family: 'Kanit', sans-serif;
    }

    /* บังคับสีอักษรหัวข้อและเนื้อหาให้เข้มชัดเจน */
    h1, h2, h3, h4 { color: #0A3D0A !important; font-weight: 600 !important; }
    p, span, label, li { color: #000000 !important; font-weight: 500 !important; }

    /* กล่องเนื้อหาหลัก */
    .content-card {
        background-color: #FFFFFF;
        padding: 2rem;
        border-radius: 25px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.15);
        border: 3px solid #4CAF50;
        margin-bottom: 1rem;
        text-align: center;
    }

    /* การ์ดหน้าสรุปผล (บังคับสีดำสนิท) */
    .result-card {
        background-color: #FFFFFF !important;
        padding: 25px;
        border-radius: 20px;
        border-top: 10px solid #FF9800;
        box-shadow: 0 8px 25px rgba(0,0,0,0.2);
        margin-bottom: 20px;
        text-align: left;
    }

    /* --- ปรับแต่งสีปุ่ม --- */
    /* ปุ่มทั่วไป / ปุ่มย้อนกลับ */
    .stButton>button {
        background-color: #FFFFFF !important;
        color: #2E7D32 !important;
        border: 2px solid #2E7D32 !important;
        border-radius: 50px !important;
        font-weight: 600 !important;
    }

  /* --- ปรับแต่งปุ่มเริ่มและปุ่มไปต่อให้เด่น (ไม่ใช่สีดำ) --- */
    .stButton>button[kind="primary"] {
        background: linear-gradient(90deg, #2ECC71, #27AE60) !important; /* สีเขียวสดใส */
        color: #FFFFFF !important; /* ตัวอักษรสีขาวบริสุทธิ์ */
        border: none !important;
        border-radius: 50px !important;
        padding: 0.6rem 2rem !important;
        font-weight: 600 !important;
        font-size: 1.1rem !important;
        box-shadow: 0 4px 15px rgba(46, 204, 113, 0.4) !important;
        transition: all 0.3s ease !important;
    }

    /* เอฟเฟกต์ตอนเมาส์ชี้ ให้ดูมีมิติ */
    .stButton>button[kind="primary"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(46, 204, 113, 0.6) !important;
        background: linear-gradient(90deg, #27AE60, #1E8449) !important;
    }

    /* บังคับสีตัวเลือก Radio */
    div[data-testid="stRadio"] label p {
        color: #000000 !important;
        font-size: 1.1rem !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. ตรรกะเบื้องหลังแอป ---
if 'step' not in st.session_state: st.session_state.step = 'landing'
if 'q_idx' not in st.session_state: st.session_state.q_idx = 0
if 'answers' not in st.session_state: st.session_state.answers = {}


def get_topic_assets(q_id):
    q_id_str = str(q_id)
    if "P" in q_id_str: return "🏃‍♂️"
    if "M" in q_id_str: return "🧠"
    if "S" in q_id_str: return "🤝"
    return "💡"


# --- 4. การแสดงผลหน้าจอ ---

# หน้าแรก (แก้ช่องว่าง)
if st.session_state.step == 'landing':
    st.markdown("""
        <div class='content-card'>
            <div style='font-size: 80px;'>🌿</div>
            <h1>Holistic Health Assessment</h1>
            <p style='font-size: 1.2rem;'>มาเช็กสมดุลชีวิตกันเถอะ! ใช้เวลาเพียงเล็กน้อย เพื่อรู้จักตัวเองให้มากขึ้น</p>
        </div>
    """, unsafe_allow_html=True)
    if st.button("เริ่มกันเลย! (Start)", use_container_width=True, type="primary"):
        st.session_state.step = 'assessment'
        st.rerun()

# หน้าคำถาม
elif st.session_state.step == 'assessment':
    q_idx = st.session_state.q_idx
    current_q = questions[q_idx]

    st.markdown(
        f"<h2 style='text-align: center;'>{get_topic_assets(current_q.id)} ข้อที่ {q_idx + 1} / {len(questions)}</h2>",
        unsafe_allow_html=True)
    st.progress((q_idx + 1) / len(questions))

    st.markdown(f"<div class='content-card' style='text-align: left;'><h3>{current_q.text}</h3></div>",
                unsafe_allow_html=True)

    options = [c['text'] for c in current_q.choices]
    choice = st.radio("เลือกสิ่งที่ตรงกับคุณ:", options, key=f"r_{current_q.id}")

    col1, col2 = st.columns(2)
    with col1:
        # ปุ่มย้อนกลับ (เป็นปุ่มธรรมดา สีขาวขอบเขียว)
        if q_idx > 0 and st.button("⬅️ ย้อนกลับ", use_container_width=True):
            st.session_state.q_idx -= 1
            st.rerun()
    with col2:
        # ปุ่มถัดไป (เป็นปุ่ม Primary สีเขียวตัวหนังสือขาว)
        btn_text = "ดูผลลัพธ์ ✅" if q_idx == len(questions) - 1 else "ข้อถัดไป ➡️"
        if st.button(btn_text, type="primary", use_container_width=True):
            for i, c in enumerate(current_q.choices):
                if c['text'] == choice:
                    st.session_state.answers[current_q.id] = i
            if q_idx < len(questions) - 1:
                st.session_state.q_idx += 1
            else:
                st.session_state.step = 'results'
            st.rerun()

# หน้าสรุปผล (แก้สีอักษรกลืน)
elif st.session_state.step == 'results':
    st.balloons()
    st.markdown("<h1 style='text-align: center;'>📊 ผลวิเคราะห์ของคุณ</h1>", unsafe_allow_html=True)

    scores = calculate_scores(st.session_state.answers)
    profile = determine_profile(scores)

    col_graph, col_info = st.columns([1.2, 1])
    with col_graph:
        st.plotly_chart(create_radar_chart(scores), use_container_width=True)
    with col_info:
        st.markdown(f"""
            <div class='result-card'>
                <h2 style='color:#1B5E20 !important;'>{profile['desc']}</h2>
                <p style='font-size: 1.1rem;'>{profile['detail']}</p>
                <div style='background-color: #F1F8E9; padding: 15px; border-radius: 12px; border: 2px solid #C8E6C9;'>
                    <b style='color: #0A3D0A !important;'>💡 คำแนะนำ:</b><br>
                    <span>{profile['recommendation']}</span>
                </div>
            </div>
        """, unsafe_allow_html=True)

    if st.button("🔄 ทำใหม่", use_container_width=True):
        st.session_state.clear()
        st.rerun()