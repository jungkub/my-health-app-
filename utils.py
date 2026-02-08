import plotly.graph_objects as go
from data import questions
import datetime
import pandas as pd

def calculate_bmi(weight, height):
    """
    Calculate BMI and return score, category label, and severity.
    Weight in kg, Height in cm.
    """
    if not weight or not height or height <= 0:
        return 0, "ข้อมูลไม่สมบูรณ์", 1, 0

    height_m = height / 100
    bmi = weight / (height_m ** 2)
    
    # User's Logic:
    # < 18.5 -> 1 Score | Improve
    # 18.5 – 22.9 -> 3 Score | Excellent
    # 23.0 – 24.9 -> 2 Score | Fairly Good
    # 25.0 – 29.9 -> 1 Score | Improve
    # >= 30.0 -> 0 Score | Highly Improve
    
    if bmi < 18.5:
        return 1, f"BMI {bmi:.1f}: น้ำหนักต่ำกว่าเกณฑ์ (Underweight)", 2, 3 
    elif 18.5 <= bmi <= 22.9:
        return 3, f"BMI {bmi:.1f}: น้ำหนักปกติ (Normal)", 1, 3 
    elif 23.0 <= bmi <= 24.9:
        return 2, f"BMI {bmi:.1f}: น้ำหนักเกิน (Overweight)", 2, 3 
    elif 25.0 <= bmi <= 29.9:
        return 1, f"BMI {bmi:.1f}: อ้วนระดับ 1 (Obese I)", 3, 3 
    else:
        return 0, f"BMI {bmi:.1f}: อ้วนระดับ 2 (Obese II)", 3, 3


def calculate_results(answers, weight=None, height=None):
    """
    answers: dict of question_id -> selected_choice_index
    Returns: results dict, strengths list, gaps list
    """
    results = {
        'Physical': {'score': 0, 'max': 0},
        'Mental': {'score': 0, 'max': 0}
    }
    
    strengths = []
    gaps = []
    
    # 1. Standard Questions
    for q in questions:
        choice_idx = answers.get(q.id)
        if choice_idx is None: continue
            
        choice = q.choices[choice_idx]
        score = choice['score']
        
        results[q.category]['score'] += score
        max_q_score = max(c['score'] for c in q.choices)
        results[q.category]['max'] += max_q_score
        
        advice = ""
        for score_range, text in q.advice_map.items():
            if score in score_range:
                advice = text
                break
        
        item_detail = {
            'topic': q.short_topic,
            'category': q.category,
            'score': score,
            'advice': advice,
            'severity': q.severity
        }
        
        if score <= 1:
            gaps.append(item_detail)
        else:
            strengths.append(item_detail)

    # 2. BMI Calculation
    if weight and height:
        bmi_score, bmi_advice, bmi_severity, bmi_max = calculate_bmi(weight, height)
        results['Physical']['score'] += bmi_score
        results['Physical']['max'] += bmi_max
        
        bmi_detail = {
            'topic': "ดัชนีมวลกาย (BMI)",
            'category': 'Physical',
            'score': bmi_score,
            'advice': bmi_advice,
            'severity': bmi_severity
        }
        
        if bmi_score <= 1:
            gaps.append(bmi_detail)
        else:
            strengths.append(bmi_detail)

    # Sort Gaps by Severity (Critical first)
    gaps.sort(key=lambda x: x['severity'], reverse=True)

    return results, strengths, gaps


