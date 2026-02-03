import plotly.graph_objects as go
from data import questions


def calculate_results(answers):
    """
    answers: dict of question_id -> selected_choice_index
    Returns: dict containing totals, strengths, gaps
    """
    results = {
        'Physical': {'score': 0, 'max': 0, 'details': []},
        'Mental': {'score': 0, 'max': 0, 'details': []}
    }

    strengths = []
    gaps = []

    for q in questions:
        choice_idx = answers.get(q.id)
        if choice_idx is None:
            continue

        choice = q.choices[choice_idx]
        score = choice['score']

        # Accumulate Category Score
        results[q.category]['score'] += score
        max_q_score = max(c['score'] for c in q.choices)
        if max_q_score == 0: max_q_score = 1  # Prevent div by zero
        results[q.category]['max'] += max_q_score

        # Logic for Advice/Gap/Strength
        advice = ""
        for score_range, text in q.advice_map.items():
            if score in score_range:
                advice = text
                break

        item_detail = {
            'topic': q.short_topic,  # Use Short Topic!
            'score': score,
            'advice': advice
        }

        if score <= 1:
            gaps.append(item_detail)
        else:
            strengths.append(item_detail)

    return results, strengths, gaps


def create_bar_chart(category_scores):
    """
    Horizontal Bar Chart for Physical vs Mental scores (Easy to Read)
    """
    p_score = category_scores['Physical']['score']
    p_max = category_scores['Physical']['max'] or 1
    m_score = category_scores['Mental']['score']
    m_max = category_scores['Mental']['max'] or 1

    phys_pct = (p_score / p_max) * 100
    ment_pct = (m_score / m_max) * 100

    current_values = [phys_pct, ment_pct]
    categories = ['Physical Health (กาย)', 'Mental Health (ใจ)']
    colors = ['#2ECC71', '#3498DB']  # Green for Body, Blue for Mind

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
            tickfont=dict(family='Kanit', size=12, color='black'),
            title_font=dict(family='Kanit', size=14, color='black'),
            showgrid=True,
            gridcolor='#E0E0E0'
        ),
        yaxis=dict(
            tickfont=dict(family='Kanit', size=16, color='black', weight='bold')
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=20, r=20, t=30, b=30),
        height=300,  # Compact height
        showlegend=False
    )

    return fig


def generate_summary(gaps):
    """
    Synthesize a nice, natural language summary using HTML for app compatibility.
    """
    if not gaps:
        return "สุขภาพโดยรวมของคุณอยู่ในเกณฑ์ดีเยี่ยม! ไม่มีจุดที่ต้องกังวลเป็นพิเศษ รักษาความสมดุลนี้ไว้นะครับ"

    topics = [item['topic'] for item in gaps]

    # 1. Opening
    summary = "จากการวิเคราะห์ พบว่ามีบางจุดที่คุณอาจจะต้องหันมาดูแลใส่ใจเพิ่มขึ้นอีกนิดครับ "

    # 2. Topic Listing (Natural Phrasing)
    if len(topics) == 1:
        summary += f"หลักๆ คือเรื่อง <b>{topics[0]}</b> ครับ "
    elif len(topics) == 2:
        summary += f"ได้แก่เรื่อง <b>{topics[0]}</b> และ <b>{topics[1]}</b> ครับ "
    elif len(topics) >= 3:
        summary += f"โดยเฉพาะเรื่อง <b>{topics[0]}</b>, <b>{topics[1]}</b> และ <b>{topics[2]}</b> "
        if len(topics) > 3:
            summary += f"รวมถึงประเด็นอื่นๆ ย่อยๆ อีกเล็กน้อย "

    summary += "<br><br><b>📌 คำแนะนำสำหรับคุณ:</b><br>"

    # 3. Advice Synthesis (Combine related advice)
    seen_advice = set()
    count = 0
    for item in gaps:
        if item['advice'] not in seen_advice and count < 4:
            summary += f"- {item['advice']}<br>"
            seen_advice.add(item['advice'])
            count += 1

    return summary
