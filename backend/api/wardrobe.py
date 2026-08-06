import uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile
from sqlalchemy.orm import Session
from database import get_db
from models.models import ClothingCategory, ClothingItem
from schemas.schemas import ClothingItemOut
from services import storage
 
router = APIRouter(prefix="/wardrobe", tags=["wardrobe"])

@router.get("/", response_model=list[ClothingItemOut])
def list_clothing_items(owner_id: uuid.UUID, db: Session = Depends(get_db)):
    items = db.query(ClothingItem).filter(ClothingItem.owner_id == owner_id).all()
    return items

@router.get("/{item_id}", response_model=ClothingItemOut)
def get_clothing_item(item_id: uuid.UUID, db: Session = Depends(get_db)):
    item = db.query(ClothingItem).filter(ClothingItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Clothing item not found")
    return item

@router.get("/{item_id}/image-url")
def get_clothing_item_image_url(item_id: uuid.UUID, db: Session = Depends(get_db)):
    item = db.query(ClothingItem).filter(ClothingItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Clothing item not found")

    original_url = storage.get_presigned_url(item.original_image_path)
    segmented_url = (
        storage.get_presigned_url(item.segmented_image_path)
        if segmented_image_path else None 
    )
    return {"original_url": original_url, "segmented_url": segmented_url}

@router.post("/", response_model=ClothingItemOut)
async def create_clothing_item(
    owner_id: uuid.UUID,
    name: str,
    category: ClothingCategory,
    file: UploadFile,
    color: str | None = None,
    description: str | None = None,
    db: Session = Depends(get_db),
):
    object_key = storage.upload_file(file, folder="clothing")
 
    item = ClothingItem(
        owner_id=owner_id,
        name=name,
        category=category,
        color=color,
        description=description,
        original_image_path=object_key,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item
 
@router.delete("/{item_id}")
def delete_clothing_item(item_id: uuid.UUID, db: Session = Depends(get_db)):
    item = db.query(ClothingItem).filter(ClothingItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Clothing item not found")

    storage.delete_file(item.original_image_path)
    if item.segmented_image_path:
        storage.delete_file(item.segmented_image_path)

    db.delete(item)
    db.commit()
    return {"detail": "Deleted"}