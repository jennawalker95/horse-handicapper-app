"""
Results and ROI page - Results entry, ROI dashboards, performance analytics.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from model import database

st.set_page_config(page_title="Results & ROI", page_icon="📈", layout="wide")

st.sidebar.page_link("app.py", label="← Back to Race Setup", icon="🏇")

st.title("📈 Results & ROI")

# ---------------------------------------------------------------------------
# Results Entry Section
# ---------------------------------------------------------------------------

st.header("Log Race Result")

with st.form("manual_result_entry"):
    st.markdown("Manually log a race result for ROI tracking.")
    
    r_col1, r_col2, r_col3 = st.columns(3)
    
    with r_col1:
        r_track = st.text_input("Track Code", value=st.session_state.get("track_code", ""), key="r_track")
        r_date = st.date_input("Race Date", value=pd.Timestamp("today"), key="r_date")
        r_num = st.number_input("Race #", min_value=1, max_value=20, value=1, key="r_num")
    
    with r_col2:
        r_horse = st.text_input("Horse Name", key="r_horse")
        r_finish = st.number_input("Finish Position", min_value=1, max_value=20, value=1, key="r_finish")
        r_odds = st.number_input("Actual Odds", min_value=0.0, value=5.0, step=0.5, key="r_odds")
    
    with r_col3:
        r_pwin = st.number_input("Win Payout ($)", min_value=0.0, value=0.0, step=0.5, key="r_pwin")
        r_pplace = st.number_input("Place Payout ($)", min_value=0.0, value=0.0, step=0.5, key="r_pplace")
        r_pshow = st.number_input("Show Payout ($)", min_value=0.0, value=0.0, step=0.5, key="r_pshow")
    
    # Optional fields
    with st.expander("Optional Details"):
        o_col1, o_col2, o_col3 = st.columns(3)
        with o_col1:
            r_surface = st.selectbox("Surface", ["", "Dirt", "Turf", "Tapeta", "Synthetic"], key="r_surface")
            r_breed = st.selectbox("Breed", ["", "TB", "QH"], key="r_breed")
        with o_col2:
            r_distance = st.text_input("Distance", placeholder="e.g. 6F, 1M", key="r_distance")
            r_type = st.text_input("Race Type", placeholder="e.g. STK, CLM", key="r_type")
        with o_col3:
            r_cond = st.text_input("Condition", key="r_cond")
            r_ml = st.number_input("Morning Line", min_value=0.0, value=0.0, step=0.5, key="r_ml")
    
    submitted = st.form_submit_button("Log Result", use_container_width=True)
    
    if submitted:
        if not r_horse.strip():
            st.error("Horse name is required!")
        else:
            result_dict = {
                "race_key": f"{r_track}_{r_date.strftime('%Y-%m-%d')}_{r_num}",
                "track_code": r_track,
                "race_date": r_date.strftime("%Y-%m-%d"),
                "race_number": r_num,
                "breed": r_breed,
                "surface": r_surface,
                "distance": r_distance,
                "race_type": r_type,
                "condition": r_cond,
                "horse_name": r_horse.strip(),
                "post_position": 0,
                "finish_position": r_finish,
                "win_probability": 0,
                "fair_odds_win": 0,
                "morning_line": r_ml,
                "actual_odds": r_odds,
                "payout_win": r_pwin if r_finish == 1 else 0,
                "payout_place": r_pplace if r_finish <= 2 else 0,
                "payout_show": r_pshow if r_finish <= 3 else 0,
                "overall_grade": "",
                "value_label": "",
                "bet_recommendation": "",
            }
            database.log_result(result_dict)
            st.success(f"Logged result for {r_horse}!")

st.divider()

# ---------------------------------------------------------------------------
# Results History
# ---------------------------------------------------------------------------

st.header("Results History")

results_df = database.get_all_results()

if results_df.empty:
    st.info("No results logged yet. Use the form above or log from the Dashboard.")
else:
    # Display results table
    display_cols = ["race_date", "track_code", "race_number", "horse_name", 
                   "finish_position", "actual_odds", "payout_win", "payout_place", "payout_show"]
    available_cols = [c for c in display_cols if c in results_df.columns]
    
    st.dataframe(results_df[available_cols], use_container_width=True, hide_index=True)
    
    # Export
    csv = results_df.to_csv(index=False)
    st.download_button(
        "Export All Results (CSV)",
        data=csv,
        file_name="race_results.csv",
        mime="text/csv",
    )
    
    # Delete option
    if len(results_df) > 0:
        del_id = st.selectbox("Select result to delete", 
                             options=results_df["id"].tolist(),
                             format_func=lambda x: f"ID {x}: {results_df[results_df['id']==x].iloc[0]['horse_name']} on {results_df[results_df['id']==x].iloc[0]['race_date']}",
                             key="del_select")
        if st.button("Delete Selected Result"):
            database.delete_result(del_id)
            st.success("Result deleted!")
            st.rerun()

st.divider()

# ---------------------------------------------------------------------------
# ROI Dashboards
# ---------------------------------------------------------------------------

st.header("Performance Dashboards")

if results_df.empty:
    st.info("No data for ROI analysis. Log some results first.")
else:
    # Calculate overall stats
    total_bets = len(results_df)
    wins = (results_df["finish_position"] == 1).sum()
    places = (results_df["finish_position"] <= 2).sum()
    shows = (results_df["finish_position"] <= 3).sum()
    
    total_staked = total_bets * 2.0  # $2 base bet
    total_return = results_df["payout_win"].fillna(0).sum() + results_df["payout_place"].fillna(0).sum() + results_df["payout_show"].fillna(0).sum()
    roi_pct = round((total_return - total_staked) / total_staked * 100, 1) if total_staked > 0 else 0
    
    # Summary metrics
    m1, m2, m3, m4, m5 = st.columns(5)
    with m1:
        st.metric("Total Bets", total_bets)
    with m2:
        st.metric("ROI %", f"{roi_pct:+.1f}%", delta=f"${total_return - total_staked:.2f} net")
    with m3:
        st.metric("Win Rate", f"{wins/total_bets*100:.1f}%" if total_bets > 0 else "0%")
    with m4:
        st.metric("Place Rate", f"{places/total_bets*100:.1f}%" if total_bets > 0 else "0%")
    with m5:
        st.metric("Show Rate", f"{shows/total_bets*100:.1f}%" if total_bets > 0 else "0%")
    
    # ROI by category tabs
    st.subheader("ROI Breakdown")
    
    roi_tab1, roi_tab2, roi_tab3, roi_tab4 = st.tabs(["By Track", "By Surface", "By Race Type", "By Condition"])
    
    categories = [
        (roi_tab1, "track_code", "Track"),
        (roi_tab2, "surface", "Surface"),
        (roi_tab3, "race_type", "Race Type"),
        (roi_tab4, "condition", "Condition"),
    ]
    
    for tab, cat_col, cat_name in categories:
        with tab:
            if cat_col in results_df.columns:
                # Group by category
                grouped = results_df[results_df[cat_col].notna()].groupby(cat_col).agg({
                    "finish_position": "count",
                    "payout_win": "sum",
                    "payout_place": "sum",
                    "payout_show": "sum",
                }).reset_index()
                grouped.columns = [cat_name, "Bets", "Win $", "Place $", "Show $"]
                grouped["Total $"] = grouped["Win $"] + grouped["Place $"] + grouped["Show $"]
                grouped["Staked $"] = grouped["Bets"] * 2
                grouped["ROI %"] = ((grouped["Total $"] - grouped["Staked $"]) / grouped["Staked $"] * 100).round(1)
                grouped["Wins"] = results_df[results_df[cat_col].notna()].groupby(cat_col).apply(
                    lambda x: (x["finish_position"] == 1).sum()
                ).values
                grouped["Win Rate"] = (grouped["Wins"] / grouped["Bets"] * 100).round(1)
                
                if not grouped.empty:
                    # Bar chart
                    fig = px.bar(
                        grouped,
                        x=cat_name,
                        y="ROI %",
                        color="ROI %",
                        color_continuous_scale=["#ef4444", "#f59e0b", "#22c55e"],
                        color_continuous_midpoint=0,
                        text=grouped["ROI %"].apply(lambda x: f"{x:+.1f}%"),
                    )
                    fig.update_layout(height=400, showlegend=False)
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Table
                    st.dataframe(
                        grouped[[cat_name, "Bets", "Wins", "Win Rate", "ROI %", "Total $"]],
                        use_container_width=True,
                        hide_index=True,
                    )
                else:
                    st.info(f"No data available for {cat_name} breakdown.")
    
    # Cumulative ROI chart
    st.subheader("Cumulative Performance")
    
    results_sorted = results_df.sort_values("race_date")
    results_sorted["staked"] = 2.0
    results_sorted["returned"] = results_sorted["payout_win"].fillna(0) + results_sorted["payout_place"].fillna(0) + results_sorted["payout_show"].fillna(0)
    results_sorted["cumulative_staked"] = results_sorted["staked"].cumsum()
    results_sorted["cumulative_returned"] = results_sorted["returned"].cumsum()
    results_sorted["cumulative_roi"] = ((results_sorted["cumulative_returned"] - results_sorted["cumulative_staked"]) / results_sorted["cumulative_staked"] * 100).round(1)
    
    fig_cum = go.Figure()
    fig_cum.add_trace(go.Scatter(
        x=results_sorted["race_date"],
        y=results_sorted["cumulative_roi"],
        mode="lines+markers",
        name="Cumulative ROI %",
        line=dict(color="#1e88e5", width=2),
        fill="tonexty",
        fillcolor="rgba(30, 136, 229, 0.1)",
    ))
    fig_cum.add_hline(y=0, line_dash="dash", line_color="#ef4444")
    fig_cum.update_layout(
        title="Cumulative ROI Over Time",
        xaxis_title="Date",
        yaxis_title="ROI %",
        height=400,
        showlegend=False,
    )
    st.plotly_chart(fig_cum, use_container_width=True)
