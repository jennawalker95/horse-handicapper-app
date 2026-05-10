"""
FAQ & Troubleshooting page - Common questions, symptoms, causes, and solutions.
"""

import streamlit as st

st.set_page_config(page_title="FAQ & Troubleshooting", page_icon="🔧", layout="wide")

st.sidebar.page_link("app.py", label="← Back to Race Setup", icon="🏇")

st.title("🔧 FAQ & Troubleshooting")

# ---------------------------------------------------------------------------
# FAQ Section
# ---------------------------------------------------------------------------

st.header("Frequently Asked Questions")

faqs = [
    (
        "Why is the favorite graded poorly?",
        """Favorites can receive low grades for several reasons:
        - **Underlay**: The morning line odds are shorter than the model's fair odds, meaning 
          there's no betting value. A 2-1 favorite with only 20% true win probability is a bad bet.
        - **Bounce Risk**: The model detects the horse may regress off a recent peak performance.
        - **Pace Pressure**: The horse faces pace pressure that could compromise its chances.
        - **Class Move Up**: The horse is stepping up in class and may not handle tougher competition.
        
        **Remember**: The grade is about *betting value*, not just win probability. 
        A horse can be the most likely winner and still be a bad bet at the offered odds."""
    ),
    (
        "What is an overlay?",
        """An **overlay** is a horse whose fair odds (calculated by the model) are HIGHER than 
        the morning line odds. This means the market is offering better odds than the horse 
        deserves based on its assessed probability.
        
        **Example**: Model calculates 25% win probability = fair odds of 3-1. 
        Morning line is 5-1. The 5-1 odds are a bargain - you're getting paid more than 
        the true probability suggests. This is an overlay.
        
        **Overlay = potential value. Underlay = poor value.**"""
    ),
    (
        "Why did the model say PASS?",
        """The model recommends PASS when:
        - No horse has a clear A-grade with positive edge
        - The race is too wide open (many horses with similar ratings)
        - The favorite is a significant underlay
        - The field size is too large (14+ runners = chaos)
        - The race type is highly volatile (e.g., maiden races with first-time starters)
        - Missing data makes predictions unreliable
        
        **PASS is a valid decision.** Not betting is often the smartest play."""
    ),
    (
        "What do the pace scenarios mean?",
        """**Lone Speed**: One horse has significantly more early speed than the field. 
        Could wire the field if unchallenged.
        
        **Pace Pressure**: Multiple horses with strong early speed. Likely duel and 
        tire, setting up for closers.
        
        **Pace Collapse Threat**: Fast early fractions expected to fall apart, 
        favoring horses with strong late pace.
        
        **Dual Threat**: Horse has both early and late speed - dangerous if pace unfolds favorably.
        
        **Closer Friendly**: Expected to produce a pace meltdown, ideal for deep closers.
        
        **Stalker Setup**: Honest pace expected, favoring horses that sit just off the lead."""
    ),
    (
        "How accurate is the model?",
        """The model uses proven handicapping principles: speed figures, pace analysis, 
        class assessment, and connections evaluation. However:
        
        - No model predicts winners with certainty
        - Horse racing has inherent randomness (trip trouble, bad starts, etc.)
        - The model identifies *value* and *probability*, not guaranteed outcomes
        - Track your results over time to assess the model's performance for your betting style
        
        **Use the model as a tool to identify value, not as a crystal ball.**"""
    ),
    (
        "What's the difference between TB and QH?",
        """**Thoroughbred (TB)**: Longer distances (typically 5-12 furlongs), more emphasis 
        on stamina, pace dynamics are complex with multiple phases. Two-turn races are common.
        
        **Quarter Horse (QH)**: Very short distances (300-870 yards), break/gate speed 
        is paramount, less emphasis on late pace. Mostly one-turn or straightaway races.
        
        The app adjusts presets and weight emphasis automatically based on breed selection."""
    ),
    (
        "How do I interpret the confidence score?",
        """The **Race Confidence** score (0-100%) indicates how confident the model is 
        in its overall assessment:
        
        - **80-100%**: Clear separation between horses, strong favorites, reliable data
        - **60-79%**: Moderate confidence, decent structure to the race
        - **40-59%**: Uncertain race, closely matched, or limited data
        - **0-39%**: Highly uncertain - consider passing
        
        Higher confidence doesn't guarantee winners, but the model's assessments are 
        more reliable when confidence is high."""
    ),
    (
        "Can I change the grade thresholds?",
        """The grade thresholds are fixed to ensure consistency. However, you can adjust 
        the **Min Edge %** slider to control how strict the value detection is. 
        
        A higher min edge means only horses with significant overlay get BET recommendations. 
        A lower min edge means more horses qualify as potential bets.
        
        Advanced users can also override individual component weights in the Presets Inspector."""
    ),
]

