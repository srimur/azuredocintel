import os, uuid, json
from dotenv import load_dotenv
from azure.identity import AzureCliCredential
from azure.search.documents import SearchClient
from azure.storage.blob import BlobServiceClient
from langchain.chat_models import ChatOpenAI

# ------------------- Load Config ------------------- #
load_dotenv()
cred = AzureCliCredential()

AZURE_SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT")
AZURE_SEARCH_INDEX = os.getenv("AZURE_SEARCH_INDEX")
AZURE_STORAGE_ACCOUNT_NAME = os.getenv("AZURE_STORAGE_ACCOUNT_NAME")
AZURE_STORAGE_CONTAINER_NAME = os.getenv("AZURE_STORAGE_CONTAINER_NAME")
AZURE_OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")

search_client = SearchClient(
    endpoint=AZURE_SEARCH_ENDPOINT,
    index_name=AZURE_SEARCH_INDEX,
    credential=cred
)

blob_service = BlobServiceClient(
    account_url=f"https://{AZURE_STORAGE_ACCOUNT_NAME}.blob.core.windows.net/",
    credential=cred
)
container = blob_service.get_container_client(AZURE_STORAGE_CONTAINER_NAME)

llm = ChatOpenAI(
    deployment_name=AZURE_OPENAI_DEPLOYMENT,
    openai_api_key=AZURE_OPENAI_API_KEY,
    temperature=0
)

# ------------------- Blob Helper ------------------- #
def save_blob(uuid_str, suffix, data):
    container.upload_blob(
        name=f"{uuid_str}_{suffix}.json",
        data=json.dumps(data, indent=2),
        overwrite=True
    )

# ------------------- Main Agent Runner ------------------- #
def run_network_analysis(alert: dict):
    uid = str(uuid.uuid4())
    print(f"[INFO] Processing alert → UUID: {uid}")
    save_blob(uid, "alert", alert)

    # Search context
    display_name = alert.get("displayName", "")
    results = search_client.search(f"displayName:{display_name}", top=20)
    context = [doc for doc in results]
    save_blob(uid, "context", context)
    save_blob(uid, "searchtext", {"query": display_name})

    # Build prompt
    alert_str = json.dumps(alert, indent=2)
    context_str = "\n\n".join([json.dumps(doc, indent=2) for doc in context])

    prompt = f"""
You are a senior network engineer.

ALERT JSON:
{alert_str}

CONTEXT: Microsoft Teams CQD data relevant to this alert:
{context_str}

TASK: 
1. Analyze the alert and CQD context to identify the most likely root cause.
2. Based on your analysis, provide 5 technically valid, realistic actions a network administrator could take to fix it.
3. From those 5, select the **most important single action** to execute first.

Respond ONLY in the following JSON format:

{{
  "root_cause": "short summary",
  "recommendations": [
    "action 1",
    "action 2",
    "action 3",
    "action 4",
    "action 5"
  ],
  "chosen_action": "one of the above"
}}
"""
    save_blob(uid, "prompt", {"prompt": prompt})

    # Get LLM response
    response = llm.predict(prompt)

    try:
        parsed = json.loads(response)
        insights = parsed
    except Exception as e:
        insights = {"error": "Failed to parse LLM JSON", "raw_response": response}

    save_blob(uid, "insights", insights)
    print(f"[SUCCESS] Analysis complete → {uid}")
    return uid, insights


# ------------------- Example Use ------------------- #
if __name__ == "__main__":
    # Simulate a triggered alert input (e.g. from Azure Event Grid, Timer, etc.)
    example_alert = {
        "alert_id": "a1",
        "displayName": "Srinath Murali",
        "alertType": "High packet loss",
        "timestamp": "2025-07-10T11:55:00Z",
        "location": "BLR-DC1",
        "callId": "cqd-call-9283",
        "description": "Call quality below acceptable threshold"
    }

    uid, output = run_network_analysis(example_alert)
    print(json.dumps(output, indent=2))
