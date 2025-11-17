# File: grok_gtm_scraper.py
# Desc: This script is an Information System pipeline for GTM/PM analysis.
# It scrapes raw, unstructured comments from specific "battleground" subreddits
# to build a dataset for competitive intelligence on Grok vs. its rivals.

import praw  # Reddit API Wrapper
import time  # For rate limiting
import csv
import os    # To check if files exist

# ==============================================================================
# PHASE 0: GTM & SYSTEM CONFIGURATION
# ==============================================================================
# This is the "Business Logic" and "System Architecture" spec.
# As a PM/GTM lead, you change these inputs to change the system's output.

GTM_CONFIG = {
    # 1. GTM SPEC: Define the "battlegrounds"
    "TARGET_SUBREDDITS": [
        'grok',              # Grok's home turf (biased)
        'ChatGPT',           # Competitor 1's home turf (biased)
        'GoogleGeminiAI',      # Competitor 2's home turf
        'perplexity_ai',
        'ClaudeAI',
        'cursor',
        'DeepSeek'
    ],

    # 2. SYSTEM SPEC: Define the scrape parameters
    # We scrape 'hot' posts to find popular, high-engagement discussions.
    # We could change this to 'new' for real-time data or 'top' for proven insights.
    "POST_SORT_METHOD": "hot",
    "POST_LIMIT_PER_SUB": 50,  # 25 *hot* posts from each subreddit

    # 3. INFO ARCHITECTURE SPEC: Define the output
    "RAW_DATA_FILENAME": "gtm_raw_comments.csv"
}

# ==============================================================================
# PHASE 1: DATA INGESTION (THE SCRAPER)
# ==============================================================================


def sanitize_text(text):
    """
    Cleans up a given string to make it safe for CSV storage.
    - Replaces newline and carriage return characters with spaces.
    - Replaces double quotes with single quotes to prevent CSV formatting issues.
    """
    if not text:
        return ""
    # Replace newline/carriage return with a space
    clean_text = text.replace('\n', ' ').replace('\r', ' ')
    # Replace double quotes with single quotes to avoid CSV errors
    clean_text = clean_text.replace('"', "'")
    return clean_text


