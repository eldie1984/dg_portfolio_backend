from app import create_app, db
from app.models import FinancialInstrument, Bond, Loan, Stock, NegotiableObligation

app = create_app()


@app.shell_context_processor
def make_shell_context():
    return {
        "db": db,
        "FinancialInstrument": FinancialInstrument,
        "Bond": Bond,
        "Loan": Loan,
        "Stock": Stock,
        "NegotiableObligation": NegotiableObligation,
    }


if __name__ == "__main__":
    app.run(debug=True)
