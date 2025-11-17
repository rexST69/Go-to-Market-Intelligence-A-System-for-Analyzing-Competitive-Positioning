# File: gtm_analysis_pipeline_v5.py
# Desc: This is the v5 "Production" version of the GTM pipeline.
# CRITICAL CHANGE: This version is secure. It reads the API key
# from a local .env file, which is ignored by .gitignore.
# DO NOT upload your .env file to GitHub.

import pandas as pd
import google.generativeai as genai
import os
import json
import time
from tqdm import tqdm # A library to show a progress bar
import re # Import the regex library for cleaning
from dotenv import load_dotenv # <-- NEW: To read the .env file

# ==============================================================================
# PHASE 0: GTM & SYSTEM CONFIGURATION (v5)
# ==============================================================================

# --- NEW: Load environment variables from .env file ---
load_dotenv()
# ---

GTM_CONFIG = {
    # 1. INFO ARCHITECTURE SPEC: File I/O
    "RAW_DATA_FILENAME": "gtm_raw_comments.csv",
    "FINAL_ANALYSIS_FILENAME": "gtm_final_analysis.csv",
    
    # 2. GTM SPEC: The "Smarter" Triage Keywords
    "TRIAGE_KEYWORDS": [
        'grok', 'xai', 'chatgpt', 'openai', 'gemini', 'google ai', 'claude', 'anthropic',
        'censored', 'woke', 'hallucination', 'too expensive', 'bias', 'unbiased'
    ],

    # 3. GTM SPEC: The AI "Data Contract"
    "PAIN_POINT_CATEGORIES": [
        'Censorship', 
        'Accuracy/Hallucination', 
        'Speed', 
        'Cost/Access', 
        'Data Privacy', 
        'Woke/Bias',
        'Technical Issue',
        'Product Gap',
        'Other',
        'N/A' 
    ],
    "SENTIMENT_CATEGORIES": ["Positive", "Negative", "Neutral"],

    # 4. SYSTEM SPEC: API & Batching
    
    # --- CRITICAL FIX: Read API key securely from environment ---
    "API_KEY": os.environ.get("GEMINI_API_KEY"),
    # ---
    
    "BATCH_SIZE": 50, 
    "MAX_COMMENT_LENGTH": 3000, 
    "API_SLEEP_TIME": 10, 
    
    # 5. SYSTEM SPEC: Error Handling
    "FAILED_BATCH_FILENAME": "gtm_failed_batches.csv"
}

# This is the "Brain" of our PM/GTM Analyst.
GTM_ANALYST_PROMPT_TEMPLATE = f"""
You are a senior Go-to-Market (GTM) analyst for xAI, the creator of Grok.
Your job is to analyze a batch of raw Reddit comments to find competitive intelligence.

My Competitors: ["ChatGPT", "Gemini", "Claude"]
My Product: "GTM_CONFIG"

You will be given a JSON list of comments, each with a "Comment_ID" and "Raw_Text".
Your task is to:
1.  Analyze EACH comment in the list *individually*.
2.  Return a single, valid JSON list of your analyses.
3.  The output JSON *must* contain an object for *every* comment in the input.
4.  The "Comment_ID" in your output MUST match the original "Comment_ID".

CRITICAL RULES:
1.  **Language:** Comments may be in any language. Analyze them in their original language, but your entire JSON output MUST be in English.
2.  **Product:** "product_mentioned" must be one of {GTM_CONFIG['TRIAGE_KEYWORDS']} or "N/A".
3.  **Sentiment:** "sentiment" MUST be one of {GTM_CONFIG['SENTIMENT_CATEGORIES']}.
4.  **Pain Point:** "pain_point" MUST be one of {GTM_CONFIG['PAIN_POINT_CATEGORIES']}.
5.  **Specifics:**
    - If a user reports a bug (like 'videos don't open'), use 'Technical Issue'.
    - If a user wants a feature we don't have, use 'Product Gap'.
    - If a pain point is valid but doesn't fit (e.g., 'the name is stupid'), use 'Other'.
    - If there is NO pain point, YOU MUST return "N/A". DO NOT invent one.

Here is the JSON list of comments to analyze:
{{batch_json_string}}
"""

