import os
import json
from pathlib import Path

env_path = Path(__file__).parent.parent.absolute() / r'config.json'
env_config = {}

if os.path.exists(env_path):
    with open(env_path, 'r') as f:
        env_config = json.load(f)

INFLUXDB_TOKEN = env_config['influxdb']['token']
INFLUXDB_URL = env_config['influxdb']['url']
INFLUXDB_ORG = env_config['influxdb']['org']
GF_API_KEY = env_config['grafana']['api_key']