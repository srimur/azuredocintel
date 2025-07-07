import json
import os
import random
from datetime import datetime, timedelta
from pathlib import Path
from copy import deepcopy

# CONFIG
NUM_USERS = 500
CALLS_PER_USER = 10
HEADSET_MODELS = [
    "Logitech X120", "Jabra Evolve2", "Poly Blackwire 5220", "HP G2",
    "Dell Wired", "Sony WH-1000XM4", "Bose QC45", "RandomOEM Model Z", "Unknown Headset"
]
SUBNETS = [
    "10.0.1.0/24", "10.0.2.0/24", "10.0.5.0/24", "172.16.0.0/24", "192.168.1.0/24", 
    "192.168.10.0/24", "172.20.5.0/24", "10.1.1.0/24", "10.20.10.0/24", "203.0.113.0/24"
]
OUTPUT_DIR = "generated_cqd_data"
os.makedirs(f"{OUTPUT_DIR}/prev_calls", exist_ok=True)
os.makedirs(f"{OUTPUT_DIR}/search_index", exist_ok=True)

# Load your 2 random base samples
with open("sample1.json", "r") as f:
    template1 = json.load(f)
with open("sample2.json", "r") as f:
    template2 = json.load(f)

BASE_TEMPLATES = [template1, template2]

def generate_call(user_id: str, call_num: int, base_time: datetime, is_bad: bool) -> dict:
    template = deepcopy(random.choice(BASE_TEMPLATES))
    timestamp = base_time + timedelta(minutes=call_num * 6)
    
    # Basic metadata
    template["user_id"] = user_id
    template["timestamp"] = timestamp.isoformat()
    template["call_quality"] = "bad" if is_bad else "good"
    template["headset_model"] = random.choice(HEADSET_MODELS)
    template["subnet"] = random.choice(SUBNETS)

    # Inject signal/network/system conditions
    template["wifi_signal_strength"] = random.randint(30, 60) if is_bad else random.randint(70, 100)
    template["link_speed"] = random.randint(5, 30) if is_bad else random.randint(80, 150)
    template["averagepacketlossrate"] = round(random.uniform(3.0, 10.0), 2) if is_bad else round(random.uniform(0.0, 0.5), 2)
    template["averagejitter"] = round(random.uniform(30, 100), 2) if is_bad else round(random.uniform(1, 10), 2)
    template["averageroundtriptime"] = random.randint(150, 300) if is_bad else random.randint(20, 100)
    template["cpuinsufficienteventratio"] = round(random.uniform(0.3, 0.6), 2) if is_bad else round(random.uniform(0.0, 0.1), 2)
    template["deviceglitcheventratio"] = round(random.uniform(0.3, 0.7), 2) if is_bad else round(random.uniform(0.0, 0.1), 2)
    template["mic_glitch_rate"] = round(random.uniform(0.2, 0.5), 2) if is_bad else round(random.uniform(0.0, 0.1), 2)
    template["speaker_glitch_rate"] = round(random.uniform(0.2, 0.5), 2) if is_bad else round(random.uniform(0.0, 0.1), 2)
    template["lowframerateratio"] = round(random.uniform(0.3, 0.8), 2) if is_bad else round(random.uniform(0.0, 0.1), 2)
    template["averagevideoframerate"] = random.randint(5, 15) if is_bad else random.randint(20, 30)
    template["sendqualityeventratio"] = round(random.uniform(0.3, 0.9), 2) if is_bad else round(random.uniform(0.0, 0.1), 2)
    template["receivequalityeventratio"] = round(random.uniform(0.3, 0.9), 2) if is_bad else round(random.uniform(0.0, 0.1), 2)
    template["sent_signal_level"] = random.randint(-90, -70) if is_bad else random.randint(-60, -40)
    template["sent_noise_level"] = random.randint(-100, -80) if is_bad else random.randint(-75, -60)

    return template

# All calls for global AI Search index
global_search_index = []

print("🔄 Generating synthetic call data for 500 users...")

for user_num in range(1, NUM_USERS + 1):
    user_id = f"user_{user_num}"
    user_calls = []
    base_time = datetime.now() - timedelta(days=2)

    for call_id in range(CALLS_PER_USER):
        is_bad = random.random() < 0.5  # 50% chance
        call = generate_call(user_id, call_id, base_time, is_bad)
        user_calls.append(call)
        global_search_index.append(call)

    # Write per-user file
    with open(f"{OUTPUT_DIR}/prev_calls/{user_id}.jsonl", "w") as f:
        for call in user_calls:
            f.write(json.dumps(call) + "\n")

# Write AI search index file
with open(f"{OUTPUT_DIR}/search_index/all_calls_for_search.jsonl", "w") as f:
    for call in global_search_index:
        f.write(json.dumps(call) + "\n")

print(f"✅ Done: {NUM_USERS} users × {CALLS_PER_USER} calls = {len(global_search_index)} total records.")
print("📁 Files saved in 'generated_cqd_data/' directory.")
