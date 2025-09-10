from datetime import datetime
from . import db


class FinancialInstrument(db.Model):
    __tablename__ = "financial_instruments"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    instrument_type = db.Column(db.String(50), nullable=False)  # 'bond', 'loan', 'stock', 'obligation'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Common fields
    issuer = db.Column(db.String(100))
    face_value = db.Column(db.Float)
    currency = db.Column(db.String(3), default="USD")

    # For bonds
    payment_date = db.Column(db.Date, nullable=True)
    coupon_rate = db.Column(db.Float, nullable=True)

    # For loans
    duration_months = db.Column(db.Integer, nullable=True)
    interest_rate = db.Column(db.Float, nullable=True)

    # For stocks
    ticker = db.Column(db.String(20), nullable=True)
    exchange = db.Column(db.String(50), nullable=True)

    # For negotiable obligations
    maturity_date = db.Column(db.Date, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "instrument_type": self.instrument_type,
            "issuer": self.issuer,
            "face_value": self.face_value,
            "currency": self.currency,
            "payment_date": self.payment_date.isoformat() if self.payment_date else None,
            "coupon_rate": self.coupon_rate,
            "duration_months": self.duration_months,
            "interest_rate": self.interest_rate,
            "ticker": self.ticker,
            "exchange": self.exchange,
            "maturity_date": self.maturity_date.isoformat() if self.maturity_date else None,
            "created_at": self.created_at.isoformat(),
        }
