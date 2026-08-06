import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr
from models.models import ClothingCategory

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: EmailStr
    silhouette_image_path: str | None = None
    silhouette_processed_path: str | None = None
    silhouette_keypoints: dict | None = None
    created_at: datetime

class ClothingItemCreate(BaseModel):
    name: str
    category: ClothingCategory
    color: str | None = None
    description: str | None = None

class ClothingItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    category: ClothingCategory
    color: str | None
    description: str | None
    original_image_path: str
    segmented_image_path: str | None
    created_at: datetime

class OutfitCreate(BaseModel):
    name: str
    clothing_item_ids: list[uuid.UUID]

class OutfitOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    items: list[ClothingItemOut]
    created_at: datetime

class UserCreateSimple(BaseModel):
    email: EmailStr