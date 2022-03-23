import os
import json
from pathlib import Path

SINO = {
    "simulation":False,
    "id":"PAPIUSER01",
    "password":"2222"
}

QUOTE_WORKER = {
    'source':'sino',
    'enable_publish':True,
    'quote_types':['tick'],
    'subscribe_codes':[
        'TXFD2', 'MXFD2', 'NYFD2', '2330'
    ],
    'database':'InfluxDB',
    'save_interval':0.1
}

HISTORY = {
    'type':'kbar', # tick or kbar
    'start_date':'',
    'end_date':'',
    'codes':[]
}



if not SINO['simulation']:
    private_path = Path(__file__).parent.parent.absolute() / r'private.json'
    if os.path.exists(private_path):
        with open(private_path, 'r') as f:
            private = json.load(f)
        SINO['id'] = private['sino']['id']
        SINO['password'] = private['sino']['password']
