"""
model_core.py - Core handicapping computations: ratings, probabilities, fair odds.
"""

import pandas as pd
import numpy as np
import streamlit as st


# ---------------------------------------------------------------------------
# Speed & Pace calculations
# ---------------------------------------------------------------------------

def compute_speed_pace(horses_df):
    """
    Compute adjusted speed figures, early/late pace ratings, pace vs field,
    energy distribution, and pace pressure indicator.
    """
    df = horses_df.copy()
    
    # Normalized speed figure (0-100 scale)
    if "speed_figure" in df.columns:
        max_sf = df["speed_figure"].max()
        if max_sf > 0:
            df["speed_figure_norm"] = (df["speed_figure"] / max_sf * 100).round(1)
        else:
            df["speed_figure_norm"] = 50.0
    else:
        df["speed_figure_norm"] = 50.0
    
    # Early pace rating (0-100)
    if "early_pace" in df.columns:
        max_ep = df["early_pace"].max()
        if max_ep > 0:
            df["early_pace_norm"] = (df["early_pace"] / max_ep * 100).round(1)
        else:
            df["early_pace_norm"] = 50.0
    else:
        df["early_pace_norm"] = 50.0
    
    # Late pace rating (0-100)
    if "late_pace" in df.columns:
        max_lp = df["late_pace"].max()
        if max_lp > 0:
            df["late_pace_norm"] = (df["late_pace"] / max_lp * 100).round(1)
        else:
            df["late_pace_norm"] = 50.0
    else:
        df["late_pace_norm"] = 50.0
    
    # Pace vs field (relative early speed rank)
    df["pace_vs_field"] = df["early_pace_norm"].rank(ascending=False, method="min").astype(int)
    
    # Energy distribution (% early vs late)
    total_pace = df["early_pace_norm"] + df["late_pace_norm"]
    total_pace = total_pace.replace(0, 1)
    df["energy_distribution"] = (df["early_pace_norm"] / total_pace * 100).round(1)
    
    # Pace pressure indicator (how many horses press early)
    fast_starters = (df["early_pace_norm"] >= 70).sum()
    df["pace_pressure"] = min(fast_starters * 15, 100)  # Scale 0-100
    
    # Pace scenario projection
    df["pace_scenario"] = df.apply(_project_pace_scenario, axis=1, args=(df,))
    
    return df


def _project_pace_scenario(row, full_df):
    """Project pace scenario for a single horse."""
    ep = row.get("early_pace_norm", 50)
    lp = row.get("late_pace_norm", 50)
    pace_pressure = row.get("pace_pressure", 50)
    
    # Count horses with higher early pace
    faster_early = (full_df["early_pace_norm"] > ep).sum()
    
    if faster_early == 0 and ep >= 75:
        return "Lone Speed"
    elif faster_early >= 2 and ep >= 65:
        return "Pace Pressure"
    elif pace_pressure >= 60 and lp >= 70:
        return "Pace Collapse Threat"
    elif ep >= 60 and lp >= 60:
        return "Dual Threat"
    elif lp >= 70 and pace_pressure >= 40:
        return "Closer Friendly"
    else:
        return "Stalker Setup"


# ---------------------------------------------------------------------------
# Class & Form calculations
# ---------------------------------------------------------------------------

def compute_class_form(horses_df, race_type_code="ALW"):
    """Compute class ratings, form trends, layoff factors, bounce flags."""
    df = horses_df.copy()
    
    # Class rating (0-100)
    if "class_rating" in df.columns:
        max_cr = df["class_rating"].max()
        if max_cr > 0:
            df["class_rating_norm"] = (df["class_rating"] / max_cr * 100).round(1)
        else:
            df["class_rating_norm"] = 50.0
    else:
        df["class_rating_norm"] = 50.0
    
    # Class move direction
    if "last_class_level" in df.columns and "prior_class_level" in df.columns:
        df["class_move"] = df["last_class_level"] - df["prior_class_level"]
        df["class_move_label"] = df["class_move"].apply(
            lambda x: "Up" if x > 0.5 else ("Down" if x < -0.5 else "Same")
        )
    else:
        df["class_move"] = 0
        df["class_move_label"] = "Same"
    
    # Field strength adjustment (default 1.0 if not provided)
    df["field_strength_adj"] = df.get("field_strength", 1.0).fillna(1.0)
    
    # Form trend (improving/declining/stable)
    if "form_trend_score" in df.columns:
        df["form_trend"] = df["form_trend_score"].apply(
            lambda x: "Improving" if x >= 2 else ("Declining" if x <= -2 else "Stable")
        )
    else:
        # Infer from speed figures if available
        if "speed_figure_1" in df.columns and "speed_figure_3" in df.columns:
            trend = df["speed_figure_1"] - df["speed_figure_3"]
            df["form_trend"] = trend.apply(
                lambda x: "Improving" if x >= 3 else ("Declining" if x <= -3 else "Stable")
            )
        else:
            df["form_trend"] = "Stable"
    
    # Layoff penalty/bonus
    if "days_since_race" in df.columns:
        df["layoff_factor"] = df["days_since_race"].apply(_compute_layoff_factor)
    else:
        df["layoff_factor"] = 0
    
    # Bounce/regression flag
    df["bounce_flag"] = df.apply(_check_bounce_risk, axis=1)
    
    return df


