"""
visualization.py
Charts for the Streamlit dashboard: match-score gauge, keyword coverage bar,
and history trend line.
"""

import plotly.graph_objects as go
import matplotlib.pyplot as plt


def match_score_gauge(score: float):
    """Gauge chart (0-100) showing overall resume-to-job match score."""
    color = "#e74c3c" if score < 40 else "#f39c12" if score < 70 else "#27ae60"

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        number={"suffix": "%"},
        title={"text": "Resume Match Score"},
        gauge={
            "axis": {"range": [0, 100]},
            "bar": {"color": color},
            "steps": [
                {"range": [0, 40], "color": "#fdecea"},
                {"range": [40, 70], "color": "#fef5e7"},
                {"range": [70, 100], "color": "#eafaf1"},
            ],
        },
    ))
    fig.update_layout(height=300, margin=dict(l=20, r=20, t=50, b=20))
    return fig


def keyword_coverage_bar(matched_count: int, missing_count: int):
    """Bar chart comparing matched vs missing keywords."""
    fig = go.Figure(data=[
        go.Bar(
            x=["Matched Keywords", "Missing Keywords"],
            y=[matched_count, missing_count],
            marker_color=["#27ae60", "#e74c3c"],
            text=[matched_count, missing_count],
            textposition="auto",
        )
    ])
    fig.update_layout(
        title="Keyword Coverage",
        height=320,
        margin=dict(l=20, r=20, t=50, b=20),
        yaxis_title="Count",
    )
    return fig


def history_trend_line(history: list[dict]):
    """
    Line chart of match scores over time from a user's analysis history.
    `history` is a list of dicts with 'created_at' and 'match_score' keys,
    most-recent-first (as returned by database.get_user_history).
    """
    if not history:
        return None

    ordered = list(reversed(history))
    dates = [h["created_at"][:10] for h in ordered]
    scores = [h["match_score"] for h in ordered]

    fig = go.Figure(data=go.Scatter(
        x=dates, y=scores, mode="lines+markers",
        line=dict(color="#3498db", width=2),
        marker=dict(size=8),
    ))
    fig.update_layout(
        title="Match Score History",
        height=320,
        margin=dict(l=20, r=20, t=50, b=20),
        yaxis_title="Match Score (%)",
        xaxis_title="Date",
        yaxis_range=[0, 100],
    )
    return fig


def keyword_wordcloud_fallback(keywords: list[str], filename: str = "data/keywords.png"):
    """
    Simple matplotlib bar rendering of top keywords as a static image
    fallback, useful for embedding in exported PDF reports.
    """
    top = keywords[:15]
    if not top:
        return None

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.barh(top[::-1], range(len(top), 0, -1), color="#3498db")
    ax.set_title("Top Keywords")
    ax.set_xlabel("Relevance rank")
    fig.tight_layout()
    fig.savefig(filename, dpi=120)
    plt.close(fig)
    return filename