# ==============================================================================
# SYSTEM FUNCTIONS
# ==============================================================================

def initialize_gemini():
    """Configures the Gemini API."""
    # --- UPDATED v5 ---
    # This now reads the key from the GTM_CONFIG, which got it from the .env file
    api_key = GTM_CONFIG["API_KEY"]
    
    if not api_key:
        print("CRITICAL ERROR: 'GEMINI_API_KEY' not found.")
        print("Please create a .env file and add: GEMINI_API_KEY=your_key_here")
        return None
        
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash-preview-09-2025')
        print("Gemini API configured successfully.")
        return model
    except Exception as e:
        print(f"CRITICAL ERROR: Failed to configure Gemini API: {e}")
        return None

# --- NEW FUNCTION (FIX #3) ---
def clean_text_for_triage(text):
# ... existing code ...
    if not isinstance(text, str):
        return ""
    
    # 1. Force-convert to ASCII, ignoring errors.
# ... existing code ...
    text = text.encode('ascii', 'ignore').decode('ascii')
    
    # 2. Remove URLs
# ... existing code ...
    text = re.sub(r'http\S+|www\S+', '', text)
    
    # 3. Remove markdown (like [links](...))
# ... existing code ...
    text = re.sub(r'\[.*?\]\(.*?\)', '', text)
    
    # 4. Convert to lowercase for consistent keyword matching
# ... existing code ...
    text = text.lower()
    
    # 5. Remove all punctuation (we only care about words for the triage)
# ... existing code ...
    text = re.sub(r'[^\w\s]', '', text)
    
    # 6. Remove excess whitespace created by the cleaning
# ... existing code ...
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text
# --- END OF NEW FUNCTION ---

def load_and_triage_data():
# ... existing code ...
    print(f"--- Loading Raw Data from {GTM_CONFIG['RAW_DATA_FILENAME']} ---")
    try:
        df_raw = pd.read_csv(GTM_CONFIG['RAW_DATA_FILENAME'])
# ... existing code ...
    except FileNotFoundError:
        print(f"CRITICAL ERROR: Input file not found: {GTM_CONFIG['RAW_DATA_FILENAME']}")
# ... existing code ...
        return None

    # --- Basic Cleaning (from our roadmap) ---
    df_clean = df_raw.dropna(subset=['Raw_Text']).copy()
# ... existing code ...
    df_clean = df_clean[~df_clean['Raw_Text'].isin(['[deleted]', '[removed]'])]
    
    print(f"Remaining after basic cleaning: {len(df_clean)} comments.")

    # --- NEW (FIX #4) ---
# ... existing code ...
    BOT_FILTER_PATTERN = 'Bot|AutoModerator'
    df_clean = df_clean[~df_clean['Author'].str.contains(BOT_FILTER_PATTERN, case=False, na=False)]
# ... existing code ...
    
    # --- Run Aggressive Pre-Triage Cleaning (FIX #3) ---
    print("Applying aggressive pre-triage cleaning (ASCII, URL, emoji removal)...")
# ... existing code ...
    df_clean['Cleaned_Triage_Text'] = df_clean['Raw_Text'].apply(clean_text_for_triage)
    # --- END OF NEW STEP ---

    # --- GTM Triage (The "Smarter" Filter - FIX #1) ---
# ... existing code ...
    pattern = '|'.join(GTM_CONFIG['TRIAGE_KEYWORDS'])
    df_triaged = df_clean[df_clean['Cleaned_Triage_Text'].str.contains(pattern)].copy()
# ... existing code ...

    # --- Batch Protection Filter (The "Outlier Filter" - FIX #2) ---
    df_triaged = df_triaged[df_triaged['Raw_Text'].str.len() < GTM_CONFIG["MAX_COMMENT_LENGTH"]]
# ... existing code ...
    
    percent_triaged = (len(df_triaged) / len(df_raw)) * 100
    print(f"--- GTM Triage Complete ---")
# ... existing code ...
    
    return df_triaged

