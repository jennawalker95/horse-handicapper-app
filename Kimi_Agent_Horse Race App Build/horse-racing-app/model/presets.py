"""
presets.py - Load and stack track/distance/surface/race-type/condition presets.
"""

import pandas as pd
import numpy as np
import os
import streamlit as st

# ---------------------------------------------------------------------------
# Cache the raw CSV reads so they do not hit disk on every rerun.
# ---------------------------------------------------------------------------

@st.cache_data
def load_tracks_master():
    path = os.path.join("presets", "tracks_master.csv")
    if not os.path.exists(path):
        return pd.DataFrame()
    return pd.read_csv(path)


@st.cache_data
def load_track_distance():
    path = os.path.join("presets", "track_distance.csv")
    if not os.path.exists(path):
        return pd.DataFrame()
    return pd.read_csv(path)


@st.cache_data
def load_race_types():
    path = os.path.join("presets", "race_types.csv")
    if not os.path.exists(path):
        return pd.DataFrame()
    return pd.read_csv(path)


@st.cache_data
def load_conditions():
    path = os.path.join("presets", "conditions.csv")
    if not os.path.exists(path):
        return pd.DataFrame()
    return pd.read_csv(path)


@st.cache_data
def load_base_weights():
    path = os.path.join("presets", "base_weights.csv")
    if not os.path.exists(path):
        return pd.DataFrame()
    return pd.read_csv(path)


# ---------------------------------------------------------------------------
# Preset lookup helpers
# ---------------------------------------------------------------------------

def get_track_info(track_code):
    """Return track info dict for a given track code."""
    df = load_tracks_master()
    if df.empty or track_code not in df["code"].values:
        return None
    row = df[df["code"] == track_code].iloc[0]
    return {
        "code": row["code"],
        "name": row["name"],
        "state": row["state"],
        "surfaces": row["surfaces"],
        "breed": row["breed"],
        "notes": row.get("notes", ""),
        "seasonal": row.get("seasonal_flag", 0) == 1,
    }


def get_track_distance_preset(track_code, surface, distance_furlongs):
    """Get the track+surface+distance preset row."""
    df = load_track_distance()
    if df.empty:
        return None
    # Normalize distance to 2 decimal places for matching
    dist_rounded = round(float(distance_furlongs), 2)
    mask = (
        (df["track_code"] == track_code)
        & (df["surface"] == surface)
        & (df["furlongs"].round(2) == dist_rounded)
    )
    if mask.sum() == 0:
        # Try without distance exact match - find closest
        sub = df[(df["track_code"] == track_code) & (df["surface"] == surface)]
        if sub.empty:
            return None
        sub["dist_diff"] = (sub["furlongs"] - dist_rounded).abs()
        sub = sub.sort_values("dist_diff")
        row = sub.iloc[0]
    else:
        row = df[mask].iloc[0]
    return {
        "track_code": row["track_code"],
        "surface": row["surface"],
        "distance": row["distance"],
        "furlongs": row["furlongs"],
        "distance_group": row.get("distance_group", ""),
        "pace_shape_default": row.get("pace_shape_default", ""),
        "speed_closer_bias": row.get("speed_closer_bias", "Fair"),
        "rail_outside_bias": row.get("rail_outside_bias", "Fair"),
        "post_position_impact": row.get("post_position_impact", ""),
        "distance_quirks": row.get("distance_quirks", ""),
        "distance_weight_multiplier": float(row.get("distance_weight_multiplier", 1.0)),
        "horse_type_favored": row.get("horse_type_favored", ""),
    }


def get_race_type_preset(race_type_code):
    """Get race type preset row."""
    df = load_race_types()
    if df.empty:
        return None
    mask = df["code"] == race_type_code
    if mask.sum() == 0:
        return None
    row = df[mask].iloc[0]
    return {
        "code": row["code"],
        "name": row["name"],
        "breed": row.get("breed", "TB"),
        "weight_emphasis_multiplier": float(row.get("weight_emphasis_multiplier", 1.0)),
        "volatility_chaos_scale": float(row.get("volatility_chaos_scale", 1.0)),
        "pass_race_sensitivity": float(row.get("pass_race_sensitivity", 1.0)),
        "chaos_factor": row.get("chaos_factor", "Medium"),
        "typical_field_size": row.get("typical_field_size", "6-9"),
        "notes": row.get("notes", ""),
    }


