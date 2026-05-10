"""
commentary.py - Commentary engine: Quick Look, Why Chosen/Why Not, Wildcard/Longshot analysis.
"""

import pandas as pd


def generate_quick_look(horse_row):
    """
    Generate a 1-2 line Quick Look summary for a horse.
    Format: "#Rank HORSE — Grade (W:A / P:B / S:A) — Win% Win — Value — Key Reason"
    """
    name = horse_row.get("horse_name", "Unknown")
    rank = int(horse_row.get("power_rank", 99)) if not pd.isna(horse_row.get("power_rank")) else 99
    og = horse_row.get("overall_grade", "D")
    wg = horse_row.get("win_grade", "D")
    pg = horse_row.get("place_grade", "D")
    sg = horse_row.get("show_grade", "D")
    wp = horse_row.get("win_probability", 0)
    if pd.isna(wp):
        wp = 0
    fair = horse_row.get("fair_odds_win", 0)
    if pd.isna(fair):
        fair = 0
    vl = str(horse_row.get("value_label", "Unknown"))
    
    # Key reason
    reasons = _get_key_reasons(horse_row, max_reasons=2)
    reason_text = "; ".join(reasons) if reasons else "No standout factor"
    
    line = (
        f"**#{rank} {name}** — **{og}** "
        f"(W:{wg} / P:{pg} / S:{sg}) — "
        f"{wp:.0f}% Win — Fair {fair:.1f} — **{vl}** — {reason_text}"
    )
    
    return line


def generate_commentary(horse_row, all_horses_df=None):
    """
    Generate WHY CHOSEN / WHY NOT commentary for a horse.
    Returns dict with strengths and weaknesses.
    """
    og = horse_row.get("overall_grade", "D")
    wp = horse_row.get("win_probability", 0)
    if pd.isna(wp):
        wp = 0
    
    strengths = []
    weaknesses = []
    
    # Speed analysis
    sf = horse_row.get("speed_figure_norm", 50)
    if sf >= 80:
        strengths.append(f"Strong speed figures ({sf:.0f}/100) - top tier")
    elif sf >= 65:
        strengths.append(f"Decent speed figures ({sf:.0f}/100)")
    elif sf < 50:
        weaknesses.append(f"Below average speed figures ({sf:.0f}/100)")
    
    # Pace analysis
    ep = horse_row.get("early_pace_norm", 50)
    lp = horse_row.get("late_pace_norm", 50)
    scenario = str(horse_row.get("pace_scenario", ""))
    
    if "Lone Speed" in scenario:
        strengths.append("Lone speed setup - unchallenged early lead potential")
    elif "Pace Collapse" in scenario and lp >= 70:
        strengths.append("Pace collapse scenario favors strong closing kick")
    elif ep >= 75:
        strengths.append(f"Elite early speed ({ep:.0f}/100) - wire-to-wire threat")
    elif lp >= 75:
        strengths.append(f"Strong closing kick ({lp:.0f}/100) - late runner")
    
    if "Pace Pressure" in scenario and ep >= 65:
        weaknesses.append("Faces pace pressure - may duel and fade")
    
    # Class analysis
    cr = horse_row.get("class_rating_norm", 50)
    cm = str(horse_row.get("class_move_label", ""))
    if cr >= 80:
        strengths.append(f"Top class rating ({cr:.0f}/100)")
    elif cr >= 65:
        strengths.append(f"Solid class level ({cr:.0f}/100)")
    elif cr < 50:
        weaknesses.append(f"Below average class ({cr:.0f}/100)")
    
    if cm == "Down":
        strengths.append("Drops in class - facing easier competition")
    elif cm == "Up":
        weaknesses.append("Steps up in class - tougher test today")
    
    # Form analysis
    form = str(horse_row.get("form_trend", ""))
    if form == "Improving":
        strengths.append("Improving form - trending in right direction")
    elif form == "Declining":
        weaknesses.append("Declining form - recent races deteriorating")
    
    # Bounce risk
    if horse_row.get("bounce_flag", False):
        weaknesses.append("Bounce risk - may regress off recent peak performance")
    
    # Connections
    tr = horse_row.get("trainer_rating", 50)
    jk = horse_row.get("jockey_rating", 50)
    if tr >= 75:
        strengths.append(f"Hot trainer connection ({tr:.0f}/100)")
    elif tr < 40:
        weaknesses.append(f"Cold trainer stats ({tr:.0f}/100)")
    if jk >= 75:
        strengths.append(f"Strong jockey ({jk:.0f}/100)")
    elif jk < 40:
        weaknesses.append(f"Weak jockey stats ({jk:.0f}/100)")
    
    # Intent flags
    flags = horse_row.get("intent_flags", [])
    if isinstance(flags, list) and flags and flags[0] != "No strong signals":
        for flag in flags[:2]:
            strengths.append(f"Positive intent signal: {flag}")
    
    # Layoff
    layoff = horse_row.get("layoff_factor", 0)
    if layoff >= 2:
        strengths.append("Sharp - recent race fitness confirmed")
    elif layoff <= -3:
        weaknesses.append("Layoff concern - may need a race to get fit")
    
    # Value
    vl = str(horse_row.get("value_label", ""))
    edge = horse_row.get("edge_percent", 0)
    if pd.isna(edge):
        edge = 0
    if vl == "Overlay" and edge >= 15:
        strengths.append(f"Value play: {edge:+.0f}% edge over morning line")
    elif vl == "Underlay":
        weaknesses.append("Underlay - shorter odds than fair value suggests")
    
    return {
        "strengths": strengths if strengths else ["No standout strengths"],
        "weaknesses": weaknesses if weaknesses else ["No major red flags"],
    }