def _compute_layoff_factor(days):
    """Compute layoff factor: negative penalty for too long or too short."""
    if pd.isna(days):
        return -2  # Unknown = slight penalty
    if days <= 7:
        return -3  # Too quick - may bounce
    elif days <= 21:
        return 2   # Sharp - fit
    elif days <= 45:
        return 0   # Normal
    elif days <= 90:
        return -2  # Getting stale
    else:
        return -4  # Long layoff - rust


def _check_bounce_risk(row):
    """Check if horse is at risk of a bounce (regression after peak)."""
    sf = row.get("speed_figure_norm", 50)
    trend = row.get("form_trend", "Stable")
    
    # If coming off a career top and not improving
    if sf >= 95 and trend != "Improving":
        return True
    # If two consecutive big figures
    if sf >= 90 and trend == "Declining":
        return True
    return False


# ---------------------------------------------------------------------------
# Trainer & Jockey calculations
# ---------------------------------------------------------------------------

def compute_connections(horses_df):
    """Compute trainer/jockey ratings, combo ratings, and intent flags."""
    df = horses_df.copy()
    
    # Trainer effectiveness (0-100)
    if "trainer_pct" in df.columns:
        df["trainer_rating"] = (df["trainer_pct"] * 5).clip(0, 100).round(1)  # Scale win% to 0-100
    else:
        df["trainer_rating"] = 50.0  # Default
    
    # Jockey effectiveness (0-100)
    if "jockey_pct" in df.columns:
        df["jockey_rating"] = (df["jockey_pct"] * 5).clip(0, 100).round(1)
    else:
        df["jockey_rating"] = 50.0
    
    # Combo rating (trainer + jockey synergy)
    df["combo_rating"] = ((df["trainer_rating"] + df["jockey_rating"]) / 2).round(1)
    
    # Intent flags
    df["intent_flags"] = df.apply(_detect_intent_flags, axis=1)
    
    return df


def _detect_intent_flags(row):
    """Detect trainer intent signals."""
    flags = []
    
    # First off claim
    if row.get("first_off_claim", False):
        flags.append("First Off Claim")
    
    # Second off layoff
    if row.get("days_since_race", 999) <= 45 and row.get("race_count_90d", 0) <= 1:
        flags.append("Second Off Layoff")
    
    # Class drop
    if row.get("class_move_label", "") == "Down":
        flags.append("Class Drop")
    
    # Route to sprint move (or vice versa)
    if row.get("distance_move", "") in ["Route to Sprint", "Sprint to Route"]:
        flags.append(f"Distance Move: {row['distance_move']}")
    
    # Positive workout pattern
    if row.get("workout_pattern", "") == "Bullet":
        flags.append("Bullet Workout")
    
    return flags if flags else ["No strong signals"]


# ---------------------------------------------------------------------------
# Composite Power Rating
# ---------------------------------------------------------------------------

