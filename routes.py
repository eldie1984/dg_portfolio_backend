from flask import Blueprint, request, jsonify
from .models import FinancialInstrument, db
from .schemas import FinancialInstrumentSchema
from datetime import datetime

api = Blueprint("api", __name__)

instrument_schema = FinancialInstrumentSchema()
instruments_schema = FinancialInstrumentSchema(many=True)


@api.route("/instruments", methods=["GET"])
def get_instruments():
    instruments = FinancialInstrument.query.all()
    return jsonify({"status": "success", "data": instruments_schema.dump(instruments)})


@api.route("/instruments/<int:instrument_id>", methods=["GET"])
def get_instrument(instrument_id):
    instrument = FinancialInstrument.query.get_or_404(instrument_id)
    return jsonify({"status": "success", "data": instrument_schema.dump(instrument)})


@api.route("/instruments", methods=["POST"])
def create_instrument():
    json_data = request.get_json()

    try:
        data = instrument_schema.load(json_data)
    except Exception as e:
        return jsonify({"status": "error", "message": "Invalid data", "errors": str(e)}), 400

    instrument = FinancialInstrument(**data)
    db.session.add(instrument)
    db.session.commit()

    return jsonify({"status": "success", "data": instrument_schema.dump(instrument)}), 201


@api.route("/instruments/<int:instrument_id>", methods=["PUT"])
def update_instrument(instrument_id):
    instrument = FinancialInstrument.query.get_or_404(instrument_id)
    json_data = request.get_json()

    try:
        data = instrument_schema.load(json_data, partial=True)
    except Exception as e:
        return jsonify({"status": "error", "message": "Invalid data", "errors": str(e)}), 400

    for key, value in data.items():
        setattr(instrument, key, value)

    db.session.commit()

    return jsonify({"status": "success", "data": instrument_schema.dump(instrument)})


@api.route("/instruments/<int:instrument_id>", methods=["DELETE"])
def delete_instrument(instrument_id):
    instrument = FinancialInstrument.query.get_or_404(instrument_id)
    db.session.delete(instrument)
    db.session.commit()

    return jsonify({"status": "success", "message": "Instrument deleted successfully"})


@api.route("/instruments/type/<instrument_type>", methods=["GET"])
def get_instruments_by_type(instrument_type):
    if instrument_type not in ["bond", "loan", "stock", "obligation"]:
        return jsonify({"status": "error", "message": "Invalid instrument type"}), 400

    instruments = FinancialInstrument.query.filter_by(instrument_type=instrument_type).all()
    return jsonify({"status": "success", "data": instruments_schema.dump(instruments)})
