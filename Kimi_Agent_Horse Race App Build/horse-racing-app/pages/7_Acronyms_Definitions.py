"""
Acronyms & Definitions page - Full searchable glossary with terms, definitions, and examples.
"""

import streamlit as st
import pandas as pd

st.set_page_config(page_title="Acronyms & Definitions", page_icon="📚", layout="wide")

st.sidebar.page_link("app.py", label="← Back to Race Setup", icon="🏇")

st.title("📚 Acronyms & Definitions")

st.markdown("Search the full glossary of horse racing terms, track codes, race types, betting terminology, and model-specific language.")

# ---------------------------------------------------------------------------
# Glossary Data
# ---------------------------------------------------------------------------

glossary_data = [
    # Track codes (sample - not exhaustive)
    ("AQU", "Aqueduct", "Track", "New York Racing Association track in Queens, NY. Hosts winter/spring meet. Inner and outer turf courses.", "AQU 6F dirt race"),
    ("BEL", "Belmont Park", "Track", "Premier track in Elmont, NY. Home of the Belmont Stakes. Has two turf courses and a main dirt track.", "BEL 1-1/2M turf"),
    ("CD", "Churchill Downs", "Track", "Legendary track in Louisville, KY. Home of the Kentucky Derby (first Saturday in May).", "CD 1-1/4M KY Derby"),
    ("DRC", "Del Mar Racetrack", "Track", "Track in Del Mar, CA. Famous slogan 'Where the turf meets the surf.' Summer meet.", "DRC 1M Pacific Classic"),
    ("GP", "Gulfstream Park", "Track", "Premier Florida track in Hallandale Beach. Hosts Championship Meet in winter/spring.", "GP 1-1/8M Pegasus"),
    ("KEE", "Keeneland", "Track", "World-class track in Lexington, KY. Famous for April and October meets. Beautiful turf course.", "KEE 1-1/8M Blue Grass"),
    ("LBG", "Los Alamitos", "Track", "Premier Quarter Horse track in Cypress, CA. Also runs TB in winter. Home of major QH stakes.", "LBG 400y QH Championship"),
    ("OP", "Oaklawn Park", "Track", "Track in Hot Springs, AR. Strong winter/spring meet including Arkansas Derby.", "OP 1-1/8M Arkansas Derby"),
    ("SA", "Santa Anita", "Track", "Flagship California track in Arcadia. Hosts major races including Santa Anita Derby and Big Cap.", "SA 1-1/4M Big Cap"),
    ("SAR", "Saratoga", "Track", "Historic summer meet in Saratoga Springs, NY. Premier racing destination since 1863.", "SAR 1-1/4M Travers"),
    ("RP", "Remington Park", "Track", "Major Oklahoma track in Oklahoma City. Mixed TB and QH meet.", "RP 400y Remington Park Futurity"),
    ("LRL", "Laurel Park", "Track", "Maryland track with year-round racing. Hosts major mid-Atlantic stakes.", "LRL 1M Maryland Million"),
    ("MTH", "Monmouth Park", "Track", "New Jersey track with summer meet. Home of the Haskell Stakes.", "MTH 1-1/8M Haskell"),
    ("FG", "Fair Grounds", "Track", "New Orleans track with winter/spring meet. Home of Louisiana Derby.", "FG 1-1/8M Louisiana Derby"),
    ("RET", "Remington Park", "Track", "Oklahoma City track with strong QH focus. Major Heritage Place sales trials.", "RET 350y QH trial"),
    ("SUN", "Sunland Park", "Track", "New Mexico track near El Paso. Hosts Sunland Derby and QH stakes.", "SUN 1-1/8M Sunland Derby"),
    ("TUP", "Turf Paradise", "Track", "Phoenix, Arizona track with winter meet. One of the oldest in the West.", "TUP 1M Turf Paradise Derby"),
    ("PRX", "Parx Racing", "Track", "Pennsylvania track (formerly Philadelphia Park). Home of PA Derby.", "PRX 1-1/8M PA Derby"),
    ("WRD", "Will Rogers Downs", "Track", "Oklahoma track with year-round racing. TB and mixed meets.", "WRD 6F Oklahoma Derby prep"),
    
    # Race types
    ("MDN", "Maiden Special Weight", "Race Type", "Race for horses that have never won. No claiming price. High volatility due to inexperience.", "MDN 6F dirt - 2-year-old debut"),
    ("MDN-C", "Maiden Claiming", "Race Type", "Maiden race where horses can be claimed for a set price. Often attracts class droppers.", "MDN-C 16k - claiming price $16,000"),
    ("CLM", "Claiming", "Race Type", "Horses run for a specified claiming price. New owner can buy horse out of race for that price.", "CLM 25k - $25,000 claiming tag"),
    ("OC", "Optional Claimer", "Race Type", "Race where some horses run for a claiming price and others run for allowance conditions.", "OC 80k/N1X - optional 80k or non-winners 1x"),
    ("ALW", "Allowance", "Race Type", "Non-claiming race with specific conditions (e.g., non-winners of 2 lifetime).", "ALW N2X - non-winners 2x lifetime"),
    ("AOC", "Allowance Optional Claiming", "Race Type", "Allowance race with optional claiming component.", "AOC 62.5k/N1X"),
    ("STK", "Stakes", "Race Type", "Race with significant purse. Higher class level. Graded (G1/G2/G3) or non-graded.", "STK $500k purse - stakes race"),
    ("G1", "Grade 1 Stakes", "Race Type", "Highest level of stakes race in North America. Elite competition.", "G1 Kentucky Derby, G1 Breeders' Cup"),
    ("G2", "Grade 2 Stakes", "Race Type", "Second-tier stakes race. Very high quality.", "G2 Blue Grass Stakes"),
    ("G3", "Grade 3 Stakes", "Race Type", "Third-tier stakes race. Quality competition.", "G3 Sham Stakes"),
    ("HCP", "Handicap", "Race Type", "Race where horses carry different weights based on ability. Weight assignments by racing secretary.", "HCP 1-1/4M - assigned weights"),
    ("QH-TR", "QH Trial", "Race Type", "Quarter Horse trial race used to qualify for championship finals.", "QH-TR 350y - Heritage Place trial"),
    ("QH-FN", "QH Final", "Race Type", "Quarter Horse championship final. Elite QH competition.", "QH-FN 440y - Heritage Place final"),
    ("QH-MDN", "QH Maiden", "Race Type", "Quarter Horse maiden race for non-winners. Break speed is critical.", "QH-MDN 300y - maiden debut"),
    ("QH-STK", "QH Stakes", "Race Type", "Quarter Horse stakes race with significant purse.", "QH-STK 400y - Los Alamitos Championship"),
    
    # Betting terms
    ("W", "Win", "Betting", "Bet on a horse to finish first. Simplest bet type.", "$2 Win on #5"),
    ("P", "Place", "Betting", "Bet on a horse to finish first or second. Pays less than win but higher hit rate.", "$2 Place on #3"),
    ("S", "Show", "Betting", "Bet on a horse to finish first, second, or third. Safest but lowest payout.", "$2 Show on #8"),
    ("WP", "Win-Place", "Betting", "Equal bets on win and place. Common conservative approach.", "$2 WP = $2 win + $2 place"),
    ("EX", "Exacta", "Betting", "Pick first and second place in exact order.", "$2 Exacta 5-3"),
    ("TRI", "Trifecta", "Betting", "Pick first, second, and third in exact order. Higher payouts.", "$1 Trifecta 5-3-8"),
    ("SUP", "Superfecta", "Betting", "Pick first through fourth in exact order. Very high payouts.", "$0.10 Superfecta box 5-3-8-1"),
    ("Overlay", "Overlay", "Betting", "When a horse's odds are higher than its true probability suggests. Value situation.", "5-1 overlay when fair is 3-1"),
    ("Underlay", "Underlay", "Betting", "When a horse's odds are lower than its true probability suggests. Poor value.", "2-1 underlay when fair is 5-1"),
    ("Chalk", "Chalk", "Betting", "The betting favorite. Often overbet by the public.", "The chalk came in at even money"),
    ("Longshot", "Longshot", "Betting", "Horse with high odds and low perceived win probability. Usually 10-1 or higher.", "50-1 longshot won the race"),
    ("Box", "Box", "Betting", "Bet covering all combinations of selected horses. Costs more but doesn't require exact order.", "$1 Trifecta box 3-5-8 = $6 total"),
    ("Key", "Key", "Betting", "Using one horse in multiple exotic combinations. Horse must perform as expected.", "Key #5 in exacta with 3,8"),
    ("Edge", "Edge", "Betting", "Mathematical advantage over the market. Positive edge = potential profit long-term.", "+25% edge means 25% overlay"),
    ("ROI", "Return on Investment", "Betting", "Percentage return on total amount wagered. Key performance metric.", "ROI +15% means $115 returned per $100 bet"),
    
    # Model terms
    ("EP", "Early Pace", "Model", "Rating of a horse's speed in the early stages of a race (first quarter/fraction).", "EP 85/100 - strong early speed"),
    ("LP", "Late Pace", "Model", "Rating of a horse's closing kick and finishing speed.", "LP 90/100 - strong closer"),
    ("PR", "Pace Rating", "Model", "Combined assessment of early and late pace abilities.", "PR composite of EP + LP"),
    ("%E", "Energy Distribution", "Model", "Percentage of energy expended in early vs late phases.", "65%E = 65% early, 35% late"),
    ("Fair Odds", "Fair Odds", "Model", "Odds calculated from the model's probability. Break-even odds.", "25% win prob = 3-1 fair odds"),
    ("Composite", "Composite Rating", "Model", "Overall score combining speed, pace, class, form, connections (0-100 scale).", "Composite 78.5 - strong contender"),
    ("Power Rank", "Power Rank", "Model", "Ranking by composite rating. #1 is the strongest horse.", "Power Rank #2 of 8"),
    ("Pace Scenario", "Pace Scenario", "Model", "Projected pace dynamic for a horse (lone speed, pressured, collapse, etc.).", "Lone Speed scenario detected"),
    ("Bounce", "Bounce", "Model", "Theory that a horse may regress after a peak performance. Flagged by the model.", "Bounce risk after 102 speed figure"),
    ("Class Drop", "Class Drop", "Model", "When a horse races against easier competition than previously. Often a positive signal.", "Class drop from STK to ALW"),
    ("Layoff", "Layoff", "Model", "Period of time since last race. Too short or too long can be negative.", "45-day layoff - moderate concern"),
    
    # Conditions
    ("Fast", "Fast (Dirt)", "Condition", "Dry, firm dirt surface. Standard baseline condition.", "Dirt rated Fast"),
    ("Good", "Good (Dirt)", "Condition", "Slightly less than fast. Still firm but not perfect.", "Dirt rated Good"),
    ("Muddy", "Muddy", "Condition", "Wet dirt surface. Favors horses with early speed.", "Track downgraded to Muddy"),
    ("Sloppy", "Sloppy", "Condition", "Very wet surface with standing water. Strong speed bias.", "Sloppy sealed - speed paradise"),
    ("Sealed", "Sealed", "Condition", "Track surface compressed to keep water out. Can be fast or tricky.", "Sealed before rain"),
    ("Firm", "Firm (Turf)", "Condition", "Hard, dry turf course. Fastest turf condition.", "Turf rated Firm"),
    ("Yielding", "Yielding", "Condition", "Softening turf. Favors horses with stamina and closing kick.", "Turf rated Yielding"),
    ("Soft", "Soft (Turf)", "Condition", "Very soft, deep turf. European-style condition. Big closer advantage.", "Turf rated Soft - deep closing bias"),
    
    # Pace dynamics
    ("Lone Speed", "Lone Speed", "Pace", "One horse with significantly more early speed than the field. Wire threat.", "#5 has lone speed - may wire"),
    ("Pace Pressure", "Pace Pressure", "Pace", "Multiple speed horses pressuring each other early. Sets up for closers.", "3 horses with EP >80 - pace pressure"),
    ("Pace Collapse", "Pace Collapse", "Pace", "When early pace fractions are so fast that leaders tire badly.", ":21.8 first quarter - collapse likely"),
    ("Presser", "Presser", "Pace", "Horse that races just behind the leader, applying pressure.", "Presser sits 1-2 lengths off"),
    ("Stalker", "Stalker", "Pace", "Horse that sits a few lengths behind the pace, ready to pounce.", "Stalker 3-4 lengths back"),
    ("Closer", "Closer", "Pace", "Horse that runs from well back and makes a late move.", "Closer drops 10+ lengths back"),
    
    # QH terms
    ("Break", "Break Speed", "QH", "Initial burst from the starting gate. Critical in QH racing.", "Break rating 92/100 - elite gate speed"),
    ("First Call", "First Call", "QH", "First timing point in a QH race, typically at the 1/16 pole.", "First call :05.8"),
    ("Gate Speed", "Gate Speed", "QH", "How quickly a horse leaves the starting gate. Often determines QH races.", "Gate speed wins 400y races"),
    ("QH Trial", "QH Trial", "QH", "Qualifier race where horses earn spots in championship finals.", "Heritage Place trial - top 2 advance"),
    ("QH Final", "QH Final", "QH", "Championship race for which trials qualified. Major QH events.", "Heritage Place final - $1M+ purse"),
]

