"""
How To Use page - Step-by-step guide for beginners.
"""

import streamlit as st

st.set_page_config(page_title="How To Use", page_icon="📖", layout="wide")

st.sidebar.page_link("app.py", label="← Back to Race Setup", icon="🏇")

st.title("📖 How To Use")

st.markdown("""
Welcome to the **Pro Elite Horse Race Handicapping App**! This guide walks you through 
every step from race setup to betting decisions and results tracking.
""")

# ---------------------------------------------------------------------------
# Step-by-Step Guide
# ---------------------------------------------------------------------------

st.header("Step-by-Step Workflow")

steps = [
    (
        "1️⃣ Race Setup",
        """Configure the race parameters on the main page. Select the track, surface, distance, race type, 
        track condition, and weather. Click **Apply Presets** to load the appropriate weight multipliers 
        for this specific race configuration. The app automatically stacks presets in order: 
        Track → Surface/Distance → Race Type → Condition → Weather.""",
        "💡 Tip: If you're unsure about a setting, check the track's official program or racing form."
    ),
    (
        "2️⃣ Enter Horse Data",
        """Add horses using one of three methods: **Manual Entry** (fill out the form for each horse), 
        **Load Sample Race** (pre-loaded demo data for learning), or **Upload CSV** (bulk import). 
        For each horse, enter: name, post position, morning line odds, speed figure, pace ratings, 
        class rating, trainer/jockey stats, and recent form.""",
        "💡 Tip: Start with the sample race to see how everything works before entering your own data."
    ),
    (
        "3️⃣ Run the Model",
        """Click **Run Model** to generate ratings, probabilities, fair odds, and grades. 
        The model processes: Speed & Pace → Class & Form → Trainer/Jockey → Composite Rating 
        → Win/Place/Show Probabilities → Grading (A/B/C/D).""",
        "💡 Tip: Use the 'Min Edge %' slider to set your minimum value threshold."
    ),
    (
        "4️⃣ Review the Dashboard",
        """The Dashboard shows: Quick Picks (top win pick, best value, longshot, safest place/show), 
        a Bet/Pass recommendation, and a full rankings table. Each horse gets grades for Overall, 
        Win, Place, and Show.""",
        "💡 Tip: Quick Look summaries give you the essential info in one line per horse."
    ),
    (
        "5️⃣ Read Horse Cards",
        """Click into **Horse Cards** to drill down on individual horses. See detailed commentary: 
        strengths, weaknesses, pace scenario, connections, and wildcard/longshot analysis.""",
        "💡 Tip: Toggle off Beginner Mode in the sidebar to see full component breakdowns."
    ),
    (
        "6️⃣ Make Your Decision",
        """Use the Bet/Pass recommendation as guidance. The app flags overlays (potential value), 
        underlays (poor value), and pass races (too uncertain). Consider your bankroll and risk tolerance.""",
        "⚠️ Remember: No model guarantees winners. Always bet responsibly and within your means."
    ),
    (
        "7️⃣ Log Results",
        """After the race, log the actual results on the Dashboard or Results & ROI page. 
        Enter the finish position and payouts. This builds your performance database for ROI tracking.""",
        "💡 Tip: Consistent logging is key to understanding your true performance over time."
    ),
]

for title, content, tip in steps:
    with st.expander(title, expanded=False):
        st.markdown(content)
        st.info(tip)

st.divider()

# ---------------------------------------------------------------------------
# Understanding Grades
# ---------------------------------------------------------------------------

st.header("Understanding Grades")

st.markdown("""
Each horse receives four grades. Here's what they mean:
""")

grade_data = [
    ("A", "🟢 Green", "Strong contender. Top composite rating with 25%+ win probability and value (overlay or fair). Best betting candidates."),
    ("B", "🔵 Blue", "Competitive. 15-24% win probability. Viable contenders, especially if overlay."),
    ("C", "🟡 Amber", "Marginal. 8-14% win probability. Use underneath in exactas and trifectas, not win bets."),
    ("D", "🔴 Red", "Weak. Under 8% win probability or clear underlay. Generally avoid."),
]

