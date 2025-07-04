 It retrieves the user’s recent call history from JSONL files in Azure Blob Storage, analyzes key metrics like Wi-Fi signal strength, packet loss, jitter, device glitch rates, CPU usage, and more to detect the root cause of poor call quality. Based on this analysis, it produces two outputs: (1) a detailed technical JSON report summarizing network, device, and system-level insights, including optional AI Search matches for known issues (e.g., problematic headset models or subnets), and (2) a concise, GPT-generated user notification that explains the issue clearly and provides only the most applicable, actionable steps to fix or prevent it. These outputs can be returned via API or pushed to Teams or email depending on the integration.
search_client.search("headset_model:Logitech X120")
The Logitech X120 has a 40% bad call rate across 50 users. Consider replacing it.
search_client.search("subnet:10.0.5.0/24 AND call_quality:bad")
Subnet 10.0.5.0/24 was involved in 24% of reported bad calls last week. IT has flagged it for diagnostics.
```
GPT_PROMPT_NOTIFICATION_JSON = """
You are a Microsoft Teams call diagnostics assistant.

A user recently had a poor-quality Teams call. Based on telemetry data from recent and past calls, your task is to generate a **short, clear diagnostic output** in JSON format.

You are given:
- Summary of recent call metrics
- Detailed data from the most recent bad call
- Optional matches from AI Search (e.g., known headset or subnet problems)

Your output must:
1. Clearly summarize the root cause in plain English (`issue_summary`)
2. List only the specific actions that are truly relevant (`action_steps`)
3. Return strictly valid JSON — do not include any other text.

---
**Call History Summary**:
{summary_table}

**Most Recent Call Details**:
{last_call_details}

**AI Search Matches**:
{ai_search_matches}

---
Now respond only with valid JSON in this format:

{
  "issue_summary": "<one sentence explanation>",
  "action_steps": [
    "<step 1>",
    "<step 2>"
  ]
}
"""
```

