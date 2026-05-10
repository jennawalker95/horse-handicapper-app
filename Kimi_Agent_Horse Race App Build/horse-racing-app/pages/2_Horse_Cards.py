"""
Horse Cards page - Detailed per-horse analysis with commentary.
"""

import streamlit as st
import pandas as pd
from model import grading, commentary

st.set_page_config(page_title="Horse Cards", page_icon="🐴", layout="wide")

st.sidebar.page_link("app.py", label="← Back to Race Setup", icon="🏇")

st.title("🐴 Horse Cards")

if not st.session_state.get("model_run", False) or st.session_state.get("results_df", pd.DataFrame()).empty:
    st.info("No model results yet. Go to **Race Setup** and run the model first.")
    st.stop()

results_df = st.session_state.results_df.copy()
active_df = results_df[~results_df.get("scratched", pd.Series([False] * len(results_df), index=results_df.index))].copy()

# Horse selector
horse_names = active_df.sort_values("power_rank")["horse_name"].tolist()
selected = st.selectbox("Select Horse", options=horse_names, key="horse_select")

if not selected:
    st.stop()

horse = active_df[active_df["horse_name"] == selected].iloc[0]

# ---------------------------------------------------------------------------
# Horse Header
# ---------------------------------------------------------------------------

og = horse.get("overall_grade", "D")
grade_color = grading.get_grade_color(og)
grade_bg = grading.get_grade_bg_color(og)

