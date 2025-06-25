from typing import List, Optional
from fastapi import APIRouter, Query, Path, HTTPException
from datetime import datetime
from models.schemas import User, UserCreate, UserUpdate, SuccessResponse, PaginatedResponse
from utils.exceptions import UserNotFoundError, DuplicateEmailError

router = APIRouter(prefix="/users", tags=["users"])

fake_users_db = [
    {
        "id": 1,
        "name": "John Doe",
        "email": "john@example.com",
        "age": 30,
        "created_at": datetime.now(),
        "is_active": True
    },
    {
        "id": 2,
        "name": "Jane Smith",
        "email": "jane@example.com",
        "age": 25,
        "created_at": datetime.now(),
        "is_active": True
    },
    {
        "id": 3,
        "name": "Bob Johnson",
        "email": "bob@example.com",
        "age": 35,
        "created_at": datetime.now(),
        "is_active": False
    }
]

@router.get("/", response_model=PaginatedResponse, summary="Get all users")
async def get_users(
    skip: int = Query(0, ge=0, description="Number of users to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of users to return"),
    active_only: bool = Query(False, description="Filter active users only")
):
    filtered_users = fake_users_db
    if active_only:
        filtered_users = [user for user in fake_users_db if user["is_active"]]
    
    total = len(filtered_users)
    users = filtered_users[skip:skip + limit]
    
    return PaginatedResponse(
        items=users,
        total=total,
        page=skip // limit + 1,
        per_page=limit,
        pages=(total + limit - 1) // limit
    )

@router.get("/{user_id}", response_model=User, summary="Get user by ID")
async def get_user(
    user_id: int = Path(..., gt=0, description="The ID of the user to retrieve")
):
    user = next((user for user in fake_users_db if user["id"] == user_id), None)
    if not user:
        raise UserNotFoundError(user_id)
    return user

@router.post("/", response_model=User, status_code=201, summary="Create a new user")
async def create_user(user: UserCreate):
    existing_user = next((u for u in fake_users_db if u["email"] == user.email), None)
    if existing_user:
        raise DuplicateEmailError(user.email)
    
    new_user = {
        "id": max([u["id"] for u in fake_users_db], default=0) + 1,
        "name": user.name,
        "email": user.email,
        "age": user.age,
        "created_at": datetime.now(),
        "is_active": True
    }
    fake_users_db.append(new_user)
    return new_user

@router.put("/{user_id}", response_model=User, summary="Update user")
async def update_user(
    user_id: int = Path(..., gt=0, description="The ID of the user to update"),
    user_update: UserUpdate = None
):
    user = next((user for user in fake_users_db if user["id"] == user_id), None)
    if not user:
        raise UserNotFoundError(user_id)
    
    if user_update.email and user_update.email != user["email"]:
        existing_user = next((u for u in fake_users_db if u["email"] == user_update.email), None)
        if existing_user:
            raise DuplicateEmailError(user_update.email)
    
    update_data = user_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if value is not None:
            user[field] = value
    
    return user

@router.delete("/{user_id}", response_model=SuccessResponse, summary="Delete user")
async def delete_user(
    user_id: int = Path(..., gt=0, description="The ID of the user to delete")
):
    user_index = next((i for i, user in enumerate(fake_users_db) if user["id"] == user_id), None)
    if user_index is None:
        raise UserNotFoundError(user_id)
    
    deleted_user = fake_users_db.pop(user_index)
    return SuccessResponse(
        message=f"User {deleted_user['name']} deleted successfully",
        data={"deleted_user_id": user_id}
    )

@router.get("/search/", response_model=List[User], summary="Search users by name")
async def search_users(
    q: str = Query(..., min_length=1, description="Search query for user name"),
    limit: int = Query(10, ge=1, le=50, description="Maximum number of results")
):
    matching_users = [
        user for user in fake_users_db 
        if q.lower() in user["name"].lower()
    ]
    return matching_users[:limit]