def compute_composite(horses_df, weights=None):
    """
    Compute composite power rating from weighted components.
    weights: dict of component -> weight multiplier from stacked presets.
    """
    df = horses_df.copy()
    
    if weights is None:
        weights = {}
    
    # Ensure all component columns exist with defaults
    for col in ["speed_figure_norm", "early_pace_norm", "late_pace_norm",
                "class_rating_norm", "trainer_rating", "jockey_rating", "combo_rating"]:
        if col not in df.columns:
            df[col] = 50.0
    
    # Calculate weighted composite
    def weighted_score(row):
        score = 0
        total_weight = 0
        
        components = {
            "speed_figure": row.get("speed_figure_norm", 50),
            "early_pace": row.get("early_pace_norm", 50),
            "late_pace": row.get("late_pace_norm", 50),
            "pace_pressure": row.get("pace_pressure", 50),
            "class_rating": row.get("class_rating_norm", 50),
            "form_trend": 70 if row.get("form_trend", "") == "Improving" else (
                40 if row.get("form_trend", "") == "Declining" else 55),
            "trainer_rating": row.get("trainer_rating", 50),
            "jockey_rating": row.get("jockey_rating", 50),
            "combo_rating": row.get("combo_rating", 50),
            "distance_fit": row.get("distance_fit_score", 50),
            "surface_fit": row.get("surface_fit_score", 50),
            "post_position": row.get("post_position_score", 50),
            "layoff_factor": max(0, 50 + row.get("layoff_factor", 0) * 5),
            "speed_consistency": row.get("speed_consistency", 50),
            "class_move": 70 if row.get("class_move_label", "") == "Down" else (
                55 if row.get("class_move_label", "") == "Same" else 45),
            "workout_pattern": row.get("workout_score", 50),
            "bounce_flag": 30 if row.get("bounce_flag", False) else 60,
        }
        
        for comp, value in components.items():
            w = weights.get(comp, 10)  # Default weight 10
            score += value * w
            total_weight += abs(w)
        
        return (score / total_weight).round(1) if total_weight > 0 else 50.0
    
    df["composite_rating"] = df.apply(weighted_score, axis=1)
    
    # Component breakdown for transparency
    df["component_breakdown"] = df.apply(_get_component_breakdown, axis=1, args=(weights,))
    
    return df


def _get_component_breakdown(row, weights):
    """Return a dict of component scores for display."""
    return {
        "Speed": round(row.get("speed_figure_norm", 50), 1),
        "Early Pace": round(row.get("early_pace_norm", 50), 1),
        "Late Pace": round(row.get("late_pace_norm", 50), 1),
        "Class": round(row.get("class_rating_norm", 50), 1),
        "Trainer": round(row.get("trainer_rating", 50), 1),
        "Jockey": round(row.get("jockey_rating", 50), 1),
        "Combo": round(row.get("combo_rating", 50), 1),
        "Form": row.get("form_trend", "Stable"),
        "Layoff": row.get("layoff_factor", 0),
        "Bounce Risk": row.get("bounce_flag", False),
    }


# ---------------------------------------------------------------------------
# Probability & Fair Odds
# ---------------------------------------------------------------------------

def compute_probabilities(horses_df):
    """
    Compute Win/Place/Show probabilities, fair odds, overlay detection.
    """
    df = horses_df.copy()
    
    # Filter out scratched horses
    active_df = df[~df.get("scratched", pd.Series([False] * len(df), index=df.index))].copy()
    
    if len(active_df) == 0:
        return df  # No active horses
    
    # Win probability from composite rating (softmax-like)
    ratings = active_df["composite_rating"].values
    # Convert to probabilities using exponential softmax
    exp_ratings = np.exp((ratings - ratings.max()) / 10)  # Temperature = 10
    win_probs = (exp_ratings / exp_ratings.sum() * 100).round(1)
    active_df["win_probability"] = win_probs
    
    # Place probability (higher horses get more place probability)
    # Simplified model: place prob ~ win_prob^0.7 scaled
    place_raw = np.power(win_probs / 100, 0.7)
    place_probs = (place_raw / place_raw.sum() * 100).round(1)
    # Apply place scaling (typically 1.5-2x win prob)
    place_multiplier = 1.8
    place_probs = (place_probs * place_multiplier).clip(5, 95).round(1)
    # Renormalize
    place_probs = (place_probs / place_probs.sum() * 100).round(1)
    active_df["place_probability"] = place_probs
    
    # Show probability
    show_raw = np.power(win_probs / 100, 0.5)
    show_probs = (show_raw / show_raw.sum() * 100).round(1)
    show_multiplier = 2.5
    show_probs = (show_probs * show_multiplier).clip(10, 98).round(1)
    show_probs = (show_probs / show_probs.sum() * 100).round(1)
    active_df["show_probability"] = show_probs
    
    # Fair odds (decimal = 100 / probability)
    active_df["fair_odds_win"] = (100 / active_df["win_probability"]).round(2)
    active_df["fair_odds_place"] = (100 / active_df["place_probability"]).round(2)
    active_df["fair_odds_show"] = (100 / active_df["show_probability"]).round(2)
    
    # Morning line comparison for value detection
    if "morning_line" in active_df.columns:
        active_df["value_label"] = active_df.apply(_detect_value, axis=1)
        active_df["edge_percent"] = active_df.apply(_compute_edge, axis=1)
    else:
        active_df["value_label"] = "Unknown"
        active_df["edge_percent"] = 0.0
    
    # Merge back to full df
    for col in ["win_probability", "place_probability", "show_probability",
                "fair_odds_win", "fair_odds_place", "fair_odds_show",
                "value_label", "edge_percent"]:
        df[col] = active_df[col].reindex(df.index)
    
    return df