def save_to_google_sheet(weight, height, results, answers, sheet_url):
    """
    Connect to Google Sheets and append a row.
    Uses st.connection if available (Streamlit way).
    """
    import streamlit as st
    try:
        from streamlit_gsheets import GSheetsConnection
        
        # Prepare Data
        # Flatten answers for storage
        ans_flat = {f"Q{k}": v for k, v in answers.items()}
        data = {
            'Timestamp': [datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
            'Weight': [weight],
            'Height': [height],
            'Physical_Score': [results['Physical']['score']],
            'Mental_Score': [results['Mental']['score']]
        }
        data.update({k: [v] for k, v in ans_flat.items()})
        df_new = pd.DataFrame(data)

        # Connect
        conn = st.connection("gsheets", type=GSheetsConnection)
        
        # Diagnostics: Check if service account info is actually present in secrets
        if "connections" not in st.secrets or "gsheets" not in st.secrets["connections"]:
             return False, "ไม่พบการตั้งค่า [connections.gsheets] ใน Secrets (กรุณาดูคู่มือ GOOGLE_SHEETS_SETUP.md)"
        
        # Read existing data
        try:
            existing_data = conn.read(spreadsheet=sheet_url)
        except Exception as read_err:
            if "Public Spreadsheet cannot be written to" in str(read_err):
                 return False, "ยังไม่ได้ตั้งค่า Service Account หรือยังไม่ได้ Share Sheet ให้ Email ของ Service Account ครับ"
            raise read_err

        # Create updated DataFrame securely
        if existing_data is None or existing_data.empty:
            updated_df = df_new
        else:
            # Avoid FutureWarning by ensuring we don't have all-NA columns that might change dtypes
            updated_df = pd.concat([existing_data, df_new], ignore_index=True)
            
        conn.update(spreadsheet=sheet_url, data=updated_df)
        return True, "บันทึกข้อมูลลง Google Sheet สำเร็จ!"
    except Exception as e:
        # Fallback to local CSV
        try:
            df_new.to_csv("assessment_results.csv", mode='a', header=not pd.io.common.file_exists("assessment_results.csv"), index=False)
            return False, f"เชื่อมต่อ Sheets ไม่ได้ (บันทึกในเครื่องแทน): {str(e)}"
        except:
            return False, "ไม่สามารถบันทึกข้อมูลได้"


def create_bar_chart(category_scores):
    """
    Horizontal Bar Chart for Physical vs Mental scores
    """
    p_score = category_scores['Physical']['score']
    p_max = category_scores['Physical']['max'] or 1
    m_score = category_scores['Mental']['score']
    m_max = category_scores['Mental']['max'] or 1
    
    phys_pct = (p_score / p_max) * 100
    ment_pct = (m_score / m_max) * 100
    
    current_values = [phys_pct, ment_pct]
    categories = ['Physical Health (กาย)', 'Mental Health (ใจ)']
    colors = ['#2ECC71', '#3498DB'] 

    fig = go.Figure(go.Bar(
        x=current_values,
        y=categories,
        orientation='h',
        text=[f"{v:.1f}%" for v in current_values],
        textposition='auto',
        marker_color=colors,
        marker_line_width=0,
        opacity=0.9
    ))

    fig.update_layout(
        xaxis=dict(
            range=[0, 100],
            title="Score (%)",
            tickfont=dict(family='Prompt', size=12, color='black'),
            title_font=dict(family='Prompt', size=14, color='black'),
            showgrid=True,
            gridcolor='#E0E0E0',
            fixedrange=True
        ),
        yaxis=dict(
            tickfont=dict(family='Prompt', size=16, color='black', weight='bold'),
            fixedrange=True
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=20, r=20, t=30, b=30),
        height=300, 
        showlegend=False,
        dragmode=False
    )
    
    return fig


def generate_summary(gaps):
    """
    Generate summary grouped by category and sorted by severity.
    """
    if not gaps:
        return "สุขภาพโดยรวมของคุณอยู่ในเกณฑ์ดีเยี่ยม! ไม่มีจุดที่ต้องกังวลเป็นพิเศษ รักษาความสมดุลนี้ไว้นะครับ"

    phys_gaps = [g for g in gaps if g['category'] == 'Physical']
    mental_gaps = [g for g in gaps if g['category'] == 'Mental']

    summary = "จากการวิเคราะห์ พบว่ามีบางจุดที่คุณควรหันมาดูแลใส่ใจเพิ่มขึ้น โดยเรียงลำดับตามความสำคัญครับ:<br><br>"
    
    def format_list(item_list):
        res = ""
        seen = set()
        for item in item_list:
            if item['advice'] in seen: continue
            seen.add(item['advice'])
            
            # Icon based on severity
            icon = "🔴 " if item['severity'] >= 3 else "🟡 " if item['severity'] == 2 else "🔵 "
            color = "#D32F2F" if item['severity'] >= 3 else "#F57C00" if item['severity'] == 2 else "#1976D2"
            
            res += f"<div style='color: {color}; margin-bottom: 5px;'>{icon}<b>{item['topic']}:</b> {item['advice']}</div>"
        return res

    if phys_gaps:
        summary += "<b>💪 ด้านสุขภาพกาย:</b><br>"
        summary += format_list(phys_gaps)
        summary += "<br>"

    if mental_gaps:
        summary += "<b>🧠 ด้านสุขภาพจิต:</b><br>"
        summary += format_list(mental_gaps)

    return summary
