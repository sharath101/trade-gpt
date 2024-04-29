from datetime import datetime, timedelta
from api import app
import requests
from utils import scheduler
from database import MarketHolidays
from .misc import backup_current_day, delete_old_data


def schedule_week():
    for i in range(1, 8):
        next_day = datetime.now() + timedelta(days=i)

        if next_day.weekday() in [5, 6]:
            continue
        next_day_str = next_day.strftime("%Y-%m-%d")
        with app.app_context():
            marketClosure = MarketHolidays.query.filter_by(date=next_day_str).first()
            if marketClosure:
                continue
        scheduler.add_job(
            id=f"market_start_{next_day.date()}",
            func=requests.get,
            trigger="date",
            run_date=next_day.replace(hour=9, minute=15, second=0),
            args=(f"http://localhost:5000/start",),
            replace_existing=True,
        )

        scheduler.add_job(
            id=f"market_stop_{next_day.date()}",
            func=requests.get,
            trigger="date",
            run_date=next_day.replace(hour=15, minute=30, second=0),
            args=(f"http://localhost:5000/stop",),
            replace_existing=True,
        )

        scheduler.add_job(
            id=f"market_backup_{next_day.date()}",
            func=backup_current_day,
            trigger="date",
            run_date=next_day.replace(hour=16, minute=0, second=0),
            replace_existing=True,
        )

        scheduler.add_job(
            id=f"market_delete_{next_day.date()}",
            func=delete_old_data,
            trigger="date",
            run_date=next_day.replace(hour=16, minute=5, second=0),
            replace_existing=True,
        )


def schedule_until_sunday():
    for i in range(7):
        next_day = datetime.now() + timedelta(days=i)

        if next_day.weekday() in [5, 6]:
            break
        next_day_str = next_day.strftime("%Y-%m-%d")
        with app.app_context():
            marketClosure = MarketHolidays.query.filter_by(date=next_day_str).first()
            if marketClosure:
                continue

        scheduler.add_job(
            id=f"market_start_{next_day.date()}",
            func=requests.get,
            trigger="date",
            run_date=next_day.replace(hour=9, minute=15, second=0),
            args=(f"http://localhost:5000/start",),
            replace_existing=True,
        )

        scheduler.add_job(
            id=f"market_stop_{next_day.date()}",
            func=requests.get,
            trigger="date",
            run_date=next_day.replace(hour=15, minute=30, second=0),
            args=(f"http://localhost:5000/stop",),
            replace_existing=True,
        )

        scheduler.add_job(
            id=f"market_backup_{next_day.date()}",
            func=backup_current_day,
            trigger="date",
            run_date=next_day.replace(hour=16, minute=0, second=0),
            replace_existing=True,
        )

        scheduler.add_job(
            id=f"market_delete_{next_day.date()}",
            func=delete_old_data,
            trigger="date",
            run_date=next_day.replace(hour=16, minute=5, second=0),
            replace_existing=True,
        )
