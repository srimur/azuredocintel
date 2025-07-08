# nodes/store_results.py

import uuid
import datetime
import os
import json
from azure.cosmos import CosmosClient
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient

# === ENV VARS ===
COSMOS_ENDPOINT = os.environ["COSMOS_ENDPOINT"]
COSMOS_KEY = os.environ["COSMOS_KEY"]
COSMOS_DB = "teams"
COSMOS_CONTAINER = "teams-call-analysis"

STORAGE_ACCOUNT_URL = os.environ["BLOB_ACCOUNT_URL"]
BLOB_CONTAINER = "cqd-analysis-logs"

# === Setup Cosmos and Blob Clients ===
cosmos_client = CosmosClient(COSMOS_ENDPOINT, COSMOS_KEY)
cosmos_container = cosmos_client.get_database_client(COSMOS_DB).get_container_client(COSMOS_CONTAINER)

blob_service = BlobServiceClient(account_url=STORAGE_ACCOUNT_URL, credential=DefaultAzureCredential())
blob_container = blob_service.get_container_client(BLOB_CONTAINER)

# === Timestamp Generator ===
def utc_now():
    return datetime.datetime.utcnow().isoformat() + "Z"

# === Log Formatter ===
def build_log_entry(level: str, message: str):
    return f"[{utc_now()}] [{level.upper()}] {message}"

# === Upload log to blob ===
def upload_log_to_blob(log_text: str, organizer_user_id: str):
    blob_path = f"logs/{organizer_user_id}.log"
    try:
        existing = ""
        try:
            existing = blob_container.download_blob(blob_path).readall().decode()
        except Exception:
            pass  # Log doesn't exist yet

        new_log = existing + "\n" + log_text
        blob_container.upload_blob(blob_path, new_log.strip(), overwrite=True)
    except Exception as e:
        print(build_log_entry("error", f"Failed to upload log: {e}"))

# === Store to Cosmos ===
def store_to_cosmos(organizer_user_id: str, gpt_response: dict):
    doc = {
        "id": str(uuid.uuid4()),
        "organizer_user_id": organizer_user_id,
        "timestamp": utc_now(),
        **gpt_response
    }
    cosmos_container.upsert_item(doc)
    return doc["id"]

# === Store to Blob ===
def upload_to_blob(organizer_user_id: str, gpt_response: dict):
    blob_path = f"reports/report_{organizer_user_id}.json"
    doc = {
        "organizer_user_id": organizer_user_id,
        "timestamp": utc_now(),
        **gpt_response
    }
    blob_container.upload_blob(blob_path, json.dumps(doc), overwrite=True)

# === LangGraph Node ===
def store_results_node(state: dict) -> dict:
    gpt_response = state.get("gpt_output")
    organizer_user_id = state.get("organizer_user_id")

    if not gpt_response or not organizer_user_id:
        raise ValueError("Missing required state fields.")

    log_lines = []
    log_lines.append(build_log_entry("info", f"Started storing report for {organizer_user_id}"))

    try:
        doc_id = store_to_cosmos(organizer_user_id, gpt_response)
        log_lines.append(build_log_entry("success", f"Stored in Cosmos DB (id: {doc_id})"))
    except Exception as e:
        log_lines.append(build_log_entry("error", f"Cosmos DB error: {e}"))

    try:
        upload_to_blob(organizer_user_id, gpt_response)
        log_lines.append(build_log_entry("success", "Report JSON uploaded to Blob"))
    except Exception as e:
        log_lines.append(build_log_entry("error", f"Blob upload error: {e}"))

    try:
        full_log = "\n".join(log_lines)
        upload_log_to_blob(full_log, organizer_user_id)
    except Exception as e:
        print(build_log_entry("error", f"Final log upload failed: {e}"))

    print(f"✅ Completed store for organizer_user_id={organizer_user_id}")
    return state
