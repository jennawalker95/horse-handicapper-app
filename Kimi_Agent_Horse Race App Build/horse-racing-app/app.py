"""
app.py - Main entry point for the Pro Elite Horse Race Handicapping App.
Handles navigation, sidebar setup, session state initialization, and workflow.
"""

import streamlit as st
import pandas as pd
from model import presets, database

# Must be first Streamlit call
st.set_page_config(
    page_title="Pro Elite Handicapper",
    page_icon="🏇",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize database
database.init_db()

# ---------------------------------------------------------------------------
# Session state defaults
# ---------------------------------------------------------------------------

def init_session_state():
    defaults = {
        # Workflow
        "workflow_step": 1,
        "beginner_mode": True,
        "model_run": False,
        
        # Race header
        "track_code": "SAR",
        "race_date": pd.Timestamp("today").strftime("%Y-%m-%d"),
        "race_number": 1,
        "breed": "TB",
        "surface": "Dirt",
        "distance": 8.0,
        "race_type": "STK",
        "condition": "D-FAST",
        "weather": "CLEAR",
        
        # Horses data (DataFrame)
        "horses_df": pd.DataFrame(),
        
        # Model results
        "results_df": pd.DataFrame(),
        "stacking_log": [],
        "final_weights": {},
        "race_confidence": 50,
        "bet_recommendation": "",
        "bet_confidence": 0,
        "bet_explanation": "",
        "chalk_chaos": "",
        "fav_vulnerability": 50,
        
        # Preset overrides
        "advanced_override": False,
        "custom_weights": {},
        
        # Selected horse for detail view
        "selected_horse": None,
        
        # Min edge threshold
        "min_edge": 10,
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


init_session_state()

# ---------------------------------------------------------------------------
# Custom CSS
# ---------------------------------------------------------------------------

def load_css():
    st.markdown("""
    <style>
    /* Grade badges */
    .grade-A { background-color: #dcfce7; color: #166534; padding: 4px 12px; 
               border-radius: 6px; font-weight: bold; border: 2px solid #22c55e; }
    .grade-B { background-color: #dbeafe; color: #1e40af; padding: 4px 12px; 
               border-radius: 6px; font-weight: bold; border: 2px solid #3b82f6; }
    .grade-C { background-color: #fef3c7; color: #92400e; padding: 4px 12px; 
               border-radius: 6px; font-weight: bold; border: 2px solid #f59e0b; }
    .grade-D { background-color: #fee2e2; color: #991b1b; padding: 4px 12px; 
               border-radius: 6px; font-weight: bold; border: 2px solid #ef4444; }
    
    /* Value labels */
    .value-overlay { background-color: #dcfce7; color: #166534; padding: 2px 8px; 
                     border-radius: 4px; font-size: 0.9em; }
    .value-underlay { background-color: #fee2e2; color: #991b1b; padding: 2px 8px; 
                      border-radius: 4px; font-size: 0.9em; }
    .value-fair { background-color: #dbeafe; color: #1e40af; padding: 2px 8px; 
                  border-radius: 4px; font-size: 0.9em; }
    
    /* Metric cards */
    .metric-card {
        background-color: #1e293b;
        border-radius: 10px;
        padding: 16px;
        border: 1px solid #334155;
        margin-bottom: 12px;
    }
    .metric-card h4 {
        color: #94a3b8;
        margin: 0 0 8px 0;
        font-size: 0.85em;
        text-transform: uppercase;
    }
    .metric-card .value {
        color: #f8fafc;
        font-size: 1.8em;
        font-weight: bold;
        margin: 0;
    }
    
    /* Section headers */
    .section-header {
        color: #f8fafc;
        border-bottom: 2px solid #1e88e5;
        padding-bottom: 8px;
        margin: 24px 0 16px 0;
    }
    
    /* Horse card */
    .horse-card {
        background-color: #1e293b;
        border-radius: 12px;
        padding: 20px;
        border: 1px solid #334155;
        margin-bottom: 16px;
    }
    
    /* Commentary box */
    .commentary-box {
        background-color: #0f172a;
        border-left: 4px solid #1e88e5;
        padding: 12px 16px;
        margin: 8px 0;
        border-radius: 0 8px 8px 0;
    }
    
    /* Quick pick card */
    .quick-pick {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border-radius: 12px;
        padding: 16px;
        border: 1px solid #334155;
        margin-bottom: 12px;
    }
    
    /* BET/PASS box */
    .bet-box {
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        margin: 16px 0;
    }
    .bet-box.bet {
        background-color: #dcfce7;
        border: 2px solid #22c55e;
        color: #166534;
    }
    .bet-box.pass {
        background-color: #fee2e2;
        border: 2px solid #ef4444;
        color: #991b1b;
    }
    </style>
    """, unsafe_allow_html=True)


load_css()

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

def render_sidebar():
    with st.sidebar:
        st.title("🏇 Pro Elite Handicapper")
        
        # Beginner/Advanced toggle
        st.session_state.beginner_mode = st.toggle(
            "Beginner Mode", 
            value=st.session_state.beginner_mode,
            help="Beginner mode shows simplified views. Advanced reveals full breakdowns."
        )
        
        st.divider()
        
        # Workflow steps
        st.subheader("Workflow")
        
        steps = [
            "1) Race Setup",
            "2) Horse/PP Input", 
            "3) Run Model",
            "4) Review",
            "5) Log Results",
        ]
        
        for i, step in enumerate(steps, 1):
            if i == st.session_state.workflow_step:
                st.markdown(f"**→ {step}**")
            else:
                st.markdown(f"<span style='color:#64748b'>{step}</span>", unsafe_allow_html=True)
        
        st.divider()
        
        # Quick links
        st.subheader("Quick Links")
        st.page_link("pages/1_Dashboard.py", label="Dashboard", icon="📊")
        st.page_link("pages/2_Horse_Cards.py", label="Horse Cards", icon="🐴")
        st.page_link("pages/3_Presets_Inspector.py", label="Presets Inspector", icon="⚙️")
        st.page_link("pages/4_Results_and_ROI.py", label="Results & ROI", icon="📈")
        st.page_link("pages/5_How_To_Use.py", label="How To Use", icon="📖")
        st.page_link("pages/6_FAQ_Troubleshooting.py", label="FAQ & Troubleshooting", icon="🔧")
        st.page_link("pages/7_Acronyms_Definitions.py", label="Acronyms & Definitions", icon="📚")


render_sidebar()

# ---------------------------------------------------------------------------
# Main page (Race Setup)
# ---------------------------------------------------------------------------

def main():
    st.title("🏇 Race Setup")
    st.markdown("Configure your race and enter horse data to begin analysis.")
    
    # Race Setup Section
    st.header("Race Information")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Track selection
        track_options = presets.get_track_display_names()
        track_codes = list(track_options.keys())
        current_track = st.session_state.track_code
        if current_track in track_codes:
            track_idx = track_codes.index(current_track)
        else:
            track_idx = 0
        
        selected_track = st.selectbox(
            "Track",
            options=track_codes,
            format_func=lambda x: track_options.get(x, x),
            index=track_idx,
            key="sb_track"
        )
        st.session_state.track_code = selected_track
        
        # Get track info for auto breed
        track_info = presets.get_track_info(selected_track)
        if track_info:
            auto_breed = track_info.get("breed", "TB")
        else:
            auto_breed = "TB"
        
        # Breed (auto from track, editable)
        breed_options = ["TB", "QH", "TB/QH"]
        breed_idx = breed_options.index(auto_breed) if auto_breed in breed_options else 0
        selected_breed = st.selectbox(
            "Breed",
            options=breed_options,
            index=breed_idx,
            key="sb_breed"
        )
        st.session_state.breed = selected_breed
    
    with col2:
        # Surface
        surface_options = ["Dirt", "Turf", "Tapeta", "Synthetic"]
        surf_idx = surface_options.index(st.session_state.surface) if st.session_state.surface in surface_options else 0
        selected_surface = st.selectbox(
            "Surface",
            options=surface_options,
            index=surf_idx,
            key="sb_surface"
        )
        st.session_state.surface = selected_surface
        
        # Distance
        selected_distance = st.number_input(
            "Distance (furlongs)",
            min_value=0.5,
            max_value=20.0,
            value=float(st.session_state.distance),
            step=0.5,
            key="sb_distance"
        )
        st.session_state.distance = selected_distance
    
    with col3:
        # Race type
        rt_options = presets.get_race_type_options(selected_breed)
        rt_display = presets.get_race_type_display()
        if st.session_state.race_type in rt_options:
            rt_idx = rt_options.index(st.session_state.race_type)
        else:
            rt_idx = 0
        
        selected_race_type = st.selectbox(
            "Race Type",
            options=rt_options,
            format_func=lambda x: rt_display.get(x, x),
            index=rt_idx if rt_options else 0,
            key="sb_race_type"
        )
        st.session_state.race_type = selected_race_type
        
        # Condition
        cond_options = presets.get_condition_options(selected_surface)
        cond_display = presets.get_condition_display()
        if st.session_state.condition in cond_options:
            cond_idx = cond_options.index(st.session_state.condition)
        else:
            cond_idx = 0
        
        selected_condition = st.selectbox(
            "Track Condition",
            options=cond_options,
            format_func=lambda x: cond_display.get(x, x),
            index=cond_idx if cond_options else 0,
            key="sb_condition"
        )
        st.session_state.condition = selected_condition
    
    # Second row
    col4, col5, col6 = st.columns(3)
    
    with col4:
        selected_date = st.date_input(
            "Race Date",
            value=pd.Timestamp(st.session_state.race_date),
            key="sb_date"
        )
        st.session_state.race_date = selected_date.strftime("%Y-%m-%d")
    
    with col5:
        selected_race_num = st.number_input(
            "Race Number",
            min_value=1,
            max_value=20,
            value=int(st.session_state.race_number),
            key="sb_race_num"
        )
        st.session_state.race_number = selected_race_num
    
    with col6:
        weather_options = presets.get_weather_options()
        weather_display = presets.get_weather_display()
        if st.session_state.weather in weather_options:
            w_idx = weather_options.index(st.session_state.weather)
        else:
            w_idx = 0
        
        selected_weather = st.selectbox(
            "Weather",
            options=weather_options,
            format_func=lambda x: weather_display.get(x, x),
            index=w_idx if weather_options else 0,
            key="sb_weather"
        )
        st.session_state.weather = selected_weather
    
    # Apply presets button
    if st.button("Apply Presets", type="primary", use_container_width=True):
        weights, log, dist_p, rt_p = presets.stack_presets(
            st.session_state.track_code,
            st.session_state.surface,
            st.session_state.distance,
            st.session_state.race_type,
            st.session_state.condition,
            st.session_state.weather
        )
        st.session_state.final_weights = weights
        st.session_state.stacking_log = log
        st.session_state.workflow_step = 2
        st.success(f"Presets applied! {len(log)} preset layers stacked.")
    
    # Show preset summary if available
    if st.session_state.stacking_log:
        with st.expander("Preset Stack Summary"):
            for entry in st.session_state.stacking_log:
                st.markdown(f"**{entry['step']}. {entry['preset']}:** {entry['detail']}")
    
    # Horse Input Section
    st.divider()
    st.header("Horse Input")
    
    input_method = st.radio(
        "Input Method",
        ["Manual Entry", "Load Sample Race (TB)", "Load Sample Race (QH)", "Upload CSV"],
        horizontal=True,
        key="input_method"
    )
    
    if input_method == "Manual Entry":
        render_manual_entry()
    elif input_method == "Load Sample Race (TB)":
        load_sample_race("TB")
    elif input_method == "Load Sample Race (QH)":
        load_sample_race("QH")
    elif input_method == "Upload CSV":
        render_csv_upload()
    
    # Display current horses
    if len(st.session_state.horses_df) > 0:
        st.divider()
        st.subheader(f"Horses Entered: {len(st.session_state.horses_df)}")
        
        display_cols = ["horse_name", "post_position", "morning_line", "speed_figure", 
                       "trainer_pct", "jockey_pct"]
        available_cols = [c for c in display_cols if c in st.session_state.horses_df.columns]
        st.dataframe(st.session_state.horses_df[available_cols], use_container_width=True)
        
        # Run Model button
        col_run1, col_run2 = st.columns([3, 1])
        with col_run1:
            if st.button("🚀 Run Model", type="primary", use_container_width=True):
                run_model()
        with col_run2:
            st.session_state.min_edge = st.number_input(
                "Min Edge %", min_value=0, max_value=50, 
                value=st.session_state.min_edge, key="min_edge_input"
            )


def render_manual_entry():
    """Render manual horse entry form."""
    st.markdown("Enter horse details below. Add at least 2 horses.")
    
    with st.form("horse_entry_form"):
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            name = st.text_input("Horse Name", key="he_name")
            post = st.number_input("Post Position", min_value=1, max_value=20, value=1, key="he_post")
        
        with col2:
            jockey = st.text_input("Jockey", key="he_jockey")
            trainer = st.text_input("Trainer", key="he_trainer")
        
        with col3:
            ml = st.number_input("Morning Line", min_value=0.1, value=10.0, step=0.5, key="he_ml")
            speed = st.number_input("Speed Figure", min_value=0, max_value=150, value=80, key="he_speed")
        
        with col4:
            ep = st.number_input("Early Pace", min_value=0, max_value=100, value=60, key="he_ep")
            lp = st.number_input("Late Pace", min_value=0, max_value=100, value=60, key="he_lp")
        
        col5, col6, col7, col8 = st.columns(4)
        
        with col5:
            cr = st.number_input("Class Rating", min_value=0, max_value=100, value=70, key="he_cr")
            tr_pct = st.number_input("Trainer Win%", min_value=0.0, max_value=50.0, value=15.0, key="he_tr")
        
        with col6:
            jk_pct = st.number_input("Jockey Win%", min_value=0.0, max_value=50.0, value=15.0, key="he_jk")
            ds = st.number_input("Days Since Race", min_value=0, max_value=365, value=14, key="he_ds")
        
        with col7:
            dist_fit = st.slider("Distance Fit", 0, 100, 70, key="he_df")
            surf_fit = st.slider("Surface Fit", 0, 100, 70, key="he_sf")
        
        with col8:
            scratched = st.checkbox("Scratched", key="he_scratch")
            form = st.selectbox("Form", ["Improving", "Stable", "Declining"], key="he_form")
        
        submitted = st.form_submit_button("Add Horse", use_container_width=True)
        
        if submitted and name.strip():
            form_score = {"Improving": 2, "Stable": 0, "Declining": -2}[form]
            
            new_horse = {
                "horse_name": name.strip(),
                "post_position": post,
                "jockey": jockey,
                "trainer": trainer,
                "morning_line": ml,
                "scratched": scratched,
                "speed_figure": speed,
                "early_pace": ep,
                "late_pace": lp,
                "class_rating": cr,
                "trainer_pct": tr_pct,
                "jockey_pct": jk_pct,
                "days_since_race": ds,
                "distance_fit_score": dist_fit,
                "surface_fit_score": surf_fit,
                "form_trend_score": form_score,
                "speed_consistency": 70,
                "workout_score": 65,
            }
            
            df = st.session_state.horses_df.copy()
            new_row = pd.DataFrame([new_horse])
            df = pd.concat([df, new_row], ignore_index=True)
            st.session_state.horses_df = df
            st.success(f"Added {name}!")


def load_sample_race(breed="TB"):
    """Load a sample race for demonstration."""
    import os
    
    if breed == "QH":
        horse_file = os.path.join("data", "sample", "sample_race_qh.csv")
        header_file = os.path.join("data", "sample", "sample_race_header_qh.csv")
    else:
        horse_file = os.path.join("data", "sample", "sample_race_tb.csv")
        header_file = os.path.join("data", "sample", "sample_race_header_tb.csv")
    
    try:
        horses = pd.read_csv(horse_file)
        header = pd.read_csv(header_file)
        
        # Set header values
        if len(header) > 0:
            h = header.iloc[0]
            st.session_state.track_code = str(h.get("track_code", "SAR"))
            st.session_state.race_date = str(h.get("date", "2026-05-11"))
            st.session_state.race_number = int(h.get("race_number", 8))
            st.session_state.breed = str(h.get("breed", "TB"))
            st.session_state.surface = str(h.get("surface", "Dirt"))
            
            # Parse distance
            dist_str = str(h.get("distance", "1M"))
            if "y" in dist_str.lower():
                # QH yards - convert to furlongs (1 furlong = 220 yards)
                yards = float(dist_str.lower().replace("y", "").strip())
                st.session_state.distance = round(yards / 220, 2)
            elif "M" in dist_str:
                # Miles
                st.session_state.distance = 8.0  # 1 mile = 8 furlongs
            else:
                try:
                    st.session_state.distance = float(dist_str)
                except:
                    st.session_state.distance = 8.0
            
            st.session_state.race_type = str(h.get("race_type", "STK"))
            st.session_state.condition = str(h.get("condition", "D-FAST"))
            st.session_state.weather = str(h.get("weather", "CLEAR"))
        
        st.session_state.horses_df = horses
        st.session_state.workflow_step = 2
        
        # Auto-apply presets
        weights, log, dist_p, rt_p = presets.stack_presets(
            st.session_state.track_code,
            st.session_state.surface,
            st.session_state.distance,
            st.session_state.race_type,
            st.session_state.condition,
            st.session_state.weather
        )
        st.session_state.final_weights = weights
        st.session_state.stacking_log = log
        
        st.success(f"Loaded sample {breed} race with {len(horses)} horses! Presets auto-applied.")
        st.rerun()
        
    except Exception as e:
        st.error(f"Error loading sample: {e}")


def render_csv_upload():
    """Render CSV upload interface."""
    st.markdown("Upload a CSV with horse data. Required columns: `horse_name`, `post_position`")
    st.markdown("Optional: `jockey`, `trainer`, `morning_line`, `speed_figure`, `early_pace`, `late_pace`, `class_rating`, `trainer_pct`, `jockey_pct`, `days_since_race`, `scratched`")
    
    uploaded = st.file_uploader("Upload Horse CSV", type=["csv"], key="csv_upload")
    
    if uploaded is not None:
        try:
            df = pd.read_csv(uploaded)
            
            # Validate
            if "horse_name" not in df.columns:
                st.error("CSV must have a 'horse_name' column!")
                return
            if "post_position" not in df.columns:
                st.error("CSV must have a 'post_position' column!")
                return
            
            # Fill defaults for missing columns
            defaults = {
                "jockey": "", "trainer": "", "morning_line": 10.0,
                "speed_figure": 70, "early_pace": 60, "late_pace": 60,
                "class_rating": 60, "trainer_pct": 10.0, "jockey_pct": 10.0,
                "days_since_race": 21, "scratched": False,
                "distance_fit_score": 70, "surface_fit_score": 70,
                "form_trend_score": 0, "speed_consistency": 65, "workout_score": 60,
            }
            
            for col, val in defaults.items():
                if col not in df.columns:
                    df[col] = val
            
            st.session_state.horses_df = df
            st.success(f"Loaded {len(df)} horses from CSV!")
            
        except Exception as e:
            st.error(f"Error reading CSV: {e}")


def run_model():
    """Execute the full model pipeline."""
    from model import model_core, grading, commentary
    from model.validators import validate_horse_data
    
    horses_df = st.session_state.horses_df.copy()
    
    # Validate
    errors, warnings = validate_horse_data(horses_df)
    if errors:
        for e in errors:
            st.error(e)
        return
    
    # Get weights
    weights = st.session_state.final_weights
    if not weights:
        weights, log, _, _ = presets.stack_presets(
            st.session_state.track_code,
            st.session_state.surface,
            st.session_state.distance,
            st.session_state.race_type,
            st.session_state.condition,
            st.session_state.weather
        )
        st.session_state.final_weights = weights
        st.session_state.stacking_log = log
    
    # Run model
    try:
        results = model_core.run_full_model(horses_df, weights, st.session_state.race_type)
        
        # Apply grades
        results = grading.compute_all_grades(results)
        
        # Compute race metrics
        confidence = model_core.compute_race_confidence(results)
        rec, rec_conf, rec_exp = grading.detect_bet_or_pass(results, st.session_state.min_edge)
        chalk_chaos = grading.get_chalk_chaos_label(results)
        fav_vuln = grading.get_favorite_vulnerability(results)
        
        # Store results
        st.session_state.results_df = results
        st.session_state.race_confidence = confidence
        st.session_state.bet_recommendation = rec
        st.session_state.bet_confidence = rec_conf
        st.session_state.bet_explanation = rec_exp
        st.session_state.chalk_chaos = chalk_chaos
        st.session_state.fav_vulnerability = fav_vuln
        st.session_state.model_run = True
        st.session_state.workflow_step = 4
        
        st.success("Model run complete! Go to Dashboard to see results.")
        
    except Exception as e:
        st.error(f"Model error: {e}")
        import traceback
        st.code(traceback.format_exc())


# Run main
main()
