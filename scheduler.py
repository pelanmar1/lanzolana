from apscheduler.schedulers.blocking import BlockingScheduler
from app import execute, CONFIG

if __name__ == "__main__":
    minutes = CONFIG["minutesBetweenEachRun"]
    
    scheduler = BlockingScheduler()
    scheduler.add_job(execute, 'interval', minutes=minutes)
    scheduler.start()


