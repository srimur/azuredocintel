from azure.cosmos import CosmosClient, PartitionKey
import uuid
import datetime
import os

# === SETUP ENVIRONMENT VARIABLES ===
# Set these in your shell or VS Code launch config
# export COSMOS_ENDPOINT="https://<your-cosmos-db-account>.documents.azure.com:443/"
# export COSMOS_KEY="<your-cosmos-key>"

COSMOS_ENDPOINT = os.environ.get("COSMOS_ENDPOINT")
COSMOS_KEY = os.environ.get("COSMOS_KEY")
DATABASE_NAME = "teams"
CONTAINER_NAME = "teams-call-analysis"

# === CONNECT TO COSMOS DB ===
client = CosmosClient(COSMOS_ENDPOINT, COSMOS_KEY)
database = client.get_database_client(DATABASE_NAME)
container = database.get_container_client(CONTAINER_NAME)

# === SAMPLE GPT OUTPUT ===
sample_gpt_response = {
    "user_id": "6d9c4cf7-4c29-41d7-b0e1-5c901e3548dc",
    "technical_analysis": {
        "bad_call_count": 6,
        "common_issues": {
            "wifi_signal_strength": "Average: 42 dBm — weak signal in 5/6 bad calls",
            "link_speed": "Below 20 Mbps in 4/6 bad calls",
            "mic_glitch_rate": "Above 0.3 in 3/6 bad calls",
            "headset_model": "Logitech X120 used in 5/6 bad calls"
        },
        "subnet_flag": "10.0.5.0/24 had 8 bad calls across all users in the last day (via AI Search)",
        "headset_flag": "Logitech X120 appears in 12 bad calls across 25 recent users (via AI Search)",
        "device_glitch_ratio_trend": "Increasing from 0.1 → 0.4 over last 3 calls",
        "packet_loss_avg": "3.8%",
        "jitter_avg": "65 ms"
    },
    "actionable_notification": {
        "summary": "6 out of your last 10 Teams calls had poor quality.",
        "recommendations": [
            "Try switching from Wi-Fi to a wired connection (signal strength low).",
            "Consider replacing headset model 'Logitech X120' — involved in many bad calls.",
            "Check your network setup on subnet '10.0.5.0/24' — common issue across users.",
            "Try restarting your device — audio glitch ratio increasing recently."
        ]
    }
}

# === FUNCTION TO STORE IN COSMOS ===
def store_gpt_response_in_cosmos(gpt_response: dict):
    gpt_response["id"] = str(uuid.uuid4())
    if "timestamp" not in gpt_response:
        gpt_response["timestamp"] = datetime.datetime.utcnow().isoformat() + "Z"
    
    container.upsert_item(gpt_response)
    print(f"✅ Stored GPT analysis for user {gpt_response['user_id']} in Cosmos DB.")

# === TEST RUN ===
if __name__ == "__main__":
    if not COSMOS_ENDPOINT or not COSMOS_KEY:
        print("❌ Set COSMOS_ENDPOINT and COSMOS_KEY as environment variables.")
    else:
        store_gpt_response_in_cosmos(sample_gpt_response)
