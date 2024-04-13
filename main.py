from market_data import app
from market_data import scheduler, marketFeedTicker, marketFeedQuote

if __name__ == "__main__":
    scheduler.start()
    app.run(debug=True)
