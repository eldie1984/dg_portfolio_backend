from flask import Blueprint, request, jsonify
from datetime import datetime
from app import db
from app.models import Bond, Loan, Stock, NegotiableObligation, Portfolio, PortfolioHolding, Transaction
from app.schemas import (
    bond_schema,
    loan_schema,
    stock_schema,
    obligation_schema,
    financial_instrument_schema,
    portfolio_schema,
    portfolio_holding_schema,
    transaction_schema,
)

api_bp = Blueprint("api", __name__)


@api_bp.route("/instruments", methods=["GET"])
def get_instruments():
    instruments = Bond.query.union(Loan.query, Stock.query, NegotiableObligation.query).all()
    return jsonify([financial_instrument_schema.dump(i) for i in instruments])


@api_bp.route("/bonds", methods=["POST"])
def create_bond():
    json_data = request.get_json()
    if not json_data:
        return {"message": "No input data provided"}, 400

    # Validate and deserialize input
    try:
        data = bond_schema.load(json_data)
    except Exception as e:
        return {"message": "Validation error", "errors": str(e)}, 422

    # Create new bond
    bond = bond_schema.make_obj(data)
    db.session.add(bond)
    db.session.commit()

    return bond_schema.dump(bond), 201


@api_bp.route("/loans", methods=["POST"])
def create_loan():
    json_data = request.get_json()
    if not json_data:
        return {"message": "No input data provided"}, 400

    try:
        data = loan_schema.load(json_data)
    except Exception as e:
        return {"message": "Validation error", "errors": str(e)}, 422

    loan = loan_schema.make_obj(data)
    db.session.add(loan)
    db.session.commit()

    return loan_schema.dump(loan), 201


@api_bp.route("/stocks", methods=["POST"])
def create_stock():
    json_data = request.get_json()
    if not json_data:
        return {"message": "No input data provided"}, 400

    try:
        data = stock_schema.load(json_data)
    except Exception as e:
        return {"message": "Validation error", "errors": str(e)}, 422

    stock = stock_schema.make_obj(data)
    db.session.add(stock)
    db.session.commit()

    return stock_schema.dump(stock), 201


@api_bp.route("/obligations", methods=["POST"])
def create_obligation():
    json_data = request.get_json()
    if not json_data:
        return {"message": "No input data provided"}, 400

    try:
        data = obligation_schema.load(json_data)
    except Exception as e:
        return {"message": "Validation error", "errors": str(e)}, 422

    obligation = obligation_schema.make_obj(data)
    db.session.add(obligation)
    db.session.commit()

    return obligation_schema.dump(obligation), 201


# Portfolio Management Endpoints


@api_bp.route("/portfolios", methods=["POST"])
def create_portfolio():
    json_data = request.get_json()
    if not json_data:
        return {"message": "No input data provided"}, 400

    try:
        data = portfolio_schema.load(json_data)
    except Exception as e:
        return {"message": "Validation error", "errors": str(e)}, 422

    portfolio = Portfolio(**data)
    db.session.add(portfolio)
    db.session.commit()

    return portfolio_schema.dump(portfolio), 201


@api_bp.route("/portfolios", methods=["GET"])
def get_portfolios():
    portfolios = Portfolio.query.all()
    return jsonify([portfolio_schema.dump(p) for p in portfolios])


@api_bp.route("/portfolios/<int:portfolio_id>", methods=["GET"])
def get_portfolio(portfolio_id):
    portfolio = Portfolio.query.get_or_404(portfolio_id)
    return portfolio_schema.dump(portfolio)


@api_bp.route("/portfolios/<int:portfolio_id>/holdings", methods=["GET"])
def get_portfolio_holdings(portfolio_id):
    portfolio = Portfolio.query.get_or_404(portfolio_id)
    holdings = PortfolioHolding.query.filter_by(portfolio_id=portfolio_id).all()
    return jsonify([portfolio_holding_schema.dump(h) for h in holdings])


@api_bp.route("/portfolios/<int:portfolio_id>/transactions", methods=["GET"])
def get_portfolio_transactions(portfolio_id):
    portfolio = Portfolio.query.get_or_404(portfolio_id)
    transactions = Transaction.query.filter_by(portfolio_id=portfolio_id).order_by(Transaction.transaction_date.desc()).all()
    return jsonify([transaction_schema.dump(t) for t in transactions])