# Create DataFrame
glossary_df = pd.DataFrame(
    glossary_data,
    columns=["Term", "Full Name", "Category", "Definition", "Example"]
)

# ---------------------------------------------------------------------------
# Search & Filter
# ---------------------------------------------------------------------------

search_col1, search_col2 = st.columns([3, 1])

with search_col1:
    search_term = st.text_input("Search terms...", placeholder="Type to search across all fields", key="glossary_search")

with search_col2:
    categories = ["All"] + sorted(glossary_df["Category"].unique().tolist())
    selected_category = st.selectbox("Category", options=categories, key="glossary_cat")

# Filter
filtered_df = glossary_df.copy()

if search_term:
    mask = (
        filtered_df["Term"].str.contains(search_term, case=False, na=False) |
        filtered_df["Full Name"].str.contains(search_term, case=False, na=False) |
        filtered_df["Definition"].str.contains(search_term, case=False, na=False) |
        filtered_df["Example"].str.contains(search_term, case=False, na=False)
    )
    filtered_df = filtered_df[mask]

if selected_category != "All":
    filtered_df = filtered_df[filtered_df["Category"] == selected_category]

st.markdown(f"**Showing {len(filtered_df)} of {len(glossary_df)} terms**")

# Display
st.dataframe(
    filtered_df,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Term": st.column_config.TextColumn("Term", width="small"),
        "Full Name": st.column_config.TextColumn("Full Name", width="medium"),
        "Category": st.column_config.TextColumn("Category", width="small"),
        "Definition": st.column_config.TextColumn("Definition", width="large"),
        "Example": st.column_config.TextColumn("Example", width="medium"),
    }
)

