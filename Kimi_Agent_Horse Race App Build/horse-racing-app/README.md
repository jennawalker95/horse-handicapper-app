# Pro Elite Horse Race Handicapping App

A production-ready Streamlit web application for US Thoroughbred and Quarter Horse race handicapping with probability-based ratings, fair odds, overlay detection, and ROI analytics.

## Features

- **Dual Breed Support**: Full support for US Thoroughbred (TB) and Quarter Horse (QH) racing
- **Smart Presets**: Pre-loaded track, distance, surface, race type, and condition presets that auto-stack
- **Probability Engine**: Win/Place/Show probabilities with fair odds and overlay detection
- **Exact Grading**: Strict A/B/C/D grading thresholds for Overall, Win, Place, and Show
- **Commentary Engine**: Per-horse "why chosen/why not" analysis with wildcard/longshot detection
- **Beginner + Advanced Modes**: Beginner-friendly by default with advanced breakdowns available
- **Results Logging**: SQLite-backed results with ROI analytics and export
- **7 Pages**: Dashboard, Horse Cards, Presets Inspector, Results & ROI, How-To, FAQ, Acronyms

## Quick Start (Local)

```bash
# Clone or download the project
cd horse-racing-app

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Launch the app
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`.

## Deploy to Streamlit Community Cloud

1. Push this project to a GitHub repository
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub account and select the repository
4. Set **Main file path** to `app.py`
5. Click **Deploy**

## Project Structure

```
horse-racing-app/
├── app.py                      # Main entry point
├── pages/
│   ├── 1_Dashboard.py          # Quick picks + rankings
│   ├── 2_Horse_Cards.py        # Detailed horse analysis
│   ├── 3_Presets_Inspector.py  # Preset stacking viewer
│   ├── 4_Results_and_ROI.py    # Results + ROI dashboards
│   ├── 5_How_To_Use.py         # Step-by-step guide
│   ├── 6_FAQ_Troubleshooting.py # FAQ and fixes
│   └── 7_Acronyms_Definitions.py # Searchable glossary
├── model/
│   ├── model_core.py           # Core computations
│   ├── grading.py              # Grade thresholds
│   ├── commentary.py           # Commentary engine
│   ├── presets.py              # Preset loading/stacking
│   └── validators.py           # Input validation
├── presets/                    # CSV preset files
├── data/                       # SQLite database + samples
└── .streamlit/
    └── config.toml             # Theme configuration
```

## How to Use

1. **Race Setup**: Select track, surface, distance, race type, and conditions from the sidebar
2. **Horse Input**: Enter horse data manually or load the sample race
3. **Run Model**: Click "Run Model" to generate ratings and probabilities
4. **Review Dashboard**: See quick picks, rankings, and bet/pass recommendations
5. **Horse Cards**: Drill into individual horses for detailed analysis
6. **Log Results**: After the race, enter results to track ROI

## Sample Race

Click **"Load Sample Race"** on the Dashboard to populate a realistic race example with overlay and longshot demonstrations.

## Grades Explained

- **A (Green)**: Strong contender, top composite rating, typically 25%+ win probability with value
- **B (Blue)**: Competitive, 15-24% win probability, viable contender
- **C (Amber)**: Marginal, 8-14% win probability, use underneath in exotics
- **D (Red)**: Weak, <8% win probability, likely pass

## Preset Stacking Order

1. Track preset
2. Surface preset
3. Distance preset
4. Race type preset
5. Track condition preset

Final weights are the product of all stacked presets. All presets are transparent and viewable in the Presets Inspector page.
