from utils import db


class APIKey(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(500), nullable=False)
    secret = db.Column(db.String(100), nullable=False)
    expiry = db.Column(db.DateTime, nullable=True)
    platform = db.Column(db.String(100), nullable=False)

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