def initialize_scraper():
    """
    Authenticates with PRAW and sets up the CSV file and resume logic.
    """
    print("--- Initializing GTM Scraper System ---")

    # --- PRAW AUTHENTICATION ---
    try:
        reddit = praw.Reddit()  # Assumes praw.ini is set up
        print(f"PRAW Authentication successful for: {reddit.user.me()}")
    except Exception as e:
        print(f"PRAW Authentication failed: {e}")
        print("Please ensure your praw.ini file is correctly configured.")
        return None, None, None

    # --- RESUME LOGIC ---
    # We will track processed POSTS to avoid re-scraping them.
    # We don't need to track comments, as we get all comments for a post at once.
    saved_post_ids = set()
    file_exists = os.path.exists(GTM_CONFIG["RAW_DATA_FILENAME"])

    if file_exists:
        print(
            f"Resuming from existing file: {GTM_CONFIG['RAW_DATA_FILENAME']}")
        with open(GTM_CONFIG['RAW_DATA_FILENAME'], 'r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            try:
                header = next(reader)  # Skip header
                for row in reader:
                    if row:
                        # Assumes 'Post_ID' is the 2nd column (index 1)
                        saved_post_ids.add(row[1])
            except StopIteration:
                pass  # File exists but is empty
        print(
            f"Found {len(saved_post_ids)} posts already processed. Will skip them.")
    else:
        print("No existing file found. Starting a new scrape.")

    # --- CSV WRITER SETUP ---
    # Open the file in 'append' mode ('a') so we can resume
    file = open(GTM_CONFIG['RAW_DATA_FILENAME'],
                'a', newline='', encoding='utf-8')
    writer = csv.writer(file)

    # If it's a new file, write the new GTM-focused header
    if not file_exists or os.path.getsize(GTM_CONFIG['RAW_DATA_FILENAME']) == 0:
        header = [
            'Comment_ID',
            'Post_ID',
            'Subreddit',
            'Author',
            'Post_Score',
            'Comment_Score',
            'Raw_Text'
        ]
        writer.writerow(header)

    return reddit, file, writer, saved_post_ids


def fetch_comments(submission, writer, saved_post_ids):
    """
    Fetches, flattens, and saves all comments from a given submission.
    This is the core data extraction logic.
    """
    comment_count = 0
    try:
        # submission.comments.replace_more(limit=0) expands all "load more comments"
        submission.comments.replace_more(limit=0)

        # .list() flattens the entire comment tree
        for comment in submission.comments.list():
            # Check if it's a valid comment and not deleted
            if hasattr(comment, 'body') and comment.body != "[deleted]" and comment.body != "[removed]":

                # Sanitize the text for CSV
                clean_comment_text = sanitize_text(comment.body)

                # Extract the new GTM/PM metadata
                # We save 'None' or 0 for data that might be missing
                author_name = comment.author.name if comment.author else "[deleted_user]"

                # Write the new, enriched GTM data structure
                writer.writerow([
                    comment.id,         # 'Comment_ID'
                    submission.id,      # 'Post_ID' (parent)
                    submission.subreddit.display_name,  # 'Subreddit'
                    author_name,        # 'Author'
                    submission.score,   # 'Post_Score'
                    comment.score,      # 'Comment_Score'
                    clean_comment_text  # 'Raw_Text'
                ])
                comment_count += 1

    except Exception as e:
        print(
            f"  [ERROR] Could not fetch comments for post {submission.id}: {e}")

    print(f"  > Saved {comment_count} comments from this post.")
    # Add the post ID to our set so we don't scrape it again
    saved_post_ids.add(submission.id)


def run_scraper(reddit, file, writer, saved_post_ids):
    """
    Main loop for the GTM scraping system.
    Iterates through each target subreddit and scrapes its posts.
    """
    print("\n--- Starting GTM Ingestion Pipeline ---")
    total_posts_processed = 0

    # Loop through each "battleground" subreddit defined in our config
    for sub_name in GTM_CONFIG["TARGET_SUBREDDITS"]:
        print(f"\n[TARGETING SUBREDDIT: r/{sub_name}]")
        try:
            subreddit = reddit.subreddit(sub_name)

            # Get the top 'hot' posts (or 'new', 'top', based on config)
            if GTM_CONFIG["POST_SORT_METHOD"] == "hot":
                posts = subreddit.hot(limit=GTM_CONFIG["POST_LIMIT_PER_SUB"])
            elif GTM_CONFIG["POST_SORT_METHOD"] == "new":
                posts = subreddit.new(limit=GTM_CONFIG["POST_LIMIT_PER_SUB"])
            else:  # Default to 'hot'
                posts = subreddit.hot(limit=GTM_CONFIG["POST_LIMIT_PER_SUB"])

            posts_in_this_sub = 0
            # Process each post found
            for submission in posts:
                # --- RESUME LOGIC ---
                if submission.id in saved_post_ids:
                    print(
                        f"  - Skipping post (already processed): {submission.id}")
                    continue

                print(
                    f"  + Processing Post: {submission.id} (Score: {submission.score}) - '{submission.title[:50]}...'")

                # Fetch and save all comments for this new post
                fetch_comments(submission, writer, saved_post_ids)

                posts_in_this_sub += 1
                total_posts_processed += 1

                # Be a good API citizen
                time.sleep(1.1)

            print(
                f"[Finished r/{sub_name} - Processed {posts_in_this_sub} new posts]")

        except Exception as e:
            print(
                f"  [CRITICAL ERROR] Failed to scrape subreddit {sub_name}: {e}")
            continue  # Move to the next subreddit

    print("\n--- GTM Ingestion Pipeline Complete ---")
    print(f"Processed {total_posts_processed} new posts in this session.")


# ==============================================================================
# SCRIPT EXECUTION
# ==============================================================================
def main():
    reddit, file, writer, saved_post_ids = initialize_scraper()

    # If initialization failed (e.g., bad auth), exit.
    if not reddit:
        return

    try:
        run_scraper(reddit, file, writer, saved_post_ids)
    except KeyboardInterrupt:
        print("\n[KeyboardInterrupt] Scrape interrupted by user. Shutting down.")
    finally:
        # ALWAYS ensure the file is closed properly
        if file:
            file.close()
            print("File closed. System shutdown complete.")


# This ensures the script only runs when executed directly
if __name__ == "__main__":
    main()
