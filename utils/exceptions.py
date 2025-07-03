from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging

logger = logging.getLogger(__name__)

class InsiderNotFoundError(HTTPException):
    def __init__(self, insider_id: int):
        super().__init__(status_code=404, detail=f"Insider with id {insider_id} not found")

class CompanyNotFoundError(HTTPException):
    def __init__(self, company_id: int):
        super().__init__(status_code=404, detail=f"Company with id {company_id} not found")

class TransactionNotFoundError(HTTPException):
    def __init__(self, transaction_id: int):
        super().__init__(status_code=404, detail=f"Transaction with id {transaction_id} not found")

class DuplicateSymbolError(HTTPException):
    def __init__(self, symbol: str):
        super().__init__(status_code=400, detail=f"Company with symbol {symbol} already exists")

async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    logger.error(f"HTTP {exc.status_code}: {exc.detail} - Path: {request.url.path}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "status_code": exc.status_code, "path": request.url.path}
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error(f"Validation error on {request.url.path}: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={
            "detail": "Validation error",
            "errors": exc.errors(),
            "status_code": 422,
            "path": request.url.path
        }
    )

async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unexpected error on {request.url.path}: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "status_code": 500,
            "path": request.url.path
        }
    )