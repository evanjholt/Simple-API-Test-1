# Simple API Test Application - Systems Profile

## Overview
**Application Type:** REST API Web Service  
**Framework:** FastAPI 0.104.1  
**Language:** Python  
**Architecture:** Modular Monolith with Router-based Organization  
**Data Storage:** In-memory (Demo/Development)  
**Deployment:** Uvicorn ASGI Server  

## System Architecture

### Core Components
```
├── main.py                 # Application entry point and configuration
├── requirements.txt        # Python dependencies
├── routers/               # API endpoint organization
│   ├── users.py           # User management endpoints
│   └── items.py           # Item management endpoints
├── models/                # Data models and schemas
│   └── schemas.py         # Pydantic models for validation
└── utils/                 # Utility functions
    └── exceptions.py      # Custom exception handlers
```

### Technology Stack
- **Web Framework:** FastAPI 0.104.1
- **ASGI Server:** Uvicorn 0.24.0
- **Data Validation:** Pydantic 2.5.0
- **File Upload Support:** python-multipart 0.0.6

## API Endpoints

### User Management (`/users`)
- `GET /users/` - List users with pagination and filtering
- `GET /users/{user_id}` - Get specific user by ID
- `POST /users/` - Create new user
- `PUT /users/{user_id}` - Update user
- `DELETE /users/{user_id}` - Delete user
- `GET /users/search/` - Search users by name

### Item Management (`/items`)
- `GET /items/` - List items with advanced filtering and pagination
- `GET /items/{item_id}` - Get specific item by ID
- `POST /items/` - Create new item
- `PUT /items/{item_id}` - Update item
- `DELETE /items/{item_id}` - Delete item
- `GET /items/categories/` - Get all available categories
- `GET /items/user/{user_id}` - Get items by specific user
- `PATCH /items/{item_id}/availability` - Toggle item availability

### System Endpoints
- `GET /` - Root endpoint with API information
- `GET /health` - Health check endpoint
- `GET /docs` - Swagger UI documentation
- `GET /redoc` - ReDoc documentation

## Data Models

### User Schema
```python
{
    "id": int,
    "name": str (1-100 chars),
    "email": str,
    "age": int (0-150, optional),
    "created_at": datetime,
    "is_active": bool
}
```

### Item Schema
```python
{
    "id": int,
    "title": str (1-200 chars),
    "description": str (max 1000 chars, optional),
    "price": float (> 0),
    "category": str (1-50 chars),
    "owner_id": int,
    "created_at": datetime,
    "is_available": bool
}
```

## Features

### Advanced Filtering
- **Items:** Category, price range (min/max), availability status
- **Users:** Active status filtering
- **Search:** Name-based user search with query strings

### Pagination
- Configurable skip/limit parameters
- Response includes: total count, page number, items per page, total pages
- Limits: 1-100 items per request, 1-50 for search results

### Validation & Error Handling
- **Input Validation:** Pydantic models with field constraints
- **Custom Exceptions:** UserNotFoundError, ItemNotFoundError, DuplicateEmailError
- **Global Handlers:** HTTP errors, validation errors, generic exceptions
- **Logging:** Request/response logging and error tracking

### Cross-Origin Resource Sharing
- **CORS:** Enabled for all origins (development configuration)
- **Methods:** All HTTP methods allowed
- **Headers:** All headers allowed

## Security Considerations
- **Current State:** No authentication/authorization implemented
- **Data Exposure:** All endpoints are publicly accessible
- **CORS Policy:** Permissive (suitable for development only)
- **Input Validation:** Comprehensive via Pydantic models

## Performance Characteristics
- **Data Storage:** In-memory lists (non-persistent)
- **Concurrency:** ASGI-based async request handling
- **Filtering:** Linear search operations (O(n) complexity)
- **Pagination:** Slice-based pagination (O(1) after filtering)

## Development & Testing
- **Documentation:** Auto-generated via FastAPI (Swagger UI + ReDoc)
- **Request Logging:** All requests logged with method, URL, and response status
- **Error Tracking:** Comprehensive exception logging with stack traces
- **Health Monitoring:** Dedicated health check endpoint

## Deployment Configuration
- **Host:** 0.0.0.0 (all interfaces)
- **Port:** 8000 (configurable)
- **Server:** Uvicorn with standard features
- **Environment:** Development-ready with auto-reload capabilities

### ngrok Deployment for Remote Testing
Two methods available for exposing the API publicly via ngrok:

