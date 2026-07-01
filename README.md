# Antigravity Ranker | Intelligent Candidate Discovery

This repository contains the **Antigravity Ranker**, a multi-stage cascading pipeline engineered for the Redrob Talent Intelligence Challenge. 

## 🚀 Live Sandbox
[Access the Command Center](https://talent-ranker-dxmhdh6vijjjv6rwdmp99a.streamlit.app/)

## 🏗 System Architecture
Our engine is designed to operate under strict CPU-only constraints while aggressively filtering for dataset traps.

1. **Deterministic Guardrails:** Hard-filters honeypots and "keyword stuffers" (e.g., non-engineering titles with high skill keywords).
2. **Hybrid Retrieval:** Uses optimized TF-IDF sparse matching to prune 100k candidates to the top 2k, followed by dense semantic scoring for relevance.
3. **Behavioral Calibration:** Applies a mathematical multiplier to prioritize candidates with high recruiter response rates and recent platform activity.

## 🛠 Tech Stack
- **Backend:** Python, Scikit-Learn (TF-IDF), Pandas, NumPy.
- **Frontend:** Streamlit with custom Glassmorphism CSS and Plotly-integrated visualizations.
- **Performance:** Optimized for <5 minute execution on CPU-constrained environments.

## 📋 How to Reproduce
1. Clone the repository: `git clone https://github.com/07MADARA/talent-ranker`
2. Install dependencies: `pip install -r requirements.txt`
3. Run the ranker: `python rank.py` (ensure `candidates.jsonl` is in the root directory).
4. Validate results: `python validate_submission.py team_antigravity.csv`

---
*Submission by Team JOYBOY_07*