def get_condition_preset(condition_type, condition_code):
    """Get condition preset by type and code."""
    df = load_conditions()
    if df.empty:
        return None
    mask = (df["condition_type"] == condition_type) & (df["code"] == condition_code)
    if mask.sum() == 0:
        return None
    row = df[mask].iloc[0]
    return {
        "condition_type": row["condition_type"],
        "code": row["code"],
        "name": row["name"],
        "speed_figure_adjust": float(row.get("speed_figure_adjust", 0)),
        "pace_bias_shift": float(row.get("pace_bias_shift", 0)),
        "closer_bias_shift": float(row.get("closer_bias_shift", 0)),
        "post_position_bias_shift": float(row.get("post_position_bias_shift", 0)),
        "weight_multiplier": float(row.get("weight_multiplier", 1.0)),
        "notes": row.get("notes", ""),
    }


def get_base_weights():
    """Return base weights as a dictionary {component: weight}."""
    df = load_base_weights()
    if df.empty:
        return _default_base_weights()
    weights = {}
    for _, row in df.iterrows():
        weights[row["component"]] = float(row["weight"])
    return weights


def _default_base_weights():
    """Fallback if CSV missing."""
    return {
        "speed_figure": 25,
        "early_pace": 15,
        "late_pace": 15,
        "pace_pressure": 10,
        "class_rating": 20,
        "form_trend": 15,
        "trainer_rating": 12,
        "jockey_rating": 10,
        "combo_rating": 8,
        "distance_fit": 10,
        "surface_fit": 8,
        "post_position": 5,
        "layoff_factor": 5,
        "weight_adjusted": 5,
        "speed_consistency": 10,
        "class_move": 8,
        "workout_pattern": 7,
        "bounce_flag": -5,
    }


# ---------------------------------------------------------------------------
# Stacking logic (mandatory order)
# ---------------------------------------------------------------------------

def stack_presets(track_code, surface, distance_furlongs, race_type_code, condition_code, weather_code=None):
    """
    Stack presets in order: Track -> Surface -> Distance -> Race Type -> Condition.
    Returns final weights dict + stacking log for transparency.
    """
    # 1) Start with base weights
    final_weights = get_base_weights().copy()
    stacking_log = []
    
    # Helper to log each step
    def log_step(name, detail, multipliers_applied):
        stacking_log.append({
            "step": len(stacking_log) + 1,
            "preset": name,
            "detail": detail,
            "multipliers": multipliers_applied,
        })
    
    # 2) Track preset (lookup track info - no weight changes, just validation)
    track_info = get_track_info(track_code)
    if track_info:
        log_step("Track", f"{track_info['name']} ({track_code}) - {track_info['breed']}", {})
    else:
        log_step("Track", f"{track_code} (custom/unlisted track)", {})
    
    # 3) Surface + Distance preset (combined in our data)
    dist_preset = get_track_distance_preset(track_code, surface, distance_furlongs)
    dist_mult = 1.0
    if dist_preset:
        dist_mult = dist_preset["distance_weight_multiplier"]
        for key in final_weights:
            final_weights[key] *= dist_mult
        log_step("Distance", 
                 f"{dist_preset['distance']} {surface} - multiplier: {dist_mult:.2f}, "
                 f"pace: {dist_preset['pace_shape_default']}, "
                 f"type favored: {dist_preset['horse_type_favored']}",
                 {"global": dist_mult})
    else:
        log_step("Distance", f"{distance_furlongs}F {surface} - no preset found, using defaults", {})
    
    # 4) Race type preset
    rt_preset = get_race_type_preset(race_type_code)
    rt_mult = 1.0
    if rt_preset:
        rt_mult = rt_preset["weight_emphasis_multiplier"]
        for key in final_weights:
            final_weights[key] *= rt_mult
        log_step("Race Type", 
                 f"{rt_preset['name']} ({race_type_code}) - multiplier: {rt_mult:.2f}, "
                 f"chaos: {rt_preset['chaos_factor']}, volatility: {rt_preset['volatility_chaos_scale']:.1f}",
                 {"global": rt_mult})
    else:
        log_step("Race Type", f"{race_type_code} - no preset found, using defaults", {})
    
    # 5) Track condition preset
    cond_mult = 1.0
    if condition_code:
        cond_preset = get_condition_preset("Surface", condition_code)
        if cond_preset:
            cond_mult = cond_preset["weight_multiplier"]
            for key in final_weights:
                final_weights[key] *= cond_mult
            log_step("Condition", 
                     f"{cond_preset['name']} - multiplier: {cond_mult:.2f}, "
                     f"speed adjust: {cond_preset['speed_figure_adjust']:+.1f}",
                     {"global": cond_mult})
        else:
            log_step("Condition", f"{condition_code} - no preset found", {})
    
    # Weather condition (optional)
    if weather_code:
        weather_preset = get_condition_preset("Weather", weather_code)
        if weather_preset:
            w_mult = weather_preset["weight_multiplier"]
            for key in final_weights:
                final_weights[key] *= w_mult
            log_step("Weather",
                     f"{weather_preset['name']} - multiplier: {w_mult:.2f}",
                     {"global": w_mult})
    
    # Normalize so max weight is ~25 (keep reasonable scale)
    max_w = max(abs(v) for v in final_weights.values()) if final_weights else 25
    if max_w > 30:
        scale = 25 / max_w
        for key in final_weights:
            final_weights[key] = round(final_weights[key] * scale, 2)
    
    return final_weights, stacking_log, dist_preset, rt_preset


