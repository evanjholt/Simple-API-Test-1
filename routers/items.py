from typing import List, Optional
from fastapi import APIRouter, Query, Path, HTTPException
from datetime import datetime
from models.schemas import Item, ItemCreate, ItemUpdate, SuccessResponse, PaginatedResponse
from utils.exceptions import ItemNotFoundError, UserNotFoundError

router = APIRouter(prefix="/items", tags=["items"])

fake_items_db = [
    {
        "id": 1,
        "title": "Laptop Computer",
        "description": "High-performance laptop for programming",
        "price": 999.99,
        "category": "Electronics",
        "owner_id": 1,
        "created_at": datetime.now(),
        "is_available": True
    },
    {
        "id": 2,
        "title": "Office Chair",
        "description": "Ergonomic office chair with lumbar support",
        "price": 299.50,
        "category": "Furniture",
        "owner_id": 1,
        "created_at": datetime.now(),
        "is_available": True
    },
    {
        "id": 3,
        "title": "Coffee Maker",
        "description": "Automatic coffee maker with timer",
        "price": 89.99,
        "category": "Appliances",
        "owner_id": 2,
        "created_at": datetime.now(),
        "is_available": False
    },
    {
        "id": 4,
        "title": "Python Programming Book",
        "description": "Complete guide to Python programming",
        "price": 45.00,
        "category": "Books",
        "owner_id": 3,
        "created_at": datetime.now(),
        "is_available": True
    }
]

fake_users_db = [1, 2, 3]

@router.get("/", response_model=PaginatedResponse, summary="Get all items")
async def get_items(
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of items to return"),
    category: Optional[str] = Query(None, description="Filter by category"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum price filter"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum price filter"),
    available_only: bool = Query(False, description="Show only available items")
):
    filtered_items = fake_items_db
    
    if category:
        filtered_items = [item for item in filtered_items if item["category"].lower() == category.lower()]
    
    if min_price is not None:
        filtered_items = [item for item in filtered_items if item["price"] >= min_price]
    
    if max_price is not None:
        filtered_items = [item for item in filtered_items if item["price"] <= max_price]
    
    if available_only:
        filtered_items = [item for item in filtered_items if item["is_available"]]
    
    total = len(filtered_items)
    items = filtered_items[skip:skip + limit]
    
    return PaginatedResponse(
        items=items,
        total=total,
        page=skip // limit + 1,
        per_page=limit,
        pages=(total + limit - 1) // limit
    )

@router.get("/{item_id}", response_model=Item, summary="Get item by ID")
async def get_item(
    item_id: int = Path(..., gt=0, description="The ID of the item to retrieve")
):
    item = next((item for item in fake_items_db if item["id"] == item_id), None)
    if not item:
        raise ItemNotFoundError(item_id)
    return item

@router.post("/", response_model=Item, status_code=201, summary="Create a new item")
async def create_item(item: ItemCreate):
    if item.owner_id not in fake_users_db:
        raise UserNotFoundError(item.owner_id)
    
    new_item = {
        "id": max([i["id"] for i in fake_items_db], default=0) + 1,
        "title": item.title,
        "description": item.description,
        "price": item.price,
        "category": item.category,
        "owner_id": item.owner_id,
        "created_at": datetime.now(),
        "is_available": True
    }
    fake_items_db.append(new_item)
    return new_item

@router.put("/{item_id}", response_model=Item, summary="Update item")
async def update_item(
    item_id: int = Path(..., gt=0, description="The ID of the item to update"),
    item_update: ItemUpdate = None
):
    item = next((item for item in fake_items_db if item["id"] == item_id), None)
    if not item:
        raise ItemNotFoundError(item_id)
    
    update_data = item_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if value is not None:
            item[field] = value
    
    return item

@router.delete("/{item_id}", response_model=SuccessResponse, summary="Delete item")
async def delete_item(
    item_id: int = Path(..., gt=0, description="The ID of the item to delete")
):
    item_index = next((i for i, item in enumerate(fake_items_db) if item["id"] == item_id), None)
    if item_index is None:
        raise ItemNotFoundError(item_id)
    
    deleted_item = fake_items_db.pop(item_index)
    return SuccessResponse(
        message=f"Item '{deleted_item['title']}' deleted successfully",
        data={"deleted_item_id": item_id}
    )

@router.get("/categories/", response_model=List[str], summary="Get all categories")
async def get_categories():
    categories = list(set(item["category"] for item in fake_items_db))
    return sorted(categories)

@router.get("/user/{user_id}", response_model=List[Item], summary="Get items by user")
async def get_items_by_user(
    user_id: int = Path(..., gt=0, description="The ID of the user"),
    available_only: bool = Query(False, description="Show only available items")
):
    if user_id not in fake_users_db:
        raise UserNotFoundError(user_id)
    
    user_items = [item for item in fake_items_db if item["owner_id"] == user_id]
    
    if available_only:
        user_items = [item for item in user_items if item["is_available"]]
    
    return user_items

@router.patch("/{item_id}/availability", response_model=Item, summary="Toggle item availability")
async def toggle_item_availability(
    item_id: int = Path(..., gt=0, description="The ID of the item")
):
    item = next((item for item in fake_items_db if item["id"] == item_id), None)
    if not item:
        raise ItemNotFoundError(item_id)
    
    item["is_available"] = not item["is_available"]
    return item