def _detect_value(row):
    """Detect if horse is overlay, underlay, or fair value."""
    ml = row.get("morning_line", None)
    fair = row.get("fair_odds_win", None)
    
    if pd.isna(ml) or pd.isna(fair) or ml <= 0 or fair <= 0:
        return "Unknown"
    
    ratio = fair / ml
    if ratio >= 1.3:
        return "Overlay"
    elif ratio <= 0.7:
        return "Underlay"
    else:
        return "Fair"


def _compute_edge(row):
    """Compute edge percentage: (fair - ml) / ml * 100"""
    ml = row.get("morning_line", None)
    fair = row.get("fair_odds_win", None)
    if pd.isna(ml) or pd.isna(fair) or ml <= 0:
        return 0.0
    return round((fair - ml) / ml * 100, 1)


# ---------------------------------------------------------------------------
# Rankings
# ---------------------------------------------------------------------------

def compute_rankings(horses_df):
    """Compute power rank and value rank."""
    df = horses_df.copy()
    
    active_mask = ~df.get("scratched", pd.Series([False] * len(df), index=df.index))
    active_df = df[active_mask].copy()
    
    if len(active_df) == 0:
        return df
    
    # Power rank (by composite rating)
    active_df["power_rank"] = active_df["composite_rating"].rank(ascending=False, method="min").astype(int)
    
    # Value rank (by edge percent)
    if "edge_percent" in active_df.columns:
        active_df["value_rank"] = active_df["edge_percent"].rank(ascending=False, method="min").astype(int)
    else:
        active_df["value_rank"] = 999
    
    # Merge back
    for col in ["power_rank", "value_rank"]:
        df[col] = active_df[col].reindex(df.index)
    
    return df


# ---------------------------------------------------------------------------
# Confidence score
# ---------------------------------------------------------------------------

def compute_race_confidence(horses_df):
    """Compute overall race confidence score (0-100)."""
    df = horses_df.copy()
    active_df = df[~df.get("scratched", pd.Series([False] * len(df), index=df.index))].copy()
    
    if len(active_df) < 2:
        return 30  # Low confidence with few horses
    
    confidence = 70  # Base
    
    # Penalize if ratings are very close (uncertain race)
    comp_std = active_df["composite_rating"].std()
    if comp_std < 3:
        confidence -= 20  # Too close to call
    elif comp_std > 10:
        confidence += 10  # Clear separation
    
    # Penalize large field (more chaotic)
    if len(active_df) >= 12:
        confidence -= 10
    
    # Penalize if many unknowns
    unknown_pct = (active_df["value_label"] == "Unknown").mean() * 100
    if unknown_pct > 50:
        confidence -= 15
    
    # Boost if clear favorite
    top_prob = active_df["win_probability"].max()
    if top_prob >= 35:
        confidence += 10
    elif top_prob <= 15:
        confidence -= 10  # Wide open race
    
    return max(0, min(100, confidence))


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------

def run_full_model(horses_df, weights=None, race_type_code="ALW"):
    """
    Run the complete model pipeline:
      1) Speed & Pace
      2) Class & Form
      3) Trainer & Jockey
      4) Composite Rating
      5) Probabilities & Fair Odds
      6) Rankings
    """
    df = horses_df.copy()
    
    # Step 1: Speed & Pace
    df = compute_speed_pace(df)
    
    # Step 2: Class & Form
    df = compute_class_form(df, race_type_code)
    
    # Step 3: Trainer & Jockey
    df = compute_connections(df)
    
    # Step 4: Composite Rating (with stacked weights)
    df = compute_composite(df, weights)
    
    # Step 5: Probabilities
    df = compute_probabilities(df)
    
    # Step 6: Rankings
    df = compute_rankings(df)
    
    return df
