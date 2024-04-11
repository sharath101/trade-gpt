from market_data import app
from market_data import scheduler

if __name__ == "__main__":
    print(type(scheduler))
    scheduler.start()
    app.run(debug=True)