#### Method 1: Python Script (Recommended)
```bash
# Install dependencies
pip install -r requirements.txt

# Deploy with default settings
python deploy_ngrok.py

# Deploy with custom port
python deploy_ngrok.py --port 8080

# Deploy with ngrok auth token
python deploy_ngrok.py --auth-token YOUR_TOKEN
```

#### Method 2: Shell Script
```bash
# Make executable
chmod +x ngrok_deploy.sh

# Deploy with default port 8000
./ngrok_deploy.sh

# Deploy with custom port
./ngrok_deploy.sh 8080

# Deploy with auth token
./ngrok_deploy.sh 8000 YOUR_TOKEN
```

**Features:**
- Automatic server startup and tunnel creation
- Public URL generation for external testing
- Graceful shutdown with Ctrl+C
- Real-time status monitoring
- Direct links to API documentation

**Use Cases:**
- Testing API from external programs
- Sharing API with team members
- Mobile app development testing
- Webhook endpoint testing

## 🌐 Current Live Deployment (ngrok)

### Active Public URLs
- **🔗 Public API Base URL:** https://be48-51-143-4-82.ngrok-free.app
- **📚 Swagger UI Documentation:** https://be48-51-143-4-82.ngrok-free.app/docs
- **📖 ReDoc Documentation:** https://be48-51-143-4-82.ngrok-free.app/redoc
- **💓 Health Check:** https://be48-51-143-4-82.ngrok-free.app/health

### API Endpoints for Testing
#### User Management
- **📋 List Users:** `GET https://be48-51-143-4-82.ngrok-free.app/users`
- **👤 Get User by ID:** `GET https://be48-51-143-4-82.ngrok-free.app/users/{id}`
- **➕ Create User:** `POST https://be48-51-143-4-82.ngrok-free.app/users`
- **✏️ Update User:** `PUT https://be48-51-143-4-82.ngrok-free.app/users/{id}`
- **🗑️ Delete User:** `DELETE https://be48-51-143-4-82.ngrok-free.app/users/{id}`
- **🔍 Search Users:** `GET https://be48-51-143-4-82.ngrok-free.app/users/search/?q=name`

#### Item Management
- **📋 List Items:** `GET https://be48-51-143-4-82.ngrok-free.app/items`
- **📦 Get Item by ID:** `GET https://be48-51-143-4-82.ngrok-free.app/items/{id}`
- **➕ Create Item:** `POST https://be48-51-143-4-82.ngrok-free.app/items`
- **✏️ Update Item:** `PUT https://be48-51-143-4-82.ngrok-free.app/items/{id}`
- **🗑️ Delete Item:** `DELETE https://be48-51-143-4-82.ngrok-free.app/items/{id}`
- **🏷️ Get Categories:** `GET https://be48-51-143-4-82.ngrok-free.app/items/categories/`
- **👤 Get User's Items:** `GET https://be48-51-143-4-82.ngrok-free.app/items/user/{user_id}`
- **🔄 Toggle Availability:** `PATCH https://be48-51-143-4-82.ngrok-free.app/items/{id}/availability`

### Example API Calls
```bash
# Get all users
curl https://be48-51-143-4-82.ngrok-free.app/users

# Get all items with filtering
curl "https://be48-51-143-4-82.ngrok-free.app/items?category=Electronics&min_price=100"

# Health check
curl https://be48-51-143-4-82.ngrok-free.app/health
```

### Deployment Details
- **Port:** 8090 (local)
- **Auth Token:** Configured
- **Status:** Active and accessible from any internet-connected device
- **Local Server:** http://127.0.0.1:8090

> **Note:** These URLs are active and can be accessed from any computer with internet access. Perfect for testing your API from external programs or sharing with team members!

## Sample Data
- **Users:** 3 pre-loaded demo users
- **Items:** 4 sample items across different categories (Electronics, Furniture, Appliances, Books)
- **Categories:** Dynamic list derived from existing items

## API Documentation Access
- **Swagger UI:** `/docs` endpoint
- **ReDoc:** `/redoc` endpoint
- **OpenAPI Schema:** Auto-generated from code annotations

## Limitations
- **Persistence:** Data resets on server restart
- **Scalability:** In-memory storage not suitable for production
- **Security:** No authentication or rate limiting
- **Database:** No relational integrity or advanced querying
- **File Storage:** No file upload/storage capabilities (despite multipart support)