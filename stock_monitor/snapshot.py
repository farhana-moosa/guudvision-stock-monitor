# stock_monitor/snapshot.py

from datetime import date
from supabase import create_client
from stock_monitor.config import SUPABASE_URL, SUPABASE_KEY, STORE_IDS
from stock_monitor.itrust_client import get_store_stock, get_frame_stock

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def take_snapshot(snapshot_type):
    today = date.today().isoformat()

    for store_id in STORE_IDS:
        print(f"Pulling stock for store {store_id}...")
        lenses = get_store_stock(store_id)

        if not lenses:
            print(f"No lens data for store {store_id}, skipping...")
            continue

        rows = [
            {
                "store_id": store_id,
                "sphere": lens["sphere"],
                "cylinder": lens["cylinder"],
                "quantity": lens["quantity"],
                "snapshot_type": snapshot_type,
                "snapshot_date": today
            }
            for lens in lenses
        ]

        supabase.table("stock_snapshots").insert(rows).execute()
        print(f"Saved {len(rows)} lenses for store {store_id}")

    print(f"Snapshot complete: {snapshot_type} - {today}")


def take_frame_snapshot(snapshot_type):
    today = date.today().isoformat()

    for store_id in STORE_IDS:
        print(f"Pulling frame stock for store {store_id}...")
        frames = get_frame_stock(store_id)

        if not frames:
            print(f"No frame data for store {store_id}, skipping...")
            continue

        rows = [
            {
                "store_id": store_id,
                "brand": frame["brand"],
                "model": frame["model"],
                "eye_size": frame["eye_size"],
                "bridge": frame["bridge"],
                "color": frame["color"],
                "exam_code": frame["exam_code"],
                "amount_on_hand": frame["amount_on_hand"],
                "snapshot_type": snapshot_type,
                "snapshot_date": today
            }
            for frame in frames
        ]

        supabase.table("frame_snapshots").insert(rows).execute()
        print(f"Saved {len(rows)} frames for store {store_id}")

    print(f"Frame snapshot complete: {snapshot_type} - {today}")