st.divider()

# ---------------------------------------------------------------------------
# Quick Reference Cards
# ---------------------------------------------------------------------------

st.header("Quick Reference Cards")

ref_col1, ref_col2, ref_col3 = st.columns(3)

with ref_col1:
    st.subheader("Grades")
    st.markdown("""
    **A (Green)** - Strong: 25%+ win, value
    **B (Blue)** - Competitive: 15-24% win
    **C (Amber)** - Marginal: 8-14% win
    **D (Red)** - Weak: <8% win
    """)

with ref_col2:
    st.subheader("Bet Types")
    st.markdown("""
    **W** = Win only
    **P** = Place (1st or 2nd)
    **S** = Show (1st-3rd)
    **EX** = Exacta (1-2 exact)
    **TRI** = Trifecta (1-2-3 exact)
    **SUP** = Superfecta (1-2-3-4 exact)
    """)

with ref_col3:
    st.subheader("Value Labels")
    st.markdown("""
    **Overlay** 💰 - Fair > ML (bet!)
    **Underlay** ⚠️ - Fair < ML (avoid)
    **Fair** 🎯 - Fair ≈ ML (neutral)
    **Unknown** ❓ - No ML data
    """)

# ---------------------------------------------------------------------------
# Category Browser
# ---------------------------------------------------------------------------

st.divider()
st.header("Browse by Category")

for cat in sorted(glossary_df["Category"].unique()):
    with st.expander(f"{cat} ({len(glossary_df[glossary_df['Category']==cat])} terms)"):
        cat_df = glossary_df[glossary_df["Category"] == cat]
        for _, row in cat_df.iterrows():
            st.markdown(f"**{row['Term']}** - {row['Full Name']}")
            st.markdown(f"_{row['Definition']}_")
            st.markdown(f"*Example: {row['Example']}*")
            st.markdown("---")