def analyze_batch(batch_df, model):
# ... existing code ...
    input_json_batch = batch_df[['Comment_ID', 'Raw_Text']].to_json(orient='records')
# ... existing code ...
    prompt = GTM_ANALYST_PROMPT_TEMPLATE.format(batch_json_string=input_json_batch)
    
    try:
        response = model.generate_content(
# ... existing code ...
            generation_config=genai.types.GenerationConfig(
                response_mime_type="application/json"
            )
        )
        results_list = json.loads(response.text)
# ... existing code ...

    except Exception as e:
        # --- Robust Error Handling (The "Simple DLQ" - FIX #3) ---
# ... existing code ...
        print(f"  SAVING failed batch to {GTM_CONFIG['FAILED_BATCH_FILENAME']}")
        
        batch_df.to_csv(
# ... existing code ...
            GTM_CONFIG['FAILED_BATCH_FILENAME'], 
            mode='a', 
            header=not os.path.exists(GTM_CONFIG['FAILED_BATCH_FILENAME']), 
            index=False
        )
        
        return [] # Return an empty list for this failed batch, but data is saved

# ==============================================================================
# MAIN EXECUTION PIPELINE
# ==============================================================================

def main():
# ... existing code ...
    model = initialize_gemini()
    if not model:
# ... existing code ...

    df_triaged = load_and_triage_data()
    if df_triaged is None or df_triaged.empty:
# ... existing code ...
        return

    all_results = []
    
# ... existing code ...
    total_batches = (len(df_triaged) + GTM_CONFIG["BATCH_SIZE"] - 1) // GTM_CONFIG["BATCH_SIZE"]
    
    print(f"\n--- Starting Phase 3: Batch AI Analysis ---")
# ... existing code ...
    
    # Use tqdm for a nice progress bar
    for i in tqdm(range(0, len(df_triaged), GTM_CONFIG["BATCH_SIZE"]), desc="Processing Batches"):
# ... existing code ...
        
        df_batch = df_triaged.iloc[i : i + GTM_CONFIG["BATCH_SIZE"]]
        
        batch_results = analyze_batch(df_batch, model)
# ... existing code ...
            all_results.extend(batch_results)
            
        print(f"\nBatch {i // GTM_CONFIG['BATCH_SIZE'] + 1}/{total_batches} complete. Waiting {GTM_CONFIG['API_SLEEP_TIME']}s...")
# ... existing code ...

    print("\n--- Phase 3 Complete: All batches processed. ---")

# ... existing code ...
    print(f"--- Starting Phase 4: Saving Final Analysis ---")
    results_df = pd.DataFrame(all_results)
    
    if results_df.empty:
# ... existing code ...
        return

    # Standardize ID columns for a clean merge
# ... existing code ...
    df_triaged['Comment_ID'] = df_triaged['Comment_ID'].astype(str)
    
    # The AI returns 'id' as per our schema, let's rename it for the merge
# ... existing code ...
    results_df['Comment_ID'] = results_df['Comment_ID'].astype(str)


    # Left merge: Keep everything from our AI analysis, add metadata from the triaged file
# ... existing code ...
    final_df = pd.merge(
        results_df, 
        df_triaged, 
        on='Comment_ID', 
        how='left'
    )
    
    # Re-order columns for a logical GTM/PM view
# ... existing code ...
    final_columns = [
        'Comment_ID', 
        'Subreddit', 
        'Author', 
        'Post_Score', 
        'Comment_Score',
        'product_mentioned',  # <-- AI Insight
        'sentiment',          # <-- AI Insight
        'pain_point',         # <-- AI Insight
        'Raw_Text'            # The original "proof"
    ]
    final_df = final_df.reindex(columns=final_columns)

    # Save to our final file
# ... existing code ...
    
    print(f"SUCCESS: Pipeline complete.")
# ... existing code ...
    if os.path.exists(GTM_CONFIG['FAILED_BATCH_FILENAME']):
        print(f"WARNING: Some batches failed. Review them in {GTM_CONFIG['FAILED_BATCH_FILENAME']}")

if __name__ == "__main__":
# ... existing code ...
