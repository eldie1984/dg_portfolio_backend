from marshmallow import Schema, fields, validate, validates, ValidationError
from datetime import datetime


class FinancialInstrumentSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    instrument_type = fields.Str(required=True, validate=validate.OneOf(["bond", "loan", "stock", "obligation"]))
    issuer = fields.Str(required=True)
    face_value = fields.Float(required=True)
    currency = fields.Str(validate=validate.Length(equal=3))

    # Bond fields
    payment_date = fields.Date(allow_none=True)
    coupon_rate = fields.Float(allow_none=True, validate=validate.Range(min=0, max=100))

    # Loan fields
    duration_months = fields.Int(allow_none=True, validate=validate.Range(min=1))
    interest_rate = fields.Float(allow_none=True, validate=validate.Range(min=0, max=100))

    # Stock fields
    ticker = fields.Str(allow_none=True)
    exchange = fields.Str(allow_none=True)

    # Obligation fields
    maturity_date = fields.Date(allow_none=True)

    created_at = fields.DateTime(dump_only=True)

    @validates("payment_date")
    def validate_payment_date(self, value):
        if value and value < datetime.now().date():
            raise ValidationError("Payment date must be in the future")

    @validates("maturity_date")
    def validate_maturity_date(self, value):
        if value and value < datetime.now().date():
            raise ValidationError("Maturity date must be in the future")

    class Meta:
        fields = (
            "id",
            "name",
            "instrument_type",
            "issuer",
            "face_value",
            "currency",
            "payment_date",
            "coupon_rate",
            "duration_months",
            "interest_rate",
            "ticker",
            "exchange",
            "maturity_date",
            "created_at",
        )
