from database import db


class MarketHolidays(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String, nullable=False)
    exchange = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f"MarketHolidays(date={self.date}, exchange={self.exchange})"
