from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging

from routers import insiders, companies, transactions
from utils.exceptions import (
    http_exception_handler,
    validation_exception_handler,
    generic_exception_handler
)
from database import database, engine
from models.database_models import Base

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Canadian Insider Trading API",
    description="""
    A comprehensive FastAPI application for Canadian insider trading data:
    
    * **Insider Management**: Track corporate insiders and their positions
    * **Company Management**: Manage publicly traded Canadian companies
    * **Transaction Tracking**: Record and analyze insider trading transactions
    * **Advanced Filtering**: Filter by date ranges, transaction types, values
    * **Statistics**: Generate insights and statistics on trading patterns
    * **Pagination**: Paginated responses for large datasets
    * **Validation**: Request/response validation using Pydantic models
    * **Error Handling**: Custom exception handlers and HTTP error responses
    * **Interactive Documentation**: Auto-generated API docs with Swagger UI
    
    ## Data Source
    This application tracks insider trading activities for Canadian public companies
    as reported to securities regulators.
    
    ## Authentication
    This is a demo application - no authentication required.
    """,
    version="2.0.0",
    contact={
        "name": "API Support",
        "url": "https://github.com/example/canadian-insider-trading-api",
        "email": "support@example.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

app.include_router(insiders.router)
app.include_router(companies.router)
app.include_router(transactions.router)

@app.get("/", tags=["root"])
async def root():
    return {
        "message": "Welcome to Canadian Insider Trading API",
        "version": "2.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "endpoints": {
            "insiders": "/insiders",
            "companies": "/companies",
            "transactions": "/transactions"
        }
    }

@app.get("/health", tags=["health"])
async def health_check():
    return {
        "status": "healthy",
        "message": "Service is running properly"
    }

@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"{request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Response status: {response.status_code}")
    return response

@app.on_event("startup")
async def startup():
    await database.connect()
    Base.metadata.create_all(bind=engine)

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)