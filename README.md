# Financial Instruments API

A Flask-based REST API for managing various financial instruments including bonds, loans, stocks, and negotiable obligations with comprehensive portfolio management capabilities.

## Features

- Create and manage different types of financial instruments
- Support for bonds with partial payment dates
- Support for loans with interest rates and durations
- Support for stocks with ticker symbols
- Support for negotiable obligations
- **Portfolio Management**: Create portfolios and track holdings
- **Buy/Sell Operations**: Execute transactions with automatic portfolio updates
- **Price Tracking**: Track buying, selling, and current prices for each instrument
- **Transaction History**: Complete audit trail of all portfolio transactions
- Input validation and error handling
- RESTful API design

## Setup

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Initialize the database:
   ```bash
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```

4. Run the application:
   ```bash
   python run.py
   ```

## API Endpoints

### Financial Instruments

#### Create a Bond
```
POST /api/bonds
Content-Type: application/json

{
  "name": "US Treasury Bond 2025",
  "instrument_type": "bond",
  "face_value": 1000,
  "currency": "USD",
  "coupon_rate": 2.5,
  "maturity_date": "2025-12-31T00:00:00Z",
  "partial_payment_date": "2023-06-30T00:00:00Z",
  "payment_frequency": 6,
  "current_price": 995.50,
  "buying_price": 990.00,
  "selling_price": 1000.00
}
```

#### Create a Loan
```
POST /api/loans
Content-Type: application/json

{
  "name": "Business Loan 2023",
  "instrument_type": "loan",
  "face_value": 50000,
  "currency": "USD",
  "interest_rate": 5.75,
  "duration_months": 60,
  "current_price": 49500.00
}
```

#### Create a Stock
```
POST /api/stocks
Content-Type: application/json

{
  "name": "Apple Inc.",
  "instrument_type": "stock",
  "ticker_symbol": "AAPL",
  "face_value": 150.25,
  "current_price": 175.30,
  "buying_price": 170.00,
  "selling_price": 180.00
}
```

#### Create a Negotiable Obligation
```
POST /api/obligations
Content-Type: application/json

{
  "name": "Corporate Bond 2030",
  "instrument_type": "obligation",
  "face_value": 5000,
  "currency": "USD",
  "issuer": "Tech Corp Inc.",
  "maturity_date": "2030-12-31T00:00:00Z",
  "current_price": 4950.00
}
```

#### List All Instruments
```
GET /api/instruments
```

#### Update Instrument Price
```
PUT /api/instruments/{instrument_id}/price
Content-Type: application/json

{
  "current_price": 175.50,
  "buying_price": 170.00,
  "selling_price": 180.00
}
```

### Portfolio Management

#### Create a Portfolio
```
POST /api/portfolios
Content-Type: application/json

{
  "name": "My Investment Portfolio",
  "description": "Diversified portfolio for long-term growth"
}
```

#### List All Portfolios
```
GET /api/portfolios
```

#### Get Portfolio Details
```
GET /api/portfolios/{portfolio_id}
```

#### Get Portfolio Holdings
```
GET /api/portfolios/{portfolio_id}/holdings
```

#### Get Portfolio Transaction History
```
GET /api/portfolios/{portfolio_id}/transactions
```

#### Buy Instrument
```
POST /api/portfolios/{portfolio_id}/buy
Content-Type: application/json

{
  "instrument_id": 1,
  "quantity": 100,
  "price_per_unit": 175.30,
  "fees": 9.99,
  "notes": "Initial purchase of AAPL shares"
}
```

#### Sell Instrument
```
POST /api/portfolios/{portfolio_id}/sell
Content-Type: application/json

{
  "instrument_id": 1,
  "quantity": 50,
  "price_per_unit": 180.00,
  "fees": 9.99,
  "notes": "Partial sale for profit taking"
}
```

## Data Models

### Financial Instruments (Base)
All financial instruments include these common fields:
- `id`: Integer (auto-generated)
- `name`: String (required)
- `instrument_type`: String (required: "bond", "loan", "stock", "obligation")
- `face_value`: Float (required, > 0)
- `currency`: String (3-letter code, default: "USD")
- `issue_date`: DateTime (auto-generated)
- `current_price`: Float (optional, > 0)
- `buying_price`: Float (optional, > 0)
- `selling_price`: Float (optional, > 0)
- `last_price_update`: DateTime (auto-generated)

### Bond
Extends Financial Instrument with:
- `coupon_rate`: Float (optional, 0-100)
- `maturity_date`: DateTime (optional)
- `partial_payment_date`: DateTime (required)
- `payment_frequency`: Integer (optional, in months)

### Loan
Extends Financial Instrument with:
- `interest_rate`: Float (required, 0-100)
- `duration_months`: Integer (required, > 0)

### Stock
Extends Financial Instrument with:
- `ticker_symbol`: String (required, max 20 chars)

### Negotiable Obligation
Extends Financial Instrument with:
- `issuer`: String (required, max 100 chars)
- `maturity_date`: DateTime (optional)

### Portfolio
- `id`: Integer (auto-generated)
- `name`: String (required, max 100 chars)
- `description`: Text (optional)
- `created_date`: DateTime (auto-generated)
- `total_value`: Float (calculated)

### Portfolio Holding
- `id`: Integer (auto-generated)
- `portfolio_id`: Integer (required)
- `instrument_id`: Integer (required)
- `quantity`: Float (required, > 0)
- `average_cost`: Float (calculated)
- `current_value`: Float (calculated)
- `last_updated`: DateTime (auto-generated)

### Transaction
- `id`: Integer (auto-generated)
- `portfolio_id`: Integer (required)
- `instrument_id`: Integer (required)
- `transaction_type`: String (required: "buy" or "sell")
- `quantity`: Float (required, > 0)
- `price_per_unit`: Float (required, > 0)
- `total_amount`: Float (calculated)
- `transaction_date`: DateTime (auto-generated)
- `fees`: Float (optional, default: 0.0)
- `notes`: Text (optional)

## Error Responses

All error responses follow this format:
```json
{
  "message": "Error description",
  "errors": "Detailed error information"
}
```

Common status codes:
- 400: Bad Request - Invalid input data
- 404: Not Found - Resource not found
- 422: Unprocessable Entity - Validation error
- 500: Internal Server Error - Server error
