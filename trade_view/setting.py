import os
import json
from pathlib import Path

SINO = {"simulation": True, "id": "", "password": ""}

QUOTE_WORKER = {
    "source": "sino",
    "enable_publish": True,
    "quote_types": ["tick", "orderbook"],
    "subscribe_codes": [
        "TXFH2",
        "TXFI2",
        "MXFH2",
        "MXFI2",
    ],
    "enable_save": False,
    "database": "InfluxDB",
    "save_interval": 0.1,
}

SCHEDULES = [
    {
        "source": "sino",
        "database": "InfluxDB",
        "types": ["tick", "kbar"],  # tick or kbar
        "start_date": "2022-03-25",
        "end_date": "2022-03-25",
        "codes": [
            "TXFH2",
            "TXFI2",
            "MXFH2",
            "MXFI2",
        ],
        "schedule": "",  # HH:MM:SS ,only support every day schedule
    },
]


private_path = Path(__file__).parent.parent.absolute() / r"private.json"
if os.path.exists(private_path):
    with open(private_path, "r") as f:
        private = json.load(f)
    SINO["id"] = private["sino"]["id"]
    SINO["password"] = private["sino"]["password"]
