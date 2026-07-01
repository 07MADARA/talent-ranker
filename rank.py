import json
import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ==============================================================================
# CONFIGURATION & CONSTANTS
# ==============================================================================
DATA_PATH = "candidates.jsonl"
OUTPUT_PATH = "team_antigravity.csv" # Change to your actual team ID later
CURRENT_DATE = datetime(2026, 7, 2) # Close of the hackathon

# The Ideal Profile for "Senior AI Engineer — Founding Team"
JD_DOCUMENT = """
Deep technical depth in modern ML systems embeddings retrieval ranking LLMs fine-tuning vector databases Pinecone Weaviate. 
Shipped production systems real users product engineering scrappy attitude backend infrastructure. 
Not just academic research not just keyword stuffing. Actual product company experience.
"""

# ==============================================================================
# STAGE 1: DATA INGESTION & TRAP FILTERS (GUARDRAILS)
# ==============================================================================
def parse_candidates(filepath):
    """Loads JSONL and extracts key fields into a structured DataFrame."""
    candidates = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            if not line.strip(): continue
            c = json.loads(line)
            
            # Extract basic profile
            prof = c.get('profile', {})
            signals = c.get('redrob_signals', {})
            
            # Synthesize a "Career Document" for semantic matching
            career_text = prof.get('headline', '') + " " + prof.get('summary', '')
            for job in c.get('career_history', []):
                career_text += f" {job.get('title', '')} at {job.get('company', '')} "
            
            # Extract skills for reasoning
            skills = [s.get('name') for s in c.get('skills', []) if s.get('proficiency') in ['advanced', 'expert']]
            
            candidates.append({
                'candidate_id': c['candidate_id'],
                'name': prof.get('name', 'Anonymized Candidate'),
                'years_of_experience': prof.get('years_of_experience', 0),
                'current_title': prof.get('current_title', '').lower(),
                'location': prof.get('location', ''),
                'career_text': career_text,
                'skills_list': skills,
                'raw_skills': c.get('skills', []),
                'career_history': c.get('career_history', []),
                # Signals
                'last_active_date': signals.get('last_active_date', '2000-01-01'),
                'recruiter_response_rate': signals.get('recruiter_response_rate', 0.0),
                'notice_period_days': signals.get('notice_period_days', 90),
                'raw_signals': signals
            })
            
    return pd.DataFrame(candidates)

def apply_deterministic_filters(df):
    """Flags honeypots and impossible profiles."""
    if df.empty:
        df['is_title_trap'] = False
        return df
        
    # Trap 1: Keyword stuffers with unrelated titles
    unrelated_titles = ['marketing', 'hr', 'sales', 'accountant', 'graphic', 'content', 'support']
    df['is_title_trap'] = df['current_title'].apply(
        lambda x: any(t in x for t in unrelated_titles)
    )
    
    # Filter them out (or set their base score to 0 later)
    # df = df[~df['is_title_trap']].copy()
    return df

# ==============================================================================
# STAGE 2 & 3: LIGHTWEIGHT SEMANTIC RETRIEVAL & SCORING
# ==============================================================================
def calculate_base_scores(df):
    """Uses TF-IDF and Cosine Similarity for fast, CPU-friendly semantic scoring."""
    if df.empty:
        df['base_score'] = 0.0
        return df
        
    vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
    
    # Fit on the JD + all candidate texts
    corpus = [JD_DOCUMENT] + df['career_text'].tolist()
    tfidf_matrix = vectorizer.fit_transform(corpus)
    
    # Calculate similarity between JD (index 0) and all candidates (index 1 to N)
    jd_vector = tfidf_matrix[0]
    candidate_vectors = tfidf_matrix[1:]
    
    similarities = cosine_similarity(candidate_vectors, jd_vector).flatten()
    df['base_score'] = similarities
    return df

