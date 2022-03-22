import os
import json
from pathlib import Path

SINO = {
    "simulation":True,
    "id":"PAPIUSER01",
    "password":"2222"
}

WORKER = {
    'source':'sino',
    'enable_publish':True,
    'limit':100,
    'quote_types':['orderbook'],
    'subscribe_codes':[
        'TXFD2'
    ],
    'database':'InfluxDB',
    'save_interval':0.1
}





if not SINO['simulation']:
    private_path = Path(__file__).parent.parent.absolute() / r'private.json'
    if os.path.exists(private_path):
        with open(private_path, 'r') as f:
            private = json.load(f)
        SINO['id'] = private['sino']['id']
        SINO['password'] = private['sino']['password']
