# stock_monitor/itrust_client.py

import requests
from stock_monitor.config import ITRUST_BASE_URL, ITRUST_API_KEY

LENS_URL = f"{ITRUST_BASE_URL}/admin/v1/settings/eyeglass_stock_lenses"
FRAME_URL = f"{ITRUST_BASE_URL}/admin/v1/settings/eyeglass_lens_frames"

def get_store_stock(store_id):
    all_lenses = []
    page = 1

    while True:
        params = {
            "sort": "created_at",
            "direction": "desc",
            "page": page,
            "rpp": 100,
            "store_id": store_id
        }

        headers = {
            "Authorization": ITRUST_API_KEY,
            "Suite-Name": "ORG-SUITE",
            "Content-Type": "application/json"
        }

        response = requests.get(LENS_URL, headers=headers, params=params)
        response.raise_for_status()

        data = response.json()
        lenses = data["eyeglass_stock_lens"]
        all_lenses.extend(lenses)

        pagination = data["meta"]["pagination"]
        if pagination["next"] is None:
            break

        page += 1

    return [
        {
            "store_id": store_id,
            "sphere": float(lens["sphere"]),
            "cylinder": float(lens["cylinder"]),
            "quantity": lens["amount_on_hand"]
        }
        for lens in all_lenses
    ]

def get_frame_stock(store_id):
    all_frames = []
    page = 1

    while True:
        params = {
            "sort": "created_at",
            "direction": "desc",
            "page": page,
            "rpp": 100,
            "store_id": store_id
        }

        headers = {
            "Authorization": ITRUST_API_KEY,
            "Suite-Name": "ORG-SUITE",
            "Content-Type": "application/json"
        }

        response = requests.get(FRAME_URL, headers=headers, params=params)
        response.raise_for_status()

        data = response.json()
        frames = data.get("eyeglass_lens_frames", [])

        if not frames:
            break

        all_frames.extend([
            {
                "store_id": str(store_id).strip(),
                "brand": frame.get("brand"),
                "model": frame.get("model"),
                "eye_size": frame.get("eye_size"),
                "bridge": frame.get("bridge"),
                "color": frame.get("color", "").split("ICD10:")[0].strip(),
                "exam_code": frame.get("exam_code"),
                "amount_on_hand": frame.get("amount_on_hand", 0),
            }
            for frame in frames
        ])

        page += 1

    return all_frames