# upload_jsonl_ad_auth.py

import os
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient

# === CONFIG ===
STORAGE_ACCOUNT_URL = "https://<your-storage-account-name>.blob.core.windows.net"
CONTAINER_NAME = "<your-container-name>"  # e.g. "cqd-data"
LOCAL_FOLDER = "generated_cqd_data/prev_calls"

# === AUTH ===
credential = DefaultAzureCredential()
blob_service = BlobServiceClient(account_url=STORAGE_ACCOUNT_URL, credential=credential)
container_client = blob_service.get_container_client(CONTAINER_NAME)

def upload_jsonl_files():
    for filename in os.listdir(LOCAL_FOLDER):
        if not filename.endswith(".jsonl"):
            continue

        local_path = os.path.join(LOCAL_FOLDER, filename)
        blob_path = f"prev_calls/{filename}"  # blob path

        print(f"Uploading {blob_path}...")

        with open(local_path, "rb") as data:
            container_client.upload_blob(name=blob_path, data=data, overwrite=True)

        print(f"✅ Uploaded: {blob_path}")

if __name__ == "__main__":
    upload_jsonl_files()