def get_available_tracks():
    """Return list of track codes for dropdown."""
    df = load_tracks_master()
    if df.empty:
        return []
    return sorted(df["code"].unique().tolist())


def get_track_display_names():
    """Return dict of {code: display_name} for dropdown."""
    df = load_tracks_master()
    if df.empty:
        return {}
    return {row["code"]: f"{row['code']} - {row['name']}" for _, row in df.iterrows()}


def get_race_type_options(breed="TB"):
    """Get race type options filtered by breed."""
    df = load_race_types()
    if df.empty:
        return []
    if breed == "TB":
        mask = df["breed"].isin(["TB", "TB/QH"])
    elif breed == "QH":
        mask = df["breed"].isin(["QH", "TB/QH"])
    else:
        mask = pd.Series([True] * len(df))
    return sorted(df[mask]["code"].unique().tolist())


def get_race_type_display():
    """Return dict of {code: display_name} for race types."""
    df = load_race_types()
    if df.empty:
        return {}
    return {row["code"]: f"{row['code']} - {row['name']}" for _, row in df.iterrows()}


def get_condition_options(surface="Dirt"):
    """Get condition codes for a surface type."""
    df = load_conditions()
    if df.empty:
        return []
    if "Turf" in surface or "turf" in surface.lower():
        prefix = "T"
    else:
        prefix = "D"
    mask = df["condition_type"] == "Surface"
    surf_conds = df[mask]
    codes = [c for c in surf_conds["code"].unique() if c.startswith(prefix)]
    return sorted(codes)


def get_condition_display():
    """Return dict of {code: display_name} for conditions."""
    df = load_conditions()
    if df.empty:
        return {}
    return {row["code"]: row["name"] for _, row in df.iterrows() if row["condition_type"] == "Surface"}


def get_weather_options():
    """Get weather condition codes."""
    df = load_conditions()
    if df.empty:
        return []
    mask = df["condition_type"] == "Weather"
    return sorted(df[mask]["code"].unique().tolist())


def get_weather_display():
    """Return dict of {code: display_name} for weather."""
    df = load_conditions()
    if df.empty:
        return {}
    return {row["code"]: row["name"] for _, row in df.iterrows() if row["condition_type"] == "Weather"}