def generate_longshot_analysis(horse_row):
    """
    For wildcard/longshot horses, generate detailed scenario analysis.
    Returns: label, why_dangerous, what_must_happen, best_usage
    """
    wp = horse_row.get("win_probability", 0)
    if pd.isna(wp):
        wp = 0
    
    label = "WILDCARD PLAY" if wp >= 8 else "LONGSHOT VALUE"
    
    # WHY DANGEROUS
    dangerous_reasons = []
    scenario = str(horse_row.get("pace_scenario", ""))
    ep = horse_row.get("early_pace_norm", 50)
    lp = horse_row.get("late_pace_norm", 50)
    form = str(horse_row.get("form_trend", ""))
    vl = str(horse_row.get("value_label", ""))
    edge = horse_row.get("edge_percent", 0)
    if pd.isna(edge):
        edge = 0
    
    if "Lone Speed" in scenario:
        dangerous_reasons.append("Could steal it on an uncontested lead")
    if lp >= 70:
        dangerous_reasons.append("Strong closer that could blow by tiring leaders")
    if form == "Improving":
        dangerous_reasons.append("Improving form suggests not at peak yet")
    if vl == "Overlay" and edge >= 20:
        dangerous_reasons.append(f"Significant overlay ({edge:+.0f}%) - market undervaluing")
    if horse_row.get("class_move_label", "") == "Down":
        dangerous_reasons.append("Class drop - easier company today")
    if ep >= 75:
        dangerous_reasons.append("Elite gate speed - could wire the field")
    
    # WHAT MUST HAPPEN
    scenarios = []
    if "Lone Speed" in scenario:
        scenarios.append("Needs to get loose early without pressure")
    elif "Pace Pressure" in scenario:
        scenarios.append("Needs the pace to collapse - fast early fractions")
    elif lp >= 70:
        scenarios.append("Needs an honest pace to set up for late run")
    else:
        scenarios.append("Needs a trouble-free trip and best effort")
    
    if horse_row.get("bounce_flag", False):
        scenarios.append("Must avoid regression/bounce off recent peak")
    
    # BEST USAGE
    if wp >= 10:
        usage = "Win small / Underneath in exactas and trifectas"
    elif wp >= 5:
        usage = "Exotics only - key underneath in trifectas/superfectas"
    else:
        usage = "Deep exotics / superfecta filler only"
    
    return {
        "label": label,
        "why_dangerous": dangerous_reasons if dangerous_reasons else ["Sneaky contender at a price"],
        "what_must_happen": scenarios,
        "best_usage": usage,
    }


def _get_key_reasons(horse_row, max_reasons=2):
    """Extract top key reasons for quick look line."""
    reasons = []
    
    scenario = str(horse_row.get("pace_scenario", ""))
    if scenario and scenario != "Stalker Setup":
        reasons.append(scenario)
    
    form = str(horse_row.get("form_trend", ""))
    if form == "Improving":
        reasons.append("improving form")
    
    if horse_row.get("class_move_label", "") == "Down":
        reasons.append("class drop")
    
    if horse_row.get("bounce_flag", False):
        reasons.append("bounce risk")
    
    vl = str(horse_row.get("value_label", ""))
    if vl == "Overlay":
        edge = horse_row.get("edge_percent", 0)
        if pd.isna(edge):
            edge = 0
        reasons.append(f"{edge:+.0f}% edge" if edge != 0 else "overlay")
    
    if not reasons:
        ep = horse_row.get("early_pace_norm", 50)
        lp = horse_row.get("late_pace_norm", 50)
        if ep >= 70:
            reasons.append("speed threat")
        elif lp >= 70:
            reasons.append("closer")
        else:
            reasons.append("balanced profile")
    
    return reasons[:max_reasons]


def generate_race_summary(horses_df):
    """Generate overall race summary text."""
    active_df = horses_df[~horses_df.get("scratched", pd.Series([False] * len(horses_df), index=horses_df.index))].copy()
    
    if len(active_df) == 0:
        return "No active horses to summarize."
    
    lines = []
    lines.append(f"**Race Analysis: {len(active_df)} runners**")
    
    # Top contenders
    top3 = active_df.nsmallest(3, "power_rank")
    lines.append("\n**Top Contenders:**")
    for _, row in top3.iterrows():
        name = row.get("horse_name", "?")
        grade = row.get("overall_grade", "D")
        wp = row.get("win_probability", 0)
        if pd.isna(wp):
            wp = 0
        vl = str(row.get("value_label", ""))
        lines.append(f"- {name}: Grade {grade}, {wp:.0f}% win, {vl}")
    
    # Race character
    chalk_chaos = ""
    if "chalk_chaos" in active_df.attrs:
        chalk_chaos = active_df.attrs["chalk_chaos"]
    
    if chalk_chaos:
        lines.append(f"\n**Race Character:** {chalk_chaos}")
    
    # Longshots
    from model.grading import get_wildcard_label
    longshots = []
    for _, row in active_df.iterrows():
        label, _ = get_wildcard_label(row)
        if label:
            longshots.append(row.get("horse_name", "?"))
    
    if longshots:
        lines.append(f"\n**Wildcard/Longshot Interest:** {', '.join(longshots)}")
    
    return "\n".join(lines)
