"""
validators.py - Input validation and warning generation for the handicapping model.
"""

import pandas as pd
import numpy as np


def validate_race_header(track_code, surface, distance, race_type, condition):
    """Validate race header inputs and return errors/warnings."""
    errors = []
    warnings = []
    
    if not track_code or track_code.strip() == "":
        errors.append("Track code is required. Select a track from the dropdown.")
    
    if not surface or surface.strip() == "":
        errors.append("Surface is required. Choose Dirt, Turf, or other available surface.")
    
    if distance is None or distance <= 0:
        errors.append("Distance must be a positive number (in furlongs).")
    
    if not race_type or race_type.strip() == "":
        errors.append("Race type is required. Select from the dropdown (e.g., MDN, CLM, ALW, STK).")
    
    if not condition or condition.strip() == "":
        warnings.append("Track condition not specified. Will use 'Fast' / 'Firm' as default.")
    
    return errors, warnings


def validate_horse_data(horse_df):
    """Validate horse input DataFrame and return errors/warnings."""
    errors = []
    warnings = []
    
    if horse_df is None or len(horse_df) == 0:
        errors.append("No horses entered. Add at least 2 horses to run the model.")
        return errors, warnings
    
    if len(horse_df) < 2:
        warnings.append("Only 1 horse entered. Need at least 2 for meaningful comparison.")
    
    # Check required columns exist
    required_cols = ["horse_name", "post_position"]
    for col in required_cols:
        if col not in horse_df.columns:
            errors.append(f"Missing required column: {col}")
    
    # Check for duplicate post positions
    if "post_position" in horse_df.columns:
        posts = horse_df["post_position"].dropna()
        if len(posts) != len(set(posts)):
            warnings.append("Duplicate post positions detected. Check entries.")
    
    # Check for duplicate horse names
    if "horse_name" in horse_df.columns:
        names = horse_df["horse_name"].dropna()
        if len(names) != len(set(names)):
            warnings.append("Duplicate horse names detected.")
    
    # Check for scratched horses (all scratched)
    if "scratched" in horse_df.columns:
        active = horse_df[~horse_df["scratched"].fillna(False)]
        if len(active) < 2:
            errors.append("Fewer than 2 active (non-scratched) horses. Need at least 2.")
    
    # Check morning line odds
    if "morning_line" in horse_df.columns:
        odds = horse_df["morning_line"].dropna()
        if len(odds) == 0:
            warnings.append("No morning line odds entered. Value detection will be limited.")
    
    # Check for missing PP data
    if "last_race_date" in horse_df.columns:
        missing_pp = horse_df["last_race_date"].isna().sum()
        if missing_pp > 0:
            warnings.append(f"{missing_pp} horse(s) missing recent race data. Patterns may be less reliable.")
    
    return errors, warnings


def get_validation_summary(horse_df):
    """Generate a friendly validation summary for the user."""
    errors, warnings = validate_horse_data(horse_df)
    
    summary = []
    if errors:
        summary.append(f"**{len(errors)} Error(s):** " + "; ".join(errors))
    if warnings:
        summary.append(f"**{len(warnings)} Warning(s):** " + "; ".join(warnings))
    
    if not errors and not warnings:
        summary.append("**All checks passed!** Ready to run the model.")
    
    return "\n\n".join(summary), len(errors) == 0


def check_data_quality(horses_df):
    """Assess overall data quality and provide feedback."""
    quality_score = 100
    issues = []
    
    if horses_df is None or len(horses_df) == 0:
        return 0, ["No horse data available."]
    
    # Check completeness
    for col in ["speed_figure", "class_rating", "trainer_pct", "jockey_pct"]:
        if col in horses_df.columns:
            missing_pct = horses_df[col].isna().mean() * 100
            if missing_pct > 50:
                quality_score -= 20
                issues.append(f"Many horses missing {col} - estimates less reliable")
            elif missing_pct > 20:
                quality_score -= 10
                issues.append(f"Some horses missing {col}")
    
    # Check PP recency
    if "days_since_race" in horses_df.columns:
        old_races = (horses_df["days_since_race"] > 90).sum()
        if old_races > 0:
            quality_score -= 10
            issues.append(f"{old_races} horse(s) with PP > 90 days old")
    
    # Check for heavy favorites
    if "morning_line" in horses_df.columns:
        ml = horses_df["morning_line"].dropna()
        if len(ml) > 0 and ml.min() < 1.0:
            issues.append("Heavy favorite detected (< 1-1 odds) - may be underlay")
    
    return max(quality_score, 0), issues
