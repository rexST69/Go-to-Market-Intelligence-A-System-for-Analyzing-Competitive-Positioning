# Go-to-Market-Intelligence-A-System-for-Analyzing-Competitive-Positioning
It's a GTM Intelligence System. It's a 2-stage Python pipeline that scrapes Reddit, then uses a cost-efficient Triage Filter and robust Batch AI (Gemini) analysis. It finds why users choose Grok over ChatGPT, categorizing pain points like 'censorship' or 'accuracy' into a final "Comparative Intelligence Dashboard" for PMs.
GTM Battleground: An AI System for Competitor Intelligence

This is the official annexure for my "Introduction to Marketing Management" project. This repository contains the complete, 2-script Python information system built to analyze public Reddit conversations and generate a "Comparative Intelligence Dashboard" for xAI (Grok) vs. its competitors (OpenAI, Google, Anthropic).

This system is designed not as a simple script, but as a robust, scalable, and cost-efficient pipeline that reflects real-world GTM and Product Management priorities.

System Architecture (The 5-Phase Pipeline)

The system is split into two main scripts, separating "Ingestion" from "Analysis" for scalability and re-running.

[Phase 1: Ingestion] -> [Phase 2: Triage Filter] -> [Phase 3: Batch AI Analysis] -> [Phase 4: Output Storage] -> [Phase 5: Dashboard]

Phase 1: Ingestion (grok_gtm_scraper.py)

Targets specific "battleground" subreddits (e.g., r/ChatGPT, r/GoogleGemini) to scrape raw, unstructured comments.

Saves all data to gtm_raw_comments.csv as the "source of truth."

Phase 2: Triage Filter (gtm_analysis_pipeline_v5.py)

Applies critical business logic to save costs.

Cleans bot spam (AutoModerator) and filters out irrelevant noise.

Uses a "Smarter Triage" keyword list (brands + symptoms like 'censored', 'woke') to isolate high-signal comments, reducing API costs by over 85%.

Phase 3: Batch AI Analysis (gtm_analysis_pipeline_v5.py)

Calls the Gemini API in efficient batches (50 comments/call) to avoid rate limits.

Uses a robust, multilingual prompt to analyze each comment for product_mentioned, sentiment, and pain_point.

Features a "Simple Dead-Letter Queue" (gtm_failed_batches.csv) to catch API errors without crashing, ensuring no data is lost.

Phase 4: Output Storage

Saves the final, structured JSON analysis to gtm_final_analysis.csv.

Phase 5: Dashboard (GTM_Dashboard.xlsx)

The final CSV is used to create a "Comparative Intelligence Dashboard" in Excel with Pivot Charts.

Key Findings (The GTM/PM Dashboard)

The system successfully identified clear, actionable management insights.

Finding 1: The "Censorship" Attack Vector
The dashboard proves that "Censorship" and "Woke/Bias" are the #1 pain points for ChatGPT and DeepSeek users, providing Grok with a data-driven GTM opportunity.

Finding 2: The "Polarized Brand" Problem
The data shows Grok is a "love it or hate it" brand, with high positive and negative sentiment. Grok's own primary pain point is also "Censorship," indicating a critical misalignment between its brand promise and the user experience.

How to Run This System

Clone the repository.

Install dependencies: pip install pandas google-generativeai python-dotenv tqdm

Create your .env file: Create a file named .env in the root and add one line: GEMINI_API_KEY=YOUR_KEY_HERE

Configure praw.ini: Create this file with your Reddit app credentials (this file is in the .gitignore and will not be uploaded).

Run Phase 1 (Ingestion): python grok_gtm_scraper.py

Run Phase 2-4 (Analysis): python gtm_analysis_pipeline_v5.py

View Results: Open GTM_Dashboard.xlsx to see the final dashboard.
