"""
Presets Inspector page - Shows active stacked presets + final weights with transparency.
"""

import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Presets Inspector", page_icon="⚙️", layout="wide")

st.sidebar.page_link("app.py", label="← Back to Race Setup", icon="🏇")

st.title("⚙️ Presets Inspector")

# ---------------------------------------------------------------------------
# Current Race Configuration
# ---------------------------------------------------------------------------

st.header("Current Race Configuration")

config_col1, config_col2, config_col3 = st.columns(3)

with config_col1:
    st.markdown(f"**Track:** {st.session_state.get('track_code', 'Not set')}")
    st.markdown(f"**Surface:** {st.session_state.get('surface', 'Not set')}")
    st.markdown(f"**Distance:** {st.session_state.get('distance', 'Not set')} furlongs")

with config_col2:
    st.markdown(f"**Race Type:** {st.session_state.get('race_type', 'Not set')}")
    st.markdown(f"**Condition:** {st.session_state.get('condition', 'Not set')}")
    st.markdown(f"**Weather:** {st.session_state.get('weather', 'Not set')}")

with config_col3:
    st.markdown(f"**Breed:** {st.session_state.get('breed', 'TB')}")
    st.markdown(f"**Date:** {st.session_state.get('race_date', 'Not set')}")
    st.markdown(f"**Race #:** {st.session_state.get('race_number', 'Not set')}")

# ---------------------------------------------------------------------------
# Stacking Log
# ---------------------------------------------------------------------------

st.divider()
st.header("Preset Stacking Order")

stacking_log = st.session_state.get("stacking_log", [])

if not stacking_log:
    st.info("No presets stacked yet. Go to **Race Setup** and click 'Apply Presets' to see the stacking.")
else:
    for entry in stacking_log:
        step_num = entry.get("step", "?")
        preset_name = entry.get("preset", "Unknown")
        detail = entry.get("detail", "")
        multipliers = entry.get("multipliers", {})
        
        mult_text = ""
        if multipliers:
            if "global" in multipliers:
                mult_text = f" (Global multiplier: **{multipliers['global']:.2f}x***)"
            for k, v in multipliers.items():
                if k != "global":
                    mult_text += f"<br>&nbsp;&nbsp;• {k}: **{v:.2f}x**"
        
        st.markdown(f"""
        <div style="background-color:#1e293b;border-left:4px solid #1e88e5;
                     padding:12px 16px;margin:8px 0;border-radius:0 8px 8px 0">
            <strong>{step_num}. {preset_name}</strong>{mult_text}<br>
            <span style="color:#94a3b8;font-size:0.9em">{detail}</span>
        </div>
        """, unsafe_allow_html=True)
    
    st.caption("Stacking order: Track → Surface/Distance → Race Type → Condition → Weather (optional)")

# ---------------------------------------------------------------------------
# Final Weights
# ---------------------------------------------------------------------------

st.divider()
st.header("Final Computed Weights")

final_weights = st.session_state.get("final_weights", {})

if not final_weights:
    st.info("No weights computed yet. Apply presets on the Race Setup page first.")
else:
    # Advanced Override toggle
    override = st.toggle("Advanced Override (Edit Weights)", 
                        value=st.session_state.get("advanced_override", False),
                        key="preset_override_toggle")
    st.session_state.advanced_override = override
    
    # Display weights as a bar chart
    weights_data = []
    base_weights_df = pd.read_csv("presets/base_weights.csv") if pd.io.common.file_exists("presets/base_weights.csv") else pd.DataFrame()
    base_map = {}
    if not base_weights_df.empty:
        base_map = dict(zip(base_weights_df["component"], base_weights_df["weight"]))
    
    for comp, weight in sorted(final_weights.items(), key=lambda x: x[1], reverse=True):
        base_val = base_map.get(comp, weight)
        weights_data.append({
            "Component": comp.replace("_", " ").title(),
            "Final Weight": weight,
            "Base Weight": base_val,
            "Change": weight - base_val,
        })
    
    weights_df = pd.DataFrame(weights_data)
    
    if override:
        st.warning("Editing weights will affect model results. Use with caution.")
        
        edited_weights = {}
        for comp, weight in final_weights.items():
            display_name = comp.replace("_", " ").title()
            new_val = st.number_input(
                display_name,
                value=float(weight),
                min_value=-30.0,
                max_value=50.0,
                step=0.5,
                key=f"override_{comp}"
            )
            edited_weights[comp] = new_val
        
        if st.button("Apply Custom Weights", type="primary"):
            st.session_state.final_weights = edited_weights
            st.session_state.custom_weights = edited_weights
            st.success("Custom weights applied! Re-run the model to see changes.")
            st.rerun()
    else:
        # Chart
        fig = px.bar(
            weights_df,
            x="Final Weight",
            y="Component",
            orientation="h",
            color="Change",
            color_continuous_scale=["#ef4444", "#f59e0b", "#22c55e"],
            color_continuous_midpoint=0,
            text=weights_df["Final Weight"].apply(lambda x: f"{x:.1f}"),
        )
        fig.update_layout(
            height=500,
            showlegend=False,
            yaxis_categoryorder="total ascending",
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Table
        st.dataframe(
            weights_df.style.format({"Final Weight": "{:.1f}", "Base Weight": "{:.1f}", "Change": "{:.1f}"}),
            use_container_width=True,
            hide_index=True,
        )

# ---------------------------------------------------------------------------
# Reset Defaults
# ---------------------------------------------------------------------------

st.divider()

if st.button("Reset to Default Weights", use_container_width=True):
    st.session_state.final_weights = {}
    st.session_state.stacking_log = []
    st.session_state.custom_weights = {}
    st.session_state.advanced_override = False
    st.success("Weights reset to defaults. Re-apply presets to regenerate.")
    st.rerun()

# ---------------------------------------------------------------------------
# Preset Reference Tables
# ---------------------------------------------------------------------------

st.divider()
st.header("Preset Reference Data")

# Track Distance Presets
tab1, tab2, tab3, tab4 = st.tabs(["Track+Distance", "Race Types", "Conditions", "Base Weights"])

with tab1:
    try:
        td_df = pd.read_csv("presets/track_distance.csv")
        if not td_df.empty:
            # Filter to current track if set
            track = st.session_state.get("track_code", "")
            if track:
                td_df = td_df[td_df["track_code"] == track] if track in td_df["track_code"].values else td_df
            st.dataframe(td_df, use_container_width=True, hide_index=True)
        else:
            st.info("No track distance data available.")
    except Exception as e:
        st.error(f"Error loading track distance data: {e}")

with tab2:
    try:
        rt_df = pd.read_csv("presets/race_types.csv")
        if not rt_df.empty:
            st.dataframe(rt_df, use_container_width=True, hide_index=True)
        else:
            st.info("No race type data available.")
    except Exception as e:
        st.error(f"Error loading race type data: {e}")

with tab3:
    try:
        cond_df = pd.read_csv("presets/conditions.csv")
        if not cond_df.empty:
            st.dataframe(cond_df, use_container_width=True, hide_index=True)
        else:
            st.info("No condition data available.")
    except Exception as e:
        st.error(f"Error loading condition data: {e}")

with tab4:
    try:
        bw_df = pd.read_csv("presets/base_weights.csv")
        if not bw_df.empty:
            st.dataframe(bw_df, use_container_width=True, hide_index=True)
        else:
            st.info("No base weight data available.")
    except Exception as e:
        st.error(f"Error loading base weight data: {e}")
