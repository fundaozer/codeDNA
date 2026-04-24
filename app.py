import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from predict import predict

st.set_page_config(page_title="CodeDNA", page_icon="🧬", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background: linear-gradient(135deg, #ede9fe 0%, #dbeafe 50%, #e0f2fe 100%);
    color: #1a1a2e;
}

.stButton > button {
    background: linear-gradient(135deg, #6c63ff, #48cae4);
    color: white;
    font-weight: 600;
    border: none;
    border-radius: 10px;
    padding: 0.6rem 2rem;
    width: 100%;
    transition: opacity 0.2s;
}
.stButton > button:hover { opacity: 0.85; }

.stTextInput > div > div > input {
    background: #f5f3ff;
    color: #1a1a2e;
    border: 1.5px solid #d8ddf0;
    border-radius: 10px;
    padding: 0.6rem 1rem;
    font-family: 'Inter', sans-serif;
}
.stTextInput > div > div > input:focus {
    border-color: #6c63ff;
    box-shadow: 0 0 0 3px rgba(108,99,255,0.1);
}

[data-testid="metric-container"] {
    background: #f5f3ff;
    border: 1px solid #e8ecf8;
    border-radius: 12px;
    padding: 1.2rem;
    box-shadow: 0 2px 12px rgba(108,99,255,0.08);
}

.header-card {
    background: linear-gradient(135deg, #6c63ff20, #48cae420);
    border: 1px solid #e8ecf8;
    border-radius: 16px;
    padding: 2.5rem;
    text-align: center;
    margin-bottom: 1.5rem;
}

.section-label {
    color: #9aa5c4;
    font-size: 0.72rem;
    letter-spacing: 3px;
    text-transform: uppercase;
    margin-bottom: 0.8rem;
    font-weight: 600;
}

.chart-card {
    background: #f5f3ff;
    border: 1px solid #e8ecf8;
    border-radius: 14px;
    padding: 1.2rem;
    box-shadow: 0 2px 12px rgba(108,99,255,0.06);
}

.block-container { padding-top: 2rem !important; }
#MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ── Header card ──
st.markdown("""
<div class="header-card">
    <h1 style='color:#6c63ff; margin:0; font-size:2.8rem'>🧬 CodeDNA</h1>
    <p style='color:#9aa5c4; letter-spacing:4px; font-size:0.8rem; margin-top:0.5rem'>
        AI · DEVELOPER PERSONALITY ANALYZER
    </p>
</div>
""", unsafe_allow_html=True)

# ── Url input and analyze  ──
c_in, c_btn = st.columns([4, 1])
with c_in:
    url = st.text_input("", placeholder="https://github.com/owner/repo", label_visibility="collapsed")
with c_btn:
    st.write("")
    btn = st.button("⚡ Analyze")

if btn and url:
    with st.spinner("Analyzing..."):
        r = predict(url)

    if not r:
        st.error("Repository not found.")
        st.stop()

    feat  = r["features"]
    level = r["level"]
    color_map = {"junior": "#ff6b6b", "mid": "#f5a623", "senior": "#6c63ff"}
    lcolor = color_map.get(level, "#6c63ff")

    st.markdown("---")

    # ── User profile header card  ──
    st.markdown(f"""
    <div style='background:#f5f3ff; border:1px solid #e8ecf8; border-radius:12px;
                padding:1.2rem 1.5rem; margin-bottom:1rem;
                box-shadow:0 2px 12px rgba(108,99,255,0.06)'>
        <span style='font-size:1.3rem; font-weight:700; color:{lcolor}'>
            👤 {r['username']}
        </span>
        <span style='margin-left:1rem; background:{lcolor}22; color:{lcolor};
                     padding:0.2rem 0.8rem; border-radius:20px; font-size:0.85rem; font-weight:600'>
            {level.upper()}
        </span>
    </div>
    """, unsafe_allow_html=True)

    # ── Metric Cards ──
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("🎯 Level",  r["level"].upper())
    m2.metric("✅ Confidence",   f"{r['confidence']:.0%}")
    m3.metric("📝 Commits", feat["total_commits"])
    m4.metric("⚠️ Risk",    f"{r['risk']:+.2f}")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Chart Section  ──
    g1, g2 = st.columns(2)

    PLOT_BG = "#f5f3ff"
    GRID    = "#e8ecf8"
    FONT    = "#1a1a2e"

    with g1:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-label">// Probability Distribution</div>', unsafe_allow_html=True)
        fig = go.Figure(go.Bar(
            x=["Junior", "Mid", "Senior"],
            y=[r["proba"].get("junior",0), r["proba"].get("mid",0), r["proba"].get("senior",0)],
            marker_color=["#ff6b6b", "#f5a623", "#6c63ff"],
            marker_line_width=0,
            text=[f"{v:.0%}" for v in [r["proba"].get("junior",0), r["proba"].get("mid",0), r["proba"].get("senior",0)]],
            textposition="outside",
            textfont=dict(color=FONT, size=13)
        ))
        fig.update_layout(
            paper_bgcolor=PLOT_BG, plot_bgcolor=PLOT_BG,
            font=dict(color=FONT, family="Inter"),
            yaxis=dict(range=[0,1.15], tickformat=".0%", gridcolor=GRID, zeroline=False),
            xaxis=dict(gridcolor=GRID),
            height=280, margin=dict(t=10, b=10, l=10, r=10)
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with g2:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-label">// Skill Radar</div>', unsafe_allow_html=True)
        cats = ["Commit Hygiene", "Community", "Seniority",
                "Test Culture", "Consistency", "Output"]
        vals = [
            min(feat["avg_commit_msg_length"] / 80, 1),
            min(feat["followers"] / 500, 1),
            r["proba"].get("senior", 0),
            float(feat["has_tests"]),
            1 - feat["night_commit_ratio"],
            min(feat["public_repos"] / 100, 1),
        ]
        fig2 = go.Figure(go.Scatterpolar(
            r=vals + [vals[0]], theta=cats + [cats[0]],
            fill="toself",
            fillcolor="rgba(108,99,255,0.08)",
            line=dict(color="#6c63ff", width=2)
        ))
        fig2.update_layout(
            polar=dict(
                bgcolor=PLOT_BG,
                radialaxis=dict(visible=True, range=[0,1],
                                gridcolor=GRID, tickfont=dict(color="#9aa5c4", size=8)),
                angularaxis=dict(gridcolor=GRID, tickfont=dict(color=FONT, size=10))
            ),
            paper_bgcolor=PLOT_BG,
            font=dict(color=FONT, family="Inter"),
            height=280, margin=dict(t=10, b=10, l=10, r=10)
        )
        st.plotly_chart(fig2, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Raw metrics ──
    st.markdown('<div class="section-label">// Raw Metrics</div>', unsafe_allow_html=True)
    df = pd.DataFrame([feat]).T.reset_index()
    df.columns = ["Metric", "Value"]
    st.dataframe(df, use_container_width=True, hide_index=True, height=420)

elif btn and not url:
    st.warning("Please enter a GitHub repository URL.")

else:
    st.markdown("""
    <div style='text-align:center; padding:4rem 0; color:#9aa5c4'>
        <div style='font-size:2rem; margin-bottom:1rem'>⬆</div>
        <div style='font-size:1rem; letter-spacing:2px; font-weight:600; color:#6c63ff'>
            ENTER A GITHUB REPO URL AND ANALYZE
        </div>
        <div style='font-size:0.85rem; margin-top:0.5rem'>
            example: https://github.com/torvalds/linux
        </div>
    </div>
    """, unsafe_allow_html=True)

