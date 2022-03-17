import os
import json
from pathlib import Path

SINO = {
    "id":"",
    "password":""
}

WORKER = {
    'source':'SINO',
    'enable_publish':True,
    'limit':100,
    'quote_types':['orderbook'],
    'subscribe_codes':[
        'TXFD2', 'MXFD2'
    ],
    'database':'InfluxDB',
    'save_interval':0.1
}






private_path = Path(__file__).parent.parent.absolute() / r'private.json'
if os.path.exists(private_path):
    with open(private_path, 'r') as f:
        private = json.load(f)
    SINO['id'] = private['sino']['id']
    SINO['password'] = private['sino']['password']
