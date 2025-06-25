from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging

from routers import users, items
from utils.exceptions import (
    http_exception_handler,
    validation_exception_handler,
    generic_exception_handler
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Simple API Test Application",
    description="""
    A comprehensive FastAPI application demonstrating:
    
    * **User Management**: Create, read, update, and delete users
    * **Item Management**: Manage items with categories and pricing
    * **Advanced Filtering**: Filter items by price, category, availability
    * **Pagination**: Paginated responses for large datasets
    * **Validation**: Request/response validation using Pydantic models
    * **Error Handling**: Custom exception handlers and HTTP error responses
    * **Interactive Documentation**: Auto-generated API docs with Swagger UI
    
    ## Authentication
    This is a demo application - no authentication required.
    
    ## Rate Limiting
    No rate limiting implemented in this demo.
    """,
    version="1.0.0",
    contact={
        "name": "API Support",
        "url": "https://github.com/example/simple-api-test",
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

app.include_router(users.router)
app.include_router(items.router)

@app.get("/", tags=["root"])
async def root():
    return {
        "message": "Welcome to Simple API Test Application",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "endpoints": {
            "users": "/users",
            "items": "/items"
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)