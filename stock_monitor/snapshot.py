# stock_monitor/snapshot.py

from datetime import date
from supabase import create_client
from stock_monitor.config import SUPABASE_URL, SUPABASE_KEY, STORE_IDS
from stock_monitor.itrust_client import get_store_stock

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def take_snapshot(snapshot_type):
    today = date.today().isoformat()

    for store_id in STORE_IDS:
        print(f"Pulling stock for store {store_id}...")
        lenses = get_store_stock(store_id)

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