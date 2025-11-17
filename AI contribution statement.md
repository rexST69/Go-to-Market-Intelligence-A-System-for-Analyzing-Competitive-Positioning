AI Contribution Statement

This statement details the use of generative AI (Google's Gemini) in the project, as required by the course guidelines.

Tools Used: Google Gemini (Advanced Model).

Purpose of AI Use: The AI was not used to write the report, but was integrated as both a core component of the product and as a development partner (pair programmer).

Core System Component (The "Brains"): The Gemini API was the central processing unit of the information system. Its role was to execute the "Batch AI Analysis" (Phase 3), analyzing thousands of comments and returning structured JSON data based on a complex GTM prompt.

System Architecture (Brainstorming Partner): I used the AI to "critique" my own architectural plans. For example, I explored the trade-offs of an "in-line" vs. "post-processing" triage filter and the challenges of API rate-limiting. This helped me design the more robust "batch processing" and "Simple DLQ" architecture.

Coding Assistance (Pair Programmer): I used the AI to generate, debug, and refine complex Python code. This included generating the pandas code for the "Smarter Triage" filter, the try...except block for robust error handling, and the multilingual, JSON-schema-enforcing "Batch Analyst" prompt.

Verification of Output:

Code Verification: All AI-generated code was tested iteratively. The "v3" test run (unit test) failed to categorize pain points correctly, which led to a human-driven "v4" fix (improving the prompt and GTM keywords). The code was not trusted blindly.

Data Verification: The AI's JSON output (the final gtm_final_analysis.csv) was manually spot-checked. The successful categorization of the Turkish "videos don't open" comment into "Technical Issue" validated that the AI's multilingual and categorization logic (v4) was working as designed.

Strategic Verification: All final "Management Insights" and "Recommendations" were derived by me (the human analyst) from the AI-generated dashboard. The AI provided the data; I provided the business strategy.
