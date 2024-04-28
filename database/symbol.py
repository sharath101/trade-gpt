from utils import db


class Symbol(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(100), nullable=False)
    exchange = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f"Symbol(symbol={self.symbol}, exchange={self.exchange})"