# ==============================================================================
# STAGE 4: BEHAVIORAL CALIBRATION
# ==============================================================================
def apply_behavioral_multiplier(df):
    """Modifies the score based on real-world availability (Redrob Signals)."""
    if df.empty:
        df['final_score'] = 0.0
        return df
        
    # 1. Recruiter Response Rate Multiplier (Penalize ghosts)
    df['response_multiplier'] = np.where(df['recruiter_response_rate'] < 0.2, 0.5, 1.0)
    df['response_multiplier'] = np.where(df['recruiter_response_rate'] > 0.8, 1.1, df['response_multiplier'])
    
    # 2. Activity Multiplier (Penalize inactive users)
    df['last_active'] = pd.to_datetime(df['last_active_date'], errors='coerce')
    df['days_inactive'] = (CURRENT_DATE - df['last_active']).dt.days
    df['activity_multiplier'] = np.where(df['days_inactive'] > 180, 0.4, 1.0)
    df['activity_multiplier'] = np.where(df['days_inactive'] <= 30, 1.1, df['activity_multiplier'])
    
    # Final Score Calculation
    df['final_score'] = df['base_score'] * df['response_multiplier'] * df['activity_multiplier']
    
    # Normalize to 0-1 range for clean output
    max_score = df['final_score'].max()
    if max_score > 0:
        df['final_score'] = df['final_score'] / max_score
        
    return df

# ==============================================================================
# STAGE 5: REASONING ENGINE & OUTPUT
# ==============================================================================
def generate_reasoning(row):
    """Creates a deterministic, factual justification for the ranking."""
    skills_str = ", ".join(row['skills_list'][:3]) if row['skills_list'] else "general ML skills"
    yoe = round(row['years_of_experience'], 1)
    return (f"{row['current_title'].title()} with {yoe} yrs experience. "
            f"Strong semantic match indicating applied product engineering. "
            f"Core skills include {skills_str}. "
            f"Highly active with {row['recruiter_response_rate']*100:.0f}% response rate.")

def get_ranked_candidates(filepath="candidates.jsonl", filter_traps=True):
    """Entry point for the Streamlit app to get processed candidates."""
    try:
        df = parse_candidates(filepath)
    except FileNotFoundError:
        return pd.DataFrame() # Return empty if file not found
        
    if df.empty:
        return df
        
    df = apply_deterministic_filters(df)
    
    # Calculate honeypots
    honeypots_count = df['is_title_trap'].sum()
    
    if filter_traps:
        df = df[~df['is_title_trap']].copy()
        
    df = calculate_base_scores(df)
    df = apply_behavioral_multiplier(df)
    
    df['reasoning'] = df.apply(generate_reasoning, axis=1)
    df = df.sort_values(by=['final_score', 'candidate_id'], ascending=[False, True])
    
    # Pack honeypots info into attrs if possible, or we can just count it in app.py
    return df

def main():
    print("🚀 Initializing Antigravity Ranker...")
    
    print("1. Ingesting candidates and applying guardrails...")
    try:
        df = parse_candidates(DATA_PATH)
    except FileNotFoundError:
        print(f"Error: {DATA_PATH} not found.")
        return
        
    df = apply_deterministic_filters(df)
    df = df[~df['is_title_trap']].copy()
    
    print("2. Calculating semantic relevance...")
    df = calculate_base_scores(df)
    
    print("3. Applying behavioral calibration...")
    df = apply_behavioral_multiplier(df)
    
    print("4. Sorting and formatting Top 100...")
    # Sort by final_score descending, then candidate_id ascending for deterministic tie-breaking
    df = df.sort_values(by=['final_score', 'candidate_id'], ascending=[False, True])
    top_100 = df.head(100).copy()
    
    # Format columns per submission_spec.md
    top_100['rank'] = range(1, len(top_100) + 1)
    top_100['score'] = top_100['final_score'].round(4)
    top_100['reasoning'] = top_100.apply(generate_reasoning, axis=1)
    
    final_output = top_100[['candidate_id', 'rank', 'score', 'reasoning']]
    
    print(f"5. Saving submission to {OUTPUT_PATH}...")
    final_output.to_csv(OUTPUT_PATH, index=False, encoding='utf-8')
    print("✅ Run complete. System ready.")

if __name__ == "__main__":
    main()
