from datetime import datetime, timedelta
from api import app, logger
import requests
from utils import scheduler
from database import MarketHolidays
from .misc import backup_current_day, delete_old_data


def schedule_week() -> None:
    try:
        for i in range(1, 8):
            next_day = datetime.now() + timedelta(days=i)
            logger.info(f"Scheduling market data for: {next_day.date()}")
            if next_day.weekday() in [5, 6]:
                logger.info(f"Skipping weekend: {next_day.date()}")
                continue
            marketClosure = MarketHolidays.get_first(date=next_day.date())
            if marketClosure:
                logger.info(f"Skipping holiday: {next_day.date()}")
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
    except Exception as e:
        logger.error(f"Error while scheduling market data: {e}")


def schedule_until_sunday() -> None:
    try:
        for i in range(7):
            next_day = datetime.now() + timedelta(days=i)
            logger.info(f"Scheduling market data for: {next_day.date()}")
            if next_day.weekday() in [5, 6]:
                logger.info(f"Skipping weekend: {next_day.date()}")
                continue

            marketClosure = MarketHolidays.get_first(date=next_day.date())
            if marketClosure:
                logger.info(f"Skipping holiday: {next_day.date()}")
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
    except Exception as e:
        logger.error(f"Error while scheduling market data: {e}")