st.markdown(f"""
<div style="background-color:#1e293b;border-radius:12px;padding:24px;margin-bottom:20px;">
    <div style="display:flex;align-items:center;gap:16px;flex-wrap:wrap">
        <h2 style="margin:0;color:#f8fafc">#{int(horse.get('power_rank', 0))} {selected}</h2>
        <span style="background-color:{grade_bg};color:{grade_color};padding:6px 16px;
                     border-radius:8px;font-size:1.5em;font-weight:bold;border:2px solid {grade_color}">
            {og}
        </span>
        <span style="color:#94a3b8;font-size:1.1em">Post {int(horse.get('post_position', 0))}</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Key Metrics Row
# ---------------------------------------------------------------------------

mc1, mc2, mc3, mc4, mc5, mc6 = st.columns(6)

wp = horse.get("win_probability", 0)
pp = horse.get("place_probability", 0)
sp = horse.get("show_probability", 0)
if pd.isna(wp): wp = 0
if pd.isna(pp): pp = 0
if pd.isna(sp): sp = 0

with mc1:
    st.metric("Win %", f"{wp:.1f}%")
with mc2:
    st.metric("Place %", f"{pp:.1f}%")
with mc3:
    st.metric("Show %", f"{sp:.1f}%")
with mc4:
    st.metric("Fair Odds", f"{horse.get('fair_odds_win', 0):.1f}" if not pd.isna(horse.get('fair_odds_win')) else "-")
with mc5:
    st.metric("Morning Line", f"{horse.get('morning_line', 0):.1f}" if not pd.isna(horse.get('morning_line')) else "-")
with mc6:
    vl = str(horse.get("value_label", "?"))
    edge = horse.get("edge_percent", 0)
    if pd.isna(edge): edge = 0
    
    val_color = {"Overlay": "#22c55e", "Underlay": "#ef4444", "Fair": "#3b82f6", "Unknown": "#6b7280"}
    st.markdown(f"""
    <div style="text-align:center">
        <div style="font-size:0.85em;color:#94a3b8">Value</div>
        <div style="font-size:1.3em;font-weight:bold;color:{val_color.get(vl, '#6b7280')}">{vl}</div>
        <div style="font-size:0.9em;color:#94a3b8">{edge:+.0f}% edge</div>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# ---------------------------------------------------------------------------
# Grades Section
# ---------------------------------------------------------------------------

st.header("Grades")

g_col1, g_col2, g_col3, g_col4 = st.columns(4)

grades = [
    ("Overall", og),
    ("Win", horse.get("win_grade", "D")),
    ("Place", horse.get("place_grade", "D")),
    ("Show", horse.get("show_grade", "D")),
]

for col, (name, grade) in zip([g_col1, g_col2, g_col3, g_col4], grades):
    with col:
        color = grading.get_grade_color(grade)
        bg = grading.get_grade_bg_color(grade)
        st.markdown(f"""
        <div style="background-color:{bg};border:2px solid {color};border-radius:10px;
                     padding:16px;text-align:center">
            <div style="font-size:0.85em;color:#64748b;text-transform:uppercase">{name}</div>
            <div style="font-size:2.5em;font-weight:bold;color:{color}">{grade}</div>
        </div>
        """, unsafe_allow_html=True)

st.divider()

# ---------------------------------------------------------------------------
# Commentary (Why Chosen / Why Not)
# ---------------------------------------------------------------------------

st.header("Analysis")

commentary_data = commentary.generate_commentary(horse, active_df)

st.markdown("#### ✅ Strengths")
for strength in commentary_data["strengths"]:
    st.markdown(f"<div style='color:#22c55e;margin:4px 0'>+ {strength}</div>", unsafe_allow_html=True)

st.markdown("#### ⚠️ Weaknesses / Concerns")
for weakness in commentary_data["weaknesses"]:
    st.markdown(f"<div style='color:#ef4444;margin:4px 0'>- {weakness}</div>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Wildcard / Longshot Analysis
# ---------------------------------------------------------------------------

from model.grading import get_wildcard_label

wl_label, wl_reasons = get_wildcard_label(horse)

if wl_label:
    st.divider()
    st.header(f"🧩 {wl_label}")
    
    ls_analysis = commentary.generate_longshot_analysis(horse)
    
    st.markdown("**Why Dangerous:**")
    for reason in ls_analysis["why_dangerous"]:
        st.markdown(f"- {reason}")
    
    st.markdown("**What Must Happen:**")
    for scenario in ls_analysis["what_must_happen"]:
        st.markdown(f"- {scenario}")
    
    st.markdown(f"**Best Usage:** {ls_analysis['best_usage']}")

# ---------------------------------------------------------------------------
# Component Breakdown (Advanced Mode)
# ---------------------------------------------------------------------------

if not st.session_state.get("beginner_mode", True):
    st.divider()
    st.header("Component Breakdown")
    
    breakdown = horse.get("component_breakdown", {})
    
    if breakdown:
        comp_data = []
        for comp, score in breakdown.items():
            if isinstance(score, (int, float)):
                comp_data.append({"Component": comp, "Score": score})
        
        if comp_data:
            comp_df = pd.DataFrame(comp_data).sort_values("Score", ascending=True)
            
            fig = go.Figure(go.Bar(
                x=comp_df["Score"],
                y=comp_df["Component"],
                orientation="h",
                marker_color=comp_df["Score"].apply(
                    lambda x: "#22c55e" if x >= 70 else ("#3b82f6" if x >= 55 else "#f59e0b" if x >= 40 else "#ef4444")
                ),
                text=comp_df["Score"].apply(lambda x: f"{x:.0f}"),
                textposition="outside",
            ))
            fig.update_layout(
                title="Component Scores (0-100)",
                xaxis_range=[0, 100],
                height=350,
                showlegend=False,
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Connections / Intent Flags
    st.subheader("Connections & Intent")
    flags = horse.get("intent_flags", ["No signals"])
    if isinstance(flags, list):
        for flag in flags:
            st.markdown(f"- {flag}")
    
    # Pace Scenario
    st.subheader("Pace Projection")
    scenario = horse.get("pace_scenario", "Unknown")
    st.info(f"**Pace Scenario:** {scenario}")
    
    st.markdown(f"- Early Pace: {horse.get('early_pace_norm', 50):.0f}/100")
    st.markdown(f"- Late Pace: {horse.get('late_pace_norm', 50):.0f}/100")
    st.markdown(f"- Energy Distribution: {horse.get('energy_distribution', 50):.0f}% early")
    st.markdown(f"- Layoff Factor: {horse.get('layoff_factor', 0):+.0f}")
    st.markdown(f"- Bounce Risk: {'Yes' if horse.get('bounce_flag', False) else 'No'}")

# ---------------------------------------------------------------------------
# Raw Data Table
# ---------------------------------------------------------------------------

with st.expander("View All Raw Data for This Horse"):
    # Select key columns to display
    raw_cols = [c for c in active_df.columns if c not in ['scratched', 'component_breakdown', 'intent_flags']]
    horse_data = horse[raw_cols] if isinstance(horse, pd.Series) else horse[[c for c in raw_cols if c in horse.columns]]
    st.dataframe(horse_data.to_frame().T if isinstance(horse_data, pd.Series) else horse_data.to_frame().T, use_container_width=True)
