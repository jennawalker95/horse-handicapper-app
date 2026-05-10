"""
Dashboard page - Quick look, rankings, bet/pass recommendation, quick picks.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from model import grading

st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")

# Back to main app link
st.sidebar.page_link("app.py", label="← Back to Race Setup", icon="🏇")

st.title("📊 Dashboard")

# Check if model has been run
if not st.session_state.get("model_run", False) or st.session_state.get("results_df", pd.DataFrame()).empty:
    st.info("No model results yet. Go to **Race Setup** and run the model first.")
    
    # Quick load sample option
    if st.button("Load Sample Race (TB) and Run", use_container_width=True):
        import sys
        sys.path.insert(0, ".")
        from app import load_sample_race, run_model
        load_sample_race("TB")
        run_model()
        st.rerun()
    
    st.stop()

results_df = st.session_state.results_df.copy()
active_df = results_df[~results_df.get("scratched", pd.Series([False] * len(results_df), index=results_df.index))].copy()

# ---------------------------------------------------------------------------
# Quick Picks Section
# ---------------------------------------------------------------------------

st.header("Quick Picks")

qp_col1, qp_col2, qp_col3, qp_col4 = st.columns(4)

# Top Win Pick
top_win = active_df.loc[active_df["power_rank"] == 1].iloc[0] if len(active_df) > 0 else None
with qp_col1:
    with st.container():
        st.markdown("#### ⭐ Top Win Pick")
        if top_win is not None:
            name = top_win.get("horse_name", "?")
            wp = top_win.get("win_probability", 0)
            og = top_win.get("overall_grade", "D")
            color = grading.get_grade_color(og)
            st.markdown(f"**{name}**")
            st.markdown(f"<span style='color:{color};font-size:2em;font-weight:bold'>{og}</span>", unsafe_allow_html=True)
            st.markdown(f"{wp:.0f}% Win | Fair {top_win.get('fair_odds_win', 0):.1f}")
        else:
            st.markdown("N/A")

# Best Value
best_value = active_df[active_df["value_label"] == "Overlay"].nsmallest(1, "value_rank") if len(active_df) > 0 else None
with qp_col2:
    with st.container():
        st.markdown("#### 💰 Best Value")
        if best_value is not None and len(best_value) > 0:
            row = best_value.iloc[0]
            name = row.get("horse_name", "?")
            edge = row.get("edge_percent", 0)
            og = row.get("overall_grade", "D")
            color = grading.get_grade_color(og)
            st.markdown(f"**{name}**")
            st.markdown(f"<span style='color:{color};font-size:2em;font-weight:bold'>{og}</span>", unsafe_allow_html=True)
            st.markdown(f"{edge:+.0f}% Edge | Overlay")
        else:
            st.markdown("No clear overlay")

# Longshot
from model.grading import get_wildcard_label
longshots = []
for _, row in active_df.iterrows():
    label, _ = get_wildcard_label(row)
    if label:
        longshots.append(row)

with qp_col3:
    with st.container():
        st.markdown("#### 🧩 Wildcard/Longshot")
        if longshots:
            ls = longshots[0]
            name = ls.get("horse_name", "?")
            wp = ls.get("win_probability", 0)
            st.markdown(f"**{name}**")
            st.markdown(f"<span style='color:#f59e0b;font-size:1.5em;font-weight:bold'>🧩</span>", unsafe_allow_html=True)
            st.markdown(f"{wp:.0f}% Win | Longshot value")
        else:
            st.markdown("No wildcards detected")

# Safest P/S
safest = active_df.nlargest(1, "show_probability") if len(active_df) > 0 else None
with qp_col4:
    with st.container():
        st.markdown("#### 🎯 Safest P/S")
        if safest is not None and len(safest) > 0:
            row = safest.iloc[0]
            name = row.get("horse_name", "?")
            pp = row.get("place_probability", 0)
            sp = row.get("show_probability", 0)
            st.markdown(f"**{name}**")
            st.markdown(f"<span style='color:#3b82f6;font-size:2em;font-weight:bold'>🎯</span>", unsafe_allow_html=True)
            st.markdown(f"{pp:.0f}% Place | {sp:.0f}% Show")
        else:
            st.markdown("N/A")

st.divider()

# ---------------------------------------------------------------------------
# BET / PASS Box
# ---------------------------------------------------------------------------

st.header("Betting Recommendation")

rec = st.session_state.get("bet_recommendation", "PASS")
rec_conf = st.session_state.get("bet_confidence", 0)
rec_exp = st.session_state.get("bet_explanation", "")
chalk_chaos = st.session_state.get("chalk_chaos", "")
fav_vuln = st.session_state.get("fav_vulnerability", 50)

bet_col1, bet_col2 = st.columns([2, 1])

with bet_col1:
    if rec == "BET":
        st.markdown(
            f"<div style='background-color:#dcfce7;border:3px solid #22c55e;border-radius:12px;"
            f"padding:24px;text-align:center;color:#166534'>"
            f"<h2 style='margin:0'>✅ BET</h2>"
            f"<p style='margin:8px 0;font-size:1.1em'>{rec_exp}</p>"
            f"<p style='margin:0;font-size:0.9em'>Confidence: {rec_conf}%</p></div>",
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f"<div style='background-color:#fee2e2;border:3px solid #ef4444;border-radius:12px;"
            f"padding:24px;text-align:center;color:#991b1b'>"
            f"<h2 style='margin:0'>❌ PASS</h2>"
            f"<p style='margin:8px 0;font-size:1.1em'>{rec_exp}</p>"
            f"<p style='margin:0;font-size:0.9em'>Confidence: {rec_conf}%</p></div>",
            unsafe_allow_html=True
        )

with bet_col2:
    st.metric("Race Confidence", f"{st.session_state.get('race_confidence', 50)}%")
    st.metric("Race Type", chalk_chaos)
    st.metric("Fav Vulnerability", f"{fav_vuln}%")

st.divider()

# ---------------------------------------------------------------------------
# Rankings Table
# ---------------------------------------------------------------------------

st.header("Horse Rankings")

# Prepare display columns
display_df = active_df.copy()
display_df = display_df.sort_values("power_rank")

# Create a clean display table
table_data = []
for _, row in display_df.iterrows():
    wp = row.get("win_probability", 0)
    pp = row.get("place_probability", 0)
    sp = row.get("show_probability", 0)
    if pd.isna(wp): wp = 0
    if pd.isna(pp): pp = 0
    if pd.isna(sp): sp = 0
    
    # Wildcard indicator
    wl_label, _ = get_wildcard_label(row)
    wildcard_icon = "🧩" if wl_label else ""
    
    table_data.append({
        "Rank": int(row.get("power_rank", 99)),
        "Horse": row.get("horse_name", "?"),
        "Post": int(row.get("post_position", 0)),
        "Grade": row.get("overall_grade", "D"),
        "W": row.get("win_grade", "D"),
        "P": row.get("place_grade", "D"),
        "S": row.get("show_grade", "D"),
        "Win%": f"{wp:.1f}%",
        "Fair Odds": f"{row.get('fair_odds_win', 0):.1f}" if not pd.isna(row.get('fair_odds_win')) else "-",
        "ML": f"{row.get('morning_line', 0):.1f}" if not pd.isna(row.get('morning_line')) else "-",
        "Value": row.get("value_label", "?"),
        "Edge": f"{row.get('edge_percent', 0):+.0f}%" if not pd.isna(row.get('edge_percent')) else "-",
        "WC": wildcard_icon,
    })

table_df = pd.DataFrame(table_data)

# Color code the Grade column
def color_grade(val):
    colors = {"A": "color: #22c55e", "B": "color: #3b82f6", "C": "color: #f59e0b", "D": "color: #ef4444"}
    return colors.get(val, "")

styled = table_df.style.applymap(color_grade, subset=["Grade", "W", "P", "S"])
st.dataframe(styled, use_container_width=True, hide_index=True)

# ---------------------------------------------------------------------------
# Quick Look Lines (Beginner Friendly)
# ---------------------------------------------------------------------------

if st.session_state.get("beginner_mode", True):
    st.divider()
    st.header("Quick Look Summaries")
    
    from model.commentary import generate_quick_look
    
    for _, row in display_df.head(5).iterrows():
        ql = generate_quick_look(row)
        
        # Determine card color based on grade
        og = row.get("overall_grade", "D")
        card_colors = {"A": "#166534", "B": "#1e40af", "C": "#92400e", "D": "#991b1b"}
        card_bg = {"A": "#dcfce7", "B": "#dbeafe", "C": "#fef3c7", "D": "#fee2e2"}
        color = card_colors.get(og, "#6b7280")
        bg = card_bg.get(og, "#f3f4f6")
        
        st.markdown(
            f"<div style='background-color:{bg};border-left:4px solid {color};"
            f"padding:12px 16px;margin:8px 0;border-radius:0 8px 8px 0;color:#1f2937'>"
            f"{ql}</div>",
            unsafe_allow_html=True
        )

# ---------------------------------------------------------------------------
# Charts (Advanced Mode)
# ---------------------------------------------------------------------------

if not st.session_state.get("beginner_mode", True):
    st.divider()
    st.header("Visual Analysis")
    
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        # Win probability bar chart
        fig = px.bar(
            display_df.sort_values("win_probability", ascending=True),
            x="win_probability",
            y="horse_name",
            orientation="h",
            title="Win Probability %",
            color="overall_grade",
            color_discrete_map={"A": "#22c55e", "B": "#3b82f6", "C": "#f59e0b", "D": "#ef4444"},
            text=display_df.sort_values("win_probability", ascending=True)["win_probability"].apply(lambda x: f"{x:.1f}%"),
        )
        fig.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with chart_col2:
        # Composite rating chart
        fig2 = px.bar(
            display_df.sort_values("composite_rating", ascending=True),
            x="composite_rating",
            y="horse_name",
            orientation="h",
            title="Composite Power Rating",
            color="overall_grade",
            color_discrete_map={"A": "#22c55e", "B": "#3b82f6", "C": "#f59e0b", "D": "#ef4444"},
            text=display_df.sort_values("composite_rating", ascending=True)["composite_rating"].apply(lambda x: f"{x:.1f}"),
        )
        fig2.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig2, use_container_width=True)

# ---------------------------------------------------------------------------
# Log Result Button
# ---------------------------------------------------------------------------

st.divider()
st.header("Log Result")

with st.form("log_result_form"):
    st.markdown("After the race, enter the actual results to track ROI.")
    
    log_cols = st.columns(3)
    with log_cols[0]:
        result_horse = st.selectbox("Horse", options=active_df["horse_name"].tolist(), key="log_horse")
    with log_cols[1]:
        finish_pos = st.number_input("Finish Position", min_value=1, max_value=20, value=1, key="log_finish")
    with log_cols[2]:
        actual_odds = st.number_input("Actual Odds", min_value=0.0, value=5.0, step=0.5, key="log_odds")
    
    payout_cols = st.columns(3)
    with payout_cols[0]:
        p_win = st.number_input("Win Payout ($)", min_value=0.0, value=0.0, step=0.5, key="log_pwin")
    with payout_cols[1]:
        p_place = st.number_input("Place Payout ($)", min_value=0.0, value=0.0, step=0.5, key="log_pplace")
    with payout_cols[2]:
        p_show = st.number_input("Show Payout ($)", min_value=0.0, value=0.0, step=0.5, key="log_pshow")
    
    submitted = st.form_submit_button("Log Result", use_container_width=True)
    
    if submitted:
        from model import database
        
        horse_row = active_df[active_df["horse_name"] == result_horse].iloc[0]
        
        result_dict = {
            "race_key": f"{st.session_state.track_code}_{st.session_state.race_date}_{st.session_state.race_number}",
            "track_code": st.session_state.track_code,
            "race_date": st.session_state.race_date,
            "race_number": st.session_state.race_number,
            "breed": st.session_state.breed,
            "surface": st.session_state.surface,
            "distance": str(st.session_state.distance),
            "race_type": st.session_state.race_type,
            "condition": st.session_state.condition,
            "horse_name": result_horse,
            "post_position": int(horse_row.get("post_position", 0)),
            "finish_position": finish_pos,
            "win_probability": float(horse_row.get("win_probability", 0)),
            "fair_odds_win": float(horse_row.get("fair_odds_win", 0)),
            "morning_line": float(horse_row.get("morning_line", 0)),
            "actual_odds": actual_odds,
            "payout_win": p_win if finish_pos == 1 else 0,
            "payout_place": p_place if finish_pos <= 2 else 0,
            "payout_show": p_show if finish_pos <= 3 else 0,
            "overall_grade": str(horse_row.get("overall_grade", "D")),
            "value_label": str(horse_row.get("value_label", "")),
            "bet_recommendation": st.session_state.get("bet_recommendation", ""),
        }
        
        database.log_result(result_dict)
        st.success(f"Logged result for {result_horse}!")
