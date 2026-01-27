import plotly.graph_objects as go
import pandas as pd
from data import questions, profiles, default_profile

def calculate_scores(answers):
    """
    answers: dict of question_id -> selected_choice_index
    Returns: dict of dimension scores (P, M, S, I)
    """
    raw_scores = {'P': 0, 'M': 0, 'S': 0, 'I': 0}
    max_scores = {'P': 0, 'M': 0, 'S': 0, 'I': 0}

    for q in questions:
        # User answer
        choice_idx = answers.get(q.id)
        if choice_idx is not None:
             selected_scores = q.choices[choice_idx]['scores']
             for key in raw_scores:
                 raw_scores[key] += selected_scores.get(key, 0)
        
        # Calculate max possible score for normalization (simplified per question max)
        # Actually, let's just sum up the raw scores for now. 
        # But to be precise, we want to normalize to 0-100 scale?
        # Let's verify max possible per dimension.
        # For this prototype, raw scores are fine to display relative balance.
        # But let's check max potential to normalize if needed.
        pass

    return raw_scores

def determine_profile(scores):
    """
    scores: dict of dimension scores
    Returns: profile dict
    """
    # Normalize simply for profile check logic if needed, or use raw thresholds
    # Let's assume the thresholds in data.py are based on raw totals approx.
    # To be safe, let's normalize to 0-100 range estimate or relative.
    
    # Simple normalization: specific score / max possible roughly
    # Let's just pass raw scores to the criteria functions in data.py and adjust thresholds there if needed.
    # Or better, we define thresholds based on the max possible score of 15 questions * 10 points = 150?
    # No, points define distribution.
    
    # Just iterate and find first match
    for key, profile in profiles.items():
        if profile['criteria'](scores):
            return profile
            
    return default_profile

def create_radar_chart(scores):
    """
    Creates a radar chart using Plotly
    """
    categories = ['Physical (กาย)', 'Mental (ใจ)', 'Social (สังคม)', 'Intellectual (ปัญญา)']
    values = [scores.get('P', 0), scores.get('M', 0), scores.get('S', 0), scores.get('I', 0)]
    
    # Close the loop for radar chart
    categories = [*categories, categories[0]]
    values = [*values, values[0]]

    fig = go.Figure(
        data=[
            go.Scatterpolar(
                r=values,
                theta=categories,
                fill='toself',
                name='Your Health Balance',
                line_color='#2E8B57',
                fillcolor='rgba(46, 139, 87, 0.3)'
            )
        ]
    )

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, max(values) + 10]
            )
        ),
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Inter, sans-serif", size=14, color="#4A4A4A"),
        margin=dict(l=40, r=40, t=40, b=40)
    )
    
    return fig
