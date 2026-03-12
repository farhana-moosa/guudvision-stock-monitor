# stock_monitor/scheduler.py

from apscheduler.schedulers.blocking import BlockingScheduler
from stock_monitor.config import MORNING_RUN_HOUR, EOD_RUN_HOUR
from stock_monitor.snapshot import take_snapshot
from stock_monitor.report import run_report

scheduler = BlockingScheduler()

def morning_job():
    print("Running morning snapshot...")
    take_snapshot("morning")

def eod_job():
    print("Running EOD snapshot...")
    take_snapshot("eod")
    # run_report()

scheduler.add_job(morning_job, "cron", hour=MORNING_RUN_HOUR, minute=0)
scheduler.add_job(eod_job, "cron", hour=EOD_RUN_HOUR, minute=0)

def start():
    print(f"Scheduler started. Morning run at {MORNING_RUN_HOUR}:00, EOD run at {EOD_RUN_HOUR}:00")
    scheduler.start()

if __name__ == "__main__":
    start()