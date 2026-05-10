"""
grading.py - Exact grade thresholds and labels for the handicapping model.

All thresholds are non-negotiable and must be applied strictly.
"""

import pandas as pd


# Grade color mapping for UI
GRADE_COLORS = {
    "A": "#22c55e",   # Green
    "B": "#3b82f6",   # Blue
    "C": "#f59e0b",   # Amber
    "D": "#ef4444",   # Red
}

GRADE_BG_COLORS = {
    "A": "#dcfce7",
    "B": "#dbeafe",
    "C": "#fef3c7",
    "D": "#fee2e2",
}


def grade_overall(win_prob, power_rank, value_label, composite_rating):
    """
    OVERALL GRADE (Composite + Value):
    - A: Top 1-2 by composite AND win% >= 25% AND (overlay OR fair value)
    - B: Top 3-4 by composite AND win% 15-24%
    - C: Competitive; win% 8-14%
    - D: win% < 8% OR clear underlay/low competitiveness
    """
    if pd.isna(win_prob):
        return "D"
    
    wp = float(win_prob)
    pr = int(power_rank) if not pd.isna(power_rank) else 99
    vl = str(value_label) if not pd.isna(value_label) else "Unknown"
    
    # A: Top 1-2 by composite AND win% >= 25% AND (overlay OR fair value)
    if pr <= 2 and wp >= 25 and vl in ("Overlay", "Fair"):
        return "A"
    
    # B: Top 3-4 by composite AND win% 15-24%
    if pr <= 4 and wp >= 15:
        return "B"
    
    # C: Competitive; win% 8-14%
    if wp >= 8:
        return "C"
    
    # D: win% < 8% OR clear underlay/low competitiveness
    return "D"


def grade_win(win_prob, value_label):
    """
    WIN GRADE:
    - A-WIN: >=25% win AND value (overlay/fair)
    - B-WIN: 15-24%
    - C-WIN: 8-14%
    - D-WIN: <8%
    """
    if pd.isna(win_prob):
        return "D"
    
    wp = float(win_prob)
    vl = str(value_label) if not pd.isna(value_label) else "Unknown"
    
    if wp >= 25 and vl in ("Overlay", "Fair"):
        return "A"
    elif wp >= 15:
        return "B"
    elif wp >= 8:
        return "C"
    else:
        return "D"


def grade_place(place_prob):
    """
    PLACE GRADE:
    - A-PLACE: >=60%
    - B-PLACE: 45-59%
    - C-PLACE: 30-44%
    - D-PLACE: <30%
    """
    if pd.isna(place_prob):
        return "D"
    
    pp = float(place_prob)
    
    if pp >= 60:
        return "A"
    elif pp >= 45:
        return "B"
    elif pp >= 30:
        return "C"
    else:
        return "D"


def grade_show(show_prob):
    """
    SHOW GRADE:
    - A-SHOW: >=75%
    - B-SHOW: 60-74%
    - C-SHOW: 45-59%
    - D-SHOW: <45%
    """
    if pd.isna(show_prob):
        return "D"
    
    sp = float(show_prob)
    
    if sp >= 75:
        return "A"
    elif sp >= 60:
        return "B"
    elif sp >= 45:
        return "C"
    else:
        return "D"


def compute_all_grades(horses_df):
    """
    Apply all grading functions to the dataframe.
    Returns dataframe with: overall_grade, win_grade, place_grade, show_grade
    """
    df = horses_df.copy()
    
    # Filter active horses
    active_mask = ~df.get("scratched", pd.Series([False] * len(df), index=df.index))
    active_df = df[active_mask].copy()
    
    if len(active_df) == 0:
        df["overall_grade"] = "D"
        df["win_grade"] = "D"
        df["place_grade"] = "D"
        df["show_grade"] = "D"
        return df
    
    # Apply grading functions
    active_df["overall_grade"] = active_df.apply(
        lambda r: grade_overall(
            r.get("win_probability"),
            r.get("power_rank"),
            r.get("value_label"),
            r.get("composite_rating")
        ), axis=1
    )
    
    active_df["win_grade"] = active_df.apply(
        lambda r: grade_win(r.get("win_probability"), r.get("value_label")), axis=1
    )
    
    active_df["place_grade"] = active_df["place_probability"].apply(grade_place)
    active_df["show_grade"] = active_df["show_probability"].apply(grade_show)
    
    # Merge back
    for col in ["overall_grade", "win_grade", "place_grade", "show_grade"]:
        df[col] = active_df[col].reindex(df.index)
    
    return df


def get_grade_color(grade):
    """Return hex color for a grade."""
    return GRADE_COLORS.get(str(grade).upper()[0], "#6b7280")


def get_grade_bg_color(grade):
    """Return background color for a grade badge."""
    return GRADE_BG_COLORS.get(str(grade).upper()[0], "#f3f4f6")


def grade_label_html(grade, size="normal"):
    """Return HTML span for a grade badge."""
    color = get_grade_color(grade)
    bg = get_grade_bg_color(grade)
    font_size = "1.2em" if size == "large" else "1em"
    padding = "4px 12px" if size == "large" else "2px 8px"
    return (
        f'<span style="background-color:{bg}; color:{color}; '
        f'font-weight:bold; border-radius:6px; padding:{padding}; '
        f'font-size:{font_size}; border:2px solid {color};">{grade}</span>'
    )


def detect_longshot(horse_row):
    """
    Detect if a horse qualifies as a wildcard/longshot play.
    Conditions: low/moderate win% but strong pace fit OR improving form 
    OR condition/track/distance advantage OR trainer intent OR significant overlay.
    """
    wp = horse_row.get("win_probability", 0)
    if pd.isna(wp):
        wp = 0
    
    vl = str(horse_row.get("value_label", ""))
    ep = horse_row.get("early_pace_norm", 50)
    lp = horse_row.get("late_pace_norm", 50)
    form = str(horse_row.get("form_trend", ""))
    bounce = horse_row.get("bounce_flag", False)
    edge = horse_row.get("edge_percent", 0)
    if pd.isna(edge):
        edge = 0
    
    # Check longshot conditions
    reasons = []
    
    # Significant overlay with moderate win chance
    if vl == "Overlay" and edge >= 20 and wp >= 5:
        reasons.append(f"Significant overlay ({edge:+.0f}% edge)")
    
    # Strong pace fit for scenario
    scenario = str(horse_row.get("pace_scenario", ""))
    if "Lone Speed" in scenario and wp >= 5 and wp <= 20:
        reasons.append("Lone speed setup - pace advantage")
    if "Pace Collapse" in scenario and lp >= 75 and wp >= 5 and wp <= 20:
        reasons.append("Pace collapse threat - strong closer")
    
    # Improving form
    if form == "Improving" and wp >= 5 and wp <= 18:
        reasons.append("Improving form trend - upward trajectory")
    
    # High pace rating with moderate win%
    if ep >= 80 and wp >= 5 and wp <= 15:
        reasons.append("Elite early speed - wire threat")
    
    # Class drop with decent rating
    if horse_row.get("class_move_label", "") == "Down" and wp >= 5 and wp <= 18:
        reasons.append("Class drop - facing easier company")
    
    # Qualify if at least 2 reasons or strong overlay
    is_longshot = (len(reasons) >= 2) or (vl == "Overlay" and edge >= 30 and wp >= 3)
    
    return is_longshot, reasons


def get_wildcard_label(horse_row):
    """Return wildcard label and explanation."""
    is_ls, reasons = detect_longshot(horse_row)
    if not is_ls:
        return None, []
    
    wp = horse_row.get("win_probability", 0)
    if pd.isna(wp):
        wp = 0
    
    if wp >= 8:
        label = "WILDCARD PLAY"
    else:
        label = "LONGSHOT VALUE"
    
    return label, reasons


def detect_bet_or_pass(horses_df, min_edge=10):
    """
    Betting decision engine.
    Returns: recommendation, confidence, explanation
    """
    active_df = horses_df[~horses_df.get("scratched", pd.Series([False] * len(horses_df), index=horses_df.index))].copy()
    
    if len(active_df) == 0:
        return "PASS", 0, "No active horses to evaluate."
    
    # Find best horse
    best = active_df.loc[active_df["composite_rating"].idxmax()]
    
    wp = best.get("win_probability", 0)
    if pd.isna(wp):
        wp = 0
    edge = best.get("edge_percent", 0)
    if pd.isna(edge):
        edge = 0
    vl = str(best.get("value_label", ""))
    og = best.get("overall_grade", "D")
    
    # Pass race detection
    if len(active_df) >= 14:
        return "PASS", 30, "Too many runners - chaotic race, low predictability."
    
    # Check for no edge
    a_grades = active_df[active_df["overall_grade"] == "A"]
    if len(a_grades) == 0 and active_df["win_probability"].max() < 15:
        return "PASS", 40, "No clear A-grade contender. Wide open race."
    
    # Check for underlay favorite
    fav = active_df.loc[active_df["win_probability"].idxmax()]
    fav_ml = fav.get("morning_line", 999)
    fav_fair = fav.get("fair_odds_win", 999)
    if not pd.isna(fav_ml) and not pd.isna(fav_fair) and fav_ml > 0:
        if fav_fair / fav_ml < 0.6:
            return "PASS", 50, f"Favorite appears underlay (fair {fav_fair:.1f} vs ML {fav_ml:.1f}). No value."
    
    # BET recommendation
    if og == "A" and vl in ("Overlay", "Fair") and edge >= min_edge:
        return "BET", 85, f"Strong A-grade with {edge:+.0f}% edge. Fair odds {best.get('fair_odds_win', 0):.1f} vs ML {best.get('morning_line', 0):.1f}."
    
    if og == "A" and wp >= 25:
        return "BET", 75, f"A-grade contender with {wp:.0f}% win probability. Solid play."
    
    if og == "B" and vl == "Overlay" and edge >= min_edge + 5:
        return "BET", 65, f"B-grade overlay with {edge:+.0f}% edge. Value play."
    
    if vl == "Overlay" and edge >= 20:
        return "BET", 60, f"Significant overlay ({edge:+.0f}% edge) despite B/C grade."
    
    # Otherwise PASS
    if og in ("C", "D"):
        return "PASS", 55, f"Best horse graded {og}. No strong edge detected."
    
    return "PASS", 50, "No clear betting edge found. Race may be too competitive."


def get_chalk_chaos_label(horses_df):
    """Label the race as Chalky or Chaotic."""
    active_df = horses_df[~horses_df.get("scratched", pd.Series([False] * len(horses_df), index=horses_df.index))].copy()
    
    if len(active_df) == 0:
        return "Unknown"
    
    top_prob = active_df["win_probability"].max()
    prob_std = active_df["win_probability"].std()
    
    if top_prob >= 40 and prob_std >= 12:
        return "Chalky"
    elif top_prob <= 15 and prob_std <= 5:
        return "Chaotic"
    else:
        return "Balanced"


def get_favorite_vulnerability(horses_df):
    """Score how vulnerable the favorite is (0-100)."""
    active_df = horses_df[~horses_df.get("scratched", pd.Series([False] * len(horses_df), index=horses_df.index))].copy()
    
    if len(active_df) == 0:
        return 50
    
    fav = active_df.loc[active_df["win_probability"].idxmax()]
    vuln = 50  # Base
    
    # Check for bounce risk
    if fav.get("bounce_flag", False):
        vuln += 20
    
    # Check pace scenario (lone speed = vulnerable if pressured)
    scenario = str(fav.get("pace_scenario", ""))
    if "Lone Speed" in scenario and (active_df["early_pace_norm"] >= 65).sum() >= 2:
        vuln += 15  # Other speed to pressure
    
    # Check for underlay
    if fav.get("value_label", "") == "Underlay":
        vuln += 10
    
    # Check class move up
    if fav.get("class_move_label", "") == "Up":
        vuln += 10
    
    return min(100, vuln)
