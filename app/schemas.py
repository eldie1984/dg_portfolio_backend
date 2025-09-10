from marshmallow import Schema, fields, validate, ValidationError
from datetime import datetime
from app import db
from app.models import Bond, Loan, Stock, NegotiableObligation, Portfolio, PortfolioHolding, Transaction


class FinancialInstrumentSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    instrument_type = fields.Str(required=True, validate=validate.OneOf(["bond", "loan", "stock", "obligation"]))
    issue_date = fields.DateTime(dump_only=True)
    face_value = fields.Float(required=True, validate=validate.Range(min=0))
    currency = fields.Str(validate=validate.Length(equal=3), default="USD")

    # Price tracking fields
    current_price = fields.Float(allow_none=True, validate=validate.Range(min=0))
    buying_price = fields.Float(allow_none=True, validate=validate.Range(min=0))
    selling_price = fields.Float(allow_none=True, validate=validate.Range(min=0))
    last_price_update = fields.DateTime(dump_only=True)

    # Common fields
    coupon_rate = fields.Float(allow_none=True, validate=validate.Range(min=0, max=100))
    maturity_date = fields.DateTime(allow_none=True)
    payment_frequency = fields.Int(allow_none=True, validate=validate.Range(min=1))
    interest_rate = fields.Float(allow_none=True, validate=validate.Range(min=0, max=100))
    duration_months = fields.Int(allow_none=True, validate=validate.Range(min=1))
    ticker_symbol = fields.Str(allow_none=True, validate=validate.Length(max=20))
    issuer = fields.Str(allow_none=True, validate=validate.Length(max=100))

    # Bond specific
    partial_payment_date = fields.DateTime(allow_none=True)

    class Meta:
        fields = (
            "id",
            "name",
            "instrument_type",
            "issue_date",
            "face_value",
            "currency",
            "current_price",
            "buying_price",
            "selling_price",
            "last_price_update",
            "coupon_rate",
            "maturity_date",
            "payment_frequency",
            "interest_rate",
            "duration_months",
            "ticker_symbol",
            "issuer",
            "partial_payment_date",
        )


class BondSchema(FinancialInstrumentSchema):
    partial_payment_date = fields.DateTime(required=True)

    def make_obj(self, data, **kwargs):
        return Bond(**data)


class LoanSchema(FinancialInstrumentSchema):
    interest_rate = fields.Float(required=True, validate=validate.Range(min=0, max=100))
    duration_months = fields.Int(required=True, validate=validate.Range(min=1))

    def make_obj(self, data, **kwargs):
        return Loan(**data)


class StockSchema(FinancialInstrumentSchema):
    ticker_symbol = fields.Str(required=True, validate=validate.Length(max=20))

    def make_obj(self, data, **kwargs):
        return Stock(**data)


class NegotiableObligationSchema(FinancialInstrumentSchema):
    issuer = fields.Str(required=True, validate=validate.Length(min=1, max=100))

    def make_obj(self, data, **kwargs):
        return NegotiableObligation(**data)


class PortfolioSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    description = fields.Str(allow_none=True)
    created_date = fields.DateTime(dump_only=True)
    total_value = fields.Float(dump_only=True)

    class Meta:
        fields = ("id", "name", "description", "created_date", "total_value")


class PortfolioHoldingSchema(Schema):
    id = fields.Int(dump_only=True)
    portfolio_id = fields.Int(required=True)
    instrument_id = fields.Int(required=True)
    quantity = fields.Float(required=True, validate=validate.Range(min=0))
    average_cost = fields.Float(dump_only=True)
    current_value = fields.Float(dump_only=True)
    last_updated = fields.DateTime(dump_only=True)
    instrument = fields.Nested(FinancialInstrumentSchema, dump_only=True)

    class Meta:
        fields = ("id", "portfolio_id", "instrument_id", "quantity", "average_cost", "current_value", "last_updated", "instrument")


class TransactionSchema(Schema):
    id = fields.Int(dump_only=True)
    portfolio_id = fields.Int(required=True)
    instrument_id = fields.Int(required=True)
    transaction_type = fields.Str(required=True, validate=validate.OneOf(["buy", "sell"]))
    quantity = fields.Float(required=True, validate=validate.Range(min=0.001))
    price_per_unit = fields.Float(required=True, validate=validate.Range(min=0))
    total_amount = fields.Float(dump_only=True)
    transaction_date = fields.DateTime(dump_only=True)
    fees = fields.Float(validate=validate.Range(min=0), default=0.0)
    notes = fields.Str(allow_none=True)
    instrument = fields.Nested(FinancialInstrumentSchema, dump_only=True)

    class Meta:
        fields = (
            "id",
            "portfolio_id",
            "instrument_id",
            "transaction_type",
            "quantity",
            "price_per_unit",
            "total_amount",
            "transaction_date",
            "fees",
            "notes",
            "instrument",
        )


# Create schema instances
financial_instrument_schema = FinancialInstrumentSchema()
bond_schema = BondSchema()
loan_schema = LoanSchema()
stock_schema = StockSchema()
obligation_schema = NegotiableObligationSchema()
portfolio_schema = PortfolioSchema()
portfolio_holding_schema = PortfolioHoldingSchema()
transaction_schema = TransactionSchema()
