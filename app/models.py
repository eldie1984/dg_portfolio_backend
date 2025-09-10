from datetime import datetime
from app import db


class FinancialInstrument(db.Model):
    __tablename__ = "financial_instruments"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    instrument_type = db.Column(db.String(50), nullable=False)  # 'bond', 'loan', 'stock', 'obligation'
    issue_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    face_value = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(3), default="USD")

    # Price tracking for portfolio management
    current_price = db.Column(db.Float, nullable=True)
    buying_price = db.Column(db.Float, nullable=True)
    selling_price = db.Column(db.Float, nullable=True)
    last_price_update = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)

    # For Bonds
    coupon_rate = db.Column(db.Float, nullable=True)
    maturity_date = db.Column(db.DateTime, nullable=True)
    payment_frequency = db.Column(db.Integer, nullable=True)  # in months

    # For Loans
    interest_rate = db.Column(db.Float, nullable=True)
    duration_months = db.Column(db.Integer, nullable=True)

    # For Stocks
    ticker_symbol = db.Column(db.String(20), nullable=True)

    # For Negotiable Obligations
    issuer = db.Column(db.String(100), nullable=True)

    __mapper_args__ = {"polymorphic_identity": "financial_instrument", "polymorphic_on": instrument_type}


class Bond(FinancialInstrument):
    __tablename__ = "bonds"

    id = db.Column(db.Integer, db.ForeignKey("financial_instruments.id"), primary_key=True)
    partial_payment_date = db.Column(db.DateTime, nullable=True)

    __mapper_args__ = {"polymorphic_identity": "bond"}


class Loan(FinancialInstrument):
    __tablename__ = "loans"

    id = db.Column(db.Integer, db.ForeignKey("financial_instruments.id"), primary_key=True)

    __mapper_args__ = {"polymorphic_identity": "loan"}


class Stock(FinancialInstrument):
    __tablename__ = "stocks"

    id = db.Column(db.Integer, db.ForeignKey("financial_instruments.id"), primary_key=True)

    __mapper_args__ = {"polymorphic_identity": "stock"}


class NegotiableObligation(FinancialInstrument):
    __tablename__ = "negotiable_obligations"

    id = db.Column(db.Integer, db.ForeignKey("financial_instruments.id"), primary_key=True)

    __mapper_args__ = {"polymorphic_identity": "obligation"}


class Portfolio(db.Model):
    __tablename__ = "portfolios"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    total_value = db.Column(db.Float, default=0.0)

    # Relationship to holdings
    holdings = db.relationship("PortfolioHolding", backref="portfolio", lazy=True, cascade="all, delete-orphan")
    transactions = db.relationship("Transaction", backref="portfolio", lazy=True, cascade="all, delete-orphan")


class PortfolioHolding(db.Model):
    __tablename__ = "portfolio_holdings"

    id = db.Column(db.Integer, primary_key=True)
    portfolio_id = db.Column(db.Integer, db.ForeignKey("portfolios.id"), nullable=False)
    instrument_id = db.Column(db.Integer, db.ForeignKey("financial_instruments.id"), nullable=False)
    quantity = db.Column(db.Float, nullable=False, default=0.0)
    average_cost = db.Column(db.Float, nullable=False, default=0.0)
    current_value = db.Column(db.Float, nullable=True)
    last_updated = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    instrument = db.relationship("FinancialInstrument", backref="holdings")


class Transaction(db.Model):
    __tablename__ = "transactions"

    id = db.Column(db.Integer, primary_key=True)
    portfolio_id = db.Column(db.Integer, db.ForeignKey("portfolios.id"), nullable=False)
    instrument_id = db.Column(db.Integer, db.ForeignKey("financial_instruments.id"), nullable=False)
    transaction_type = db.Column(db.String(10), nullable=False)  # 'buy' or 'sell'
    quantity = db.Column(db.Float, nullable=False)
    price_per_unit = db.Column(db.Float, nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    transaction_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    fees = db.Column(db.Float, default=0.0)
    notes = db.Column(db.Text, nullable=True)

    # Relationships
    instrument = db.relationship("FinancialInstrument", backref="transactions")