for question, answer in faqs:
    with st.expander(question):
        st.markdown(answer)

st.divider()

# ---------------------------------------------------------------------------
# Troubleshooting Section
# ---------------------------------------------------------------------------

st.header("Troubleshooting")

troubleshooting = [
    (
        "App not updating after entering data",
        [
            "Click **Apply Presets** after changing track/surface/distance",
            "Click **Run Model** after adding horses",
            "If nothing changes, try clicking **Run Model** again",
            "Check that at least 2 horses are entered and not scratched",
        ]
    ),
    (
        "'No model results yet' message on Dashboard",
        [
            "You must click **Run Model** on the main page first",
            "Ensure at least 2 non-scratched horses are entered",
            "Check that required fields (name, post position) are filled",
            "Try loading a sample race to verify the workflow",
        ]
    ),
    (
        "Model returns all D grades",
        [
            "Check that speed figures and ratings are entered (not all zero)",
            "Ensure morning line odds are reasonable (not all 99-1)",
            "Verify at least 2 horses have meaningful data",
            "Check that presets were applied before running the model",
        ]
    ),
    (
        "Preset stacking looks wrong",
        [
            "Verify track code is correct in the dropdown",
            "Check surface matches the track (some tracks don't have turf)",
            "Distance should be in furlongs (1 mile = 8 furlongs)",
            "Click **Reset to Default Weights** in Presets Inspector, then re-apply",
        ]
    ),
    (
        "CSV upload fails",
        [
            "CSV must have **horse_name** and **post_position** columns",
            "Check file encoding (UTF-8 recommended)",
            "Ensure no special characters in column names",
            "Try opening the CSV in a text editor to check formatting",
        ]
    ),
    (
        "Results not saving to database",
        [
            "The /data directory must be writable",
            "Check that you filled in the required fields (horse name, finish position)",
            "Try the manual entry form on the Results & ROI page",
            "Restarting the app will reset the session but keep the SQLite database",
        ]
    ),
    (
        "Dashboard shows empty or strange values",
        [
            "Re-run the model after making changes to horse data",
            "Check for scratched horses being the only ones entered",
            "Verify morning line odds are reasonable values",
            "Toggle Beginner Mode off/on to refresh the view",
        ]
    ),
]

for problem, solutions in troubleshooting:
    with st.expander(problem):
        st.markdown("**Solutions:**")
        for i, sol in enumerate(solutions, 1):
            st.markdown(f"{i}. {sol}")

st.divider()

# ---------------------------------------------------------------------------
# Reset & Recovery
# ---------------------------------------------------------------------------

st.header("Reset & Recovery")

st.markdown("""
If the app seems to be in a bad state, try these steps in order:

1. **Refresh Presets**: Go to main page and click **Apply Presets** again
2. **Re-run Model**: After any data changes, always click **Run Model**
3. **Reset Weights**: Go to Presets Inspector and click **Reset to Default Weights**
4. **Reload Sample**: Load a sample race to verify the app is working
5. **Clear Session**: Refresh the browser page to clear session state
6. **Restart App**: Stop and restart Streamlit completely
""")

if st.button("Clear Current Session Data", use_container_width=True):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.success("Session cleared! The page will refresh.")
    st.rerun()
