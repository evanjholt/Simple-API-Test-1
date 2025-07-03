# Canadian Insider Trading API

A comprehensive FastAPI application for tracking and analyzing Canadian insider trading data. This API provides endpoints for managing corporate insiders, companies, and trading transactions with advanced filtering and statistics capabilities.

## Features

- **Insider Management**: Track corporate insiders and their positions
- **Company Management**: Manage publicly traded Canadian companies  
- **Transaction Tracking**: Record and analyze insider trading transactions
- **Advanced Filtering**: Filter by date ranges, transaction types, values
- **Statistics**: Generate insights and statistics on trading patterns
- **Pagination**: Paginated responses for large datasets
- **Interactive Documentation**: Auto-generated API docs with Swagger UI
- **Error Handling**: Custom exception handlers and validation
- **CORS Support**: Cross-origin resource sharing enabled

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/Simple-API-Test-1.git
   cd Simple-API-Test-1
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   python main.py
   ```

   The API will be available at `http://localhost:8000`

4. **Access the documentation:**
   - Swagger UI: `http://localhost:8000/docs`
   - ReDoc: `http://localhost:8000/redoc`

## API Endpoints

### Root Endpoints
- `GET /` - Welcome message and API information
- `GET /health` - Health check endpoint

### Insiders
- `GET /insiders` - List all insiders with filtering and pagination
- `POST /insiders` - Create a new insider
- `GET /insiders/{insider_id}` - Get insider by ID
- `PUT /insiders/{insider_id}` - Update insider
- `DELETE /insiders/{insider_id}` - Delete insider

### Companies
- `GET /companies` - List all companies with filtering and pagination
- `POST /companies` - Create a new company
- `GET /companies/{company_id}` - Get company by ID
- `PUT /companies/{company_id}` - Update company
- `DELETE /companies/{company_id}` - Delete company

### Transactions
- `GET /transactions` - List all transactions with filtering and pagination
- `POST /transactions` - Create a new transaction
- `GET /transactions/{transaction_id}` - Get transaction by ID
- `PUT /transactions/{transaction_id}` - Update transaction
- `DELETE /transactions/{transaction_id}` - Delete transaction

## Usage Examples

### Get all insiders
```bash
curl -X GET "http://localhost:8000/insiders" -H "accept: application/json"
```

### Create a new company
```bash
curl -X POST "http://localhost:8000/companies" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Example Corp",
    "ticker": "EXAMPLE",
    "exchange": "TSX"
  }'
```

### Get transactions with filtering
```bash
curl -X GET "http://localhost:8000/transactions?limit=10&offset=0" \
  -H "accept: application/json"
```

## Project Structure

```
Simple-API-Test-1/
├── main.py                    # FastAPI application entry point
├── database.py                # Database configuration and connection
├── requirements.txt           # Python dependencies
├── models/                    # Data models
│   ├── __init__.py
│   ├── database_models.py     # SQLAlchemy models
│   └── schemas.py             # Pydantic schemas
├── routers/                   # API route handlers
│   ├── __init__.py
│   ├── companies.py           # Company endpoints
│   ├── insiders.py            # Insider endpoints
│   └── transactions.py        # Transaction endpoints
├── utils/                     # Utility functions
│   ├── __init__.py
│   └── exceptions.py          # Custom exception handlers
├── deploy_ngrok.py            # Ngrok deployment script
├── ngrok_deploy.sh            # Shell script for ngrok deployment
├── populate_data.py           # Database seeding script
├── quick_populate.py          # Quick database population
└── insider_trading.db         # SQLite database file
```

## Development Setup

### Prerequisites
- Python 3.7+
- pip (Python package manager)

### Local Development
1. **Set up virtual environment (recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Initialize database with sample data:**
   ```bash
   python populate_data.py
   # or for quick setup:
   python quick_populate.py
   ```

4. **Run the development server:**
   ```bash
   python main.py
   ```

### Ngrok Deployment
For exposing your local API to the internet using ngrok:

1. **Using Python script:**
   ```bash
   python deploy_ngrok.py
   ```

2. **Using shell script:**
   ```bash
   ./ngrok_deploy.sh
   ```

## Technology Stack

- **FastAPI**: Modern web framework for building APIs
- **SQLAlchemy**: SQL toolkit and ORM
- **Pydantic**: Data validation using Python type hints
- **Uvicorn**: ASGI server for running FastAPI
- **SQLite**: Lightweight database for development
- **Ngrok**: Secure tunneling for local development

## License

This project is licensed under the MIT License. 
