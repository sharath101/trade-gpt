from database import db


class APIKey(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(500), nullable=False)
    secret = db.Column(db.String(100), nullable=False)
    expiry = db.Column(db.DateTime, nullable=True)
    platform = db.Column(db.String(100), nullable=False)
    trading = db.Column(db.Boolean, nullable=False, default=True)

    def __repr__(self):
        return f"APIKey(key={self.key}, secret={self.secret})"
