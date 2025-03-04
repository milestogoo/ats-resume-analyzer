import plotly.graph_objects as go
import streamlit as st

def create_score_chart(score):
    """Create a gauge chart for overall score"""
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = score,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Compliance Score"},
        gauge = {
            'axis': {'range': [0, 100]},
            'bar': {'color': "rgb(75, 192, 192)"},
            'steps': [
                {'range': [0, 33], 'color': "rgb(255, 99, 132)"},
                {'range': [33, 66], 'color': "rgb(255, 205, 86)"},
                {'range': [66, 100], 'color': "rgb(75, 192, 192)"}
            ]
        }
    ))
    
    fig.update_layout(height=300)
    st.plotly_chart(fig, use_container_width=True)

def create_section_breakdown(section_scores):
    """Create bar chart for section-wise scores"""
    fig = go.Figure()
    
    sections = list(section_scores.keys())
    scores = list(section_scores.values())
    
    fig.add_trace(go.Bar(
        x=sections,
        y=scores,
        marker_color=['rgb(75, 192, 192)', 'rgb(255, 205, 86)', 'rgb(255, 99, 132)']
    ))
    
    fig.update_layout(
        yaxis_range=[0, 100],
        height=300,
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)