@api_bp.route("/portfolios/<int:portfolio_id>/buy", methods=["POST"])
def buy_instrument(portfolio_id):
    json_data = request.get_json()
    if not json_data:
        return {"message": "No input data provided"}, 400

    # Validate required fields
    required_fields = ["instrument_id", "quantity", "price_per_unit"]
    for field in required_fields:
        if field not in json_data:
            return {"message": f"Missing required field: {field}"}, 400

    portfolio = Portfolio.query.get_or_404(portfolio_id)
    instrument_id = json_data["instrument_id"]
    quantity = float(json_data["quantity"])
    price_per_unit = float(json_data["price_per_unit"])
    fees = float(json_data.get("fees", 0.0))
    notes = json_data.get("notes", "")

    # Verify instrument exists
    instrument = (
        Bond.query.get(instrument_id)
        or Loan.query.get(instrument_id)
        or Stock.query.get(instrument_id)
        or NegotiableObligation.query.get(instrument_id)
    )

    if not instrument:
        return {"message": "Instrument not found"}, 404

    # Calculate total amount
    total_amount = (quantity * price_per_unit) + fees

    # Create transaction
    transaction = Transaction(
        portfolio_id=portfolio_id,
        instrument_id=instrument_id,
        transaction_type="buy",
        quantity=quantity,
        price_per_unit=price_per_unit,
        total_amount=total_amount,
        fees=fees,
        notes=notes,
    )

    # Update or create holding
    holding = PortfolioHolding.query.filter_by(portfolio_id=portfolio_id, instrument_id=instrument_id).first()

    if holding:
        # Update existing holding
        total_cost = (holding.quantity * holding.average_cost) + total_amount
        holding.quantity += quantity
        holding.average_cost = total_cost / holding.quantity
        holding.last_updated = datetime.utcnow()
    else:
        # Create new holding
        holding = PortfolioHolding(
            portfolio_id=portfolio_id, instrument_id=instrument_id, quantity=quantity, average_cost=price_per_unit + (fees / quantity)
        )
        db.session.add(holding)

    # Update instrument buying price
    instrument.buying_price = price_per_unit
    instrument.current_price = price_per_unit
    instrument.last_price_update = datetime.utcnow()

    db.session.add(transaction)
    db.session.commit()

    return transaction_schema.dump(transaction), 201


@api_bp.route("/portfolios/<int:portfolio_id>/sell", methods=["POST"])
def sell_instrument(portfolio_id):
    json_data = request.get_json()
    if not json_data:
        return {"message": "No input data provided"}, 400

    # Validate required fields
    required_fields = ["instrument_id", "quantity", "price_per_unit"]
    for field in required_fields:
        if field not in json_data:
            return {"message": f"Missing required field: {field}"}, 400

    portfolio = Portfolio.query.get_or_404(portfolio_id)
    instrument_id = json_data["instrument_id"]
    quantity = float(json_data["quantity"])
    price_per_unit = float(json_data["price_per_unit"])
    fees = float(json_data.get("fees", 0.0))
    notes = json_data.get("notes", "")

    # Check if holding exists and has sufficient quantity
    holding = PortfolioHolding.query.filter_by(portfolio_id=portfolio_id, instrument_id=instrument_id).first()

    if not holding or holding.quantity < quantity:
        return {"message": "Insufficient holdings to sell"}, 400

    # Verify instrument exists
    instrument = (
        Bond.query.get(instrument_id)
        or Loan.query.get(instrument_id)
        or Stock.query.get(instrument_id)
        or NegotiableObligation.query.get(instrument_id)
    )

    if not instrument:
        return {"message": "Instrument not found"}, 404

    # Calculate total amount (subtract fees from sale proceeds)
    total_amount = (quantity * price_per_unit) - fees

    # Create transaction
    transaction = Transaction(
        portfolio_id=portfolio_id,
        instrument_id=instrument_id,
        transaction_type="sell",
        quantity=quantity,
        price_per_unit=price_per_unit,
        total_amount=total_amount,
        fees=fees,
        notes=notes,
    )

    # Update holding
    holding.quantity -= quantity
    holding.last_updated = datetime.utcnow()

    # Remove holding if quantity becomes zero
    if holding.quantity == 0:
        db.session.delete(holding)

    # Update instrument selling price
    instrument.selling_price = price_per_unit
    instrument.current_price = price_per_unit
    instrument.last_price_update = datetime.utcnow()

    db.session.add(transaction)
    db.session.commit()

    return transaction_schema.dump(transaction), 201


@api_bp.route("/instruments/<int:instrument_id>/price", methods=["PUT"])
def update_instrument_price(instrument_id):
    json_data = request.get_json()
    if not json_data or "current_price" not in json_data:
        return {"message": "Current price is required"}, 400

    # Find instrument
    instrument = (
        Bond.query.get(instrument_id)
        or Loan.query.get(instrument_id)
        or Stock.query.get(instrument_id)
        or NegotiableObligation.query.get(instrument_id)
    )

    if not instrument:
        return {"message": "Instrument not found"}, 404

    # Update price
    instrument.current_price = float(json_data["current_price"])
    instrument.last_price_update = datetime.utcnow()

    # Update buying/selling prices if provided
    if "buying_price" in json_data:
        instrument.buying_price = float(json_data["buying_price"])
    if "selling_price" in json_data:
        instrument.selling_price = float(json_data["selling_price"])

    db.session.commit()

    return financial_instrument_schema.dump(instrument)