for grade, color, meaning in grade_data:
    st.markdown(f"**{grade}** ({color}): {meaning}")

st.markdown("""
**Grade Types:**
- **Overall Grade**: Combined assessment of composite rating + value
- **Win Grade**: Based purely on win probability and value
- **Place Grade**: A=60%+ place prob, B=45-59%, C=30-44%, D=<30%
- **Show Grade**: A=75%+ show prob, B=60-74%, C=45-59%, D=<45%
""")

st.divider()

# ---------------------------------------------------------------------------
# Understanding Value
# ---------------------------------------------------------------------------

st.header("Understanding Value (Overlay/Underlay)")

st.markdown("""
**Value** compares the morning line (or actual) odds to the model's calculated fair odds:

| Label | Meaning | Action |
|-------|---------|--------|
| **Overlay** 💰 | Fair odds > ML odds. The model thinks the horse is UNDER-valued by the market. | **Potential bet** - positive expected value |
| **Underlay** ⚠️ | Fair odds < ML odds. The model thinks the horse is OVER-valued. | **Avoid** - negative expected value |
| **Fair** 🎯 | Fair odds ≈ ML odds. Correctly priced. | **Neutral** - no edge either way |

**Edge %** shows exactly how much overlay/underlay exists. For example, +25% edge means 
the model's fair odds are 25% higher than the morning line, suggesting value.
""")

st.divider()

# ---------------------------------------------------------------------------
# Icons Legend
# ---------------------------------------------------------------------------

st.header("Icons & Symbols")

icons = [
    ("⭐", "Top Pick", "Highest composite rating in the race"),
    ("💰", "Overlay/Value", "Horse is under-valued by the market"),
    ("⚠️", "Risk/Underlay", "Horse is over-valued - likely poor bet"),
    ("🧩", "Wildcard/Longshot", "Low win% but dangerous in specific scenarios"),
    ("🎯", "Key/Exotics", "Safe for place/show or underneath in exotic bets"),
    ("✅", "BET", "Model recommends a bet on this race"),
    ("❌", "PASS", "Model recommends passing this race"),
]

for icon, name, meaning in icons:
    st.markdown(f"**{icon} {name}**: {meaning}")

st.divider()

# ---------------------------------------------------------------------------
# Beginner vs Advanced Mode
# ---------------------------------------------------------------------------

st.header("Beginner vs Advanced Mode")

st.markdown("""
Toggle between modes using the switch in the left sidebar:

**Beginner Mode (default):**
- Shows simplified views: Quick Picks, Grades, Win%, Fair Odds, Value, Bet/Pass
- One-line summaries for each horse
- Cleaner interface with less clutter

**Advanced Mode:**
- Reveals full component breakdowns with weighted scores
- Shows preset stacking details and weight multipliers
- Displays pace scenarios, energy distribution, and intent flags
- Access to raw data tables

**Recommendation:** Start in Beginner Mode. Switch to Advanced when you want to understand 
*why* the model made a specific recommendation.
""")

st.divider()

# ---------------------------------------------------------------------------
# Quick Start Guide
# ---------------------------------------------------------------------------

st.header("Quick Start: Your First Race")

st.markdown("""
1. On the main page, click **Load Sample Race (TB)** - this fills in everything automatically
2. Click **Run Model** - wait a moment for processing
3. Navigate to **Dashboard** - see the Quick Picks and rankings
4. Click **Horse Cards** - explore individual horse analysis
5. Return to main page - click **Load Sample Race (QH)** to see Quarter Horse data
6. Try changing the **Min Edge %** slider and re-running to see different recommendations

Once comfortable, enter your own race data using Manual Entry or CSV upload!
""")
