from utils import db


class APIKey(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(500), nullable=False)
    secret = db.Column(db.String(100), nullable=False)
    expiry = db.Column(db.DateTime, nullable=True)
    platform = db.Column(db.String(100), nullable=False)
    trading = db.Column(db.Boolean, nullable=False, default=True)

    def __repr__(self):
        return f"APIKey(key={self.key}, secret={self.secret})"


class Symbol(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(100), nullable=False)
    exchange = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f"Symbol(symbol={self.symbol}, exchange={self.exchange})"


class MarketHolidays(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String, nullable=False)
    exchange = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f"MarketHolidays(date={self.date}, exchange={self.exchange})"


class OrderBook(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Primary key in database
    correlation_id = db.Column(db.String(100), nullable=False)  # Correlation ID
    client_id = db.Column(db.String(100), nullable=False)  # Client ID from the client
    order_id = db.Column(db.String(100), nullable=False)  # Order ID from the broker
    symbol = db.Column(db.String(100), nullable=False)  # Symbol of the stock
    exchange = db.Column(db.String(100), nullable=False)  # Exchange of the stock
    quantity = db.Column(db.Integer, nullable=False)  # Quantity of the stock placed
    price = db.Column(db.Float, nullable=False)  # Price of the order excuted
    transaction_type = db.Column(db.String(100), nullable=False)  # Buy or Sell
    order_type = db.Column(db.String(100), nullable=False)  # Market or Limit
    product_type = db.Column(db.String(100), nullable=False)  # Intraday or Delivery
    status = db.Column(db.String(100), nullable=False)  # Order status
    order_created = db.Column(db.DateTime, nullable=True)  # Order created timestamp
    order_updated = db.Column(db.DateTime, nullable=True)  # Order updated timestamp
    exchange_timestamp = db.Column(db.DateTime, nullable=True)  # Exchange timestamp
    bo_profit_val = db.Column(db.Float, nullable=True)  # Bracket order profit value
    bo_stoploss_val = db.Column(db.Float, nullable=True)  # Bracket order stoploss value
    order_opened = db.Column(db.Boolean, nullable=True)  # Order opened or not

    def __repr__(self):
        return f"Order(order_id={self.order_id}, symbol={self.symbol})"
