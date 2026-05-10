"""
database.py - SQLite database for results logging and settings persistence.
"""

import sqlite3
import pandas as pd
import os
from datetime import datetime

DB_PATH = os.path.join("data", "app.db")


def get_connection():
    """Get SQLite connection with row factory."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize the database with required tables."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Results table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            race_key TEXT NOT NULL,
            track_code TEXT NOT NULL,
            race_date TEXT NOT NULL,
            race_number INTEGER NOT NULL,
            breed TEXT,
            surface TEXT,
            distance TEXT,
            race_type TEXT,
            condition TEXT,
            horse_name TEXT NOT NULL,
            post_position INTEGER,
            finish_position INTEGER,
            win_probability REAL,
            fair_odds_win REAL,
            morning_line REAL,
            actual_odds REAL,
            payout_win REAL DEFAULT 0,
            payout_place REAL DEFAULT 0,
            payout_show REAL DEFAULT 0,
            overall_grade TEXT,
            value_label TEXT,
            bet_recommendation TEXT,
            logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Settings table (for user preferences)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Performance summary view (materialized via query)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS performance_cache (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            category_value TEXT NOT NULL,
            bets INTEGER DEFAULT 0,
            wins INTEGER DEFAULT 0,
            places INTEGER DEFAULT 0,
            shows INTEGER DEFAULT 0,
            total_staked REAL DEFAULT 0,
            total_returned REAL DEFAULT 0,
            roi_pct REAL DEFAULT 0,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(category, category_value)
        )
    """)
    
    conn.commit()
    conn.close()


def log_result(result_dict):
    """
    Log a race result.
    result_dict must contain: race_key, track_code, race_date, race_number,
    horse_name, finish_position, win_probability, fair_odds_win, morning_line,
    actual_odds, payout_win, payout_place, payout_show, overall_grade, value_label, bet_recommendation
    Optional: breed, surface, distance, race_type, condition, post_position
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO results (
            race_key, track_code, race_date, race_number, breed, surface,
            distance, race_type, condition, horse_name, post_position,
            finish_position, win_probability, fair_odds_win, morning_line,
            actual_odds, payout_win, payout_place, payout_show,
            overall_grade, value_label, bet_recommendation
        ) VALUES (
            :race_key, :track_code, :race_date, :race_number, :breed, :surface,
            :distance, :race_type, :condition, :horse_name, :post_position,
            :finish_position, :win_probability, :fair_odds_win, :morning_line,
            :actual_odds, :payout_win, :payout_place, :payout_show,
            :overall_grade, :value_label, :bet_recommendation
        )
    """, result_dict)
    
    conn.commit()
    conn.close()
    return cursor.lastrowid


def get_all_results():
    """Get all logged results as DataFrame."""
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM results ORDER BY logged_at DESC", conn)
    conn.close()
    return df


def get_results_by_track(track_code):
    """Get results filtered by track."""
    conn = get_connection()
    df = pd.read_sql_query(
        "SELECT * FROM results WHERE track_code = ? ORDER BY logged_at DESC",
        conn, params=(track_code,)
    )
    conn.close()
    return df


def delete_result(result_id):
    """Delete a result by ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM results WHERE id = ?", (result_id,))
    conn.commit()
    conn.close()


def export_results_csv(filepath=None):
    """Export all results to CSV."""
    df = get_all_results()
    if filepath:
        df.to_csv(filepath, index=False)
    return df


def get_roi_summary(category="track"):
    """
    Compute ROI summary by category (track, surface, distance, race_type, condition).
    Returns DataFrame with ROI%, hit rate, etc.
    """
    conn = get_connection()
    
    category_col = category
    query = f"""
        SELECT 
            {category_col} as category_value,
            COUNT(*) as total_bets,
            SUM(CASE WHEN finish_position = 1 THEN 1 ELSE 0 END) as wins,
            SUM(CASE WHEN finish_position <= 2 THEN 1 ELSE 0 END) as places,
            SUM(CASE WHEN finish_position <= 3 THEN 1 ELSE 0 END) as shows,
            SUM(payout_win) as win_return,
            SUM(payout_place) as place_return,
            SUM(payout_show) as show_return,
            SUM(payout_win + payout_place + payout_show) as total_return,
            AVG(win_probability) as avg_win_prob
        FROM results
        WHERE {category_col} IS NOT NULL
        GROUP BY {category_col}
        ORDER BY total_bets DESC
    """
    
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    if df.empty:
        return df
    
    # Assume $2 base bet per entry for ROI calc
    df["total_staked"] = df["total_bets"] * 2.0
    df["roi_pct"] = ((df["total_return"] - df["total_staked"]) / df["total_staked"] * 100).round(1)
    df["win_rate"] = (df["wins"] / df["total_bets"] * 100).round(1)
    df["place_rate"] = (df["places"] / df["total_bets"] * 100).round(1)
    
    return df


def set_setting(key, value):
    """Set a user setting."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO settings (key, value, updated_at)
        VALUES (?, ?, CURRENT_TIMESTAMP)
    """, (key, str(value)))
    conn.commit()
    conn.close()


def get_setting(key, default=None):
    """Get a user setting."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
    row = cursor.fetchone()
    conn.close()
    return row["value"] if row else default


def get_recent_races(limit=10):
    """Get recent unique races."""
    conn = get_connection()
    df = pd.read_sql_query("""
        SELECT DISTINCT race_key, track_code, race_date, race_number, surface, distance, race_type
        FROM results
        ORDER BY race_date DESC, race_number DESC
        LIMIT ?
    """, conn, params=(limit,))
    conn.close()
    return df
