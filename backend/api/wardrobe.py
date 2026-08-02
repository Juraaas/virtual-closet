import uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import ClothingCategory, ClothingItem
from app.schemas.schemas import ClothingItemOut
 
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
    # TODO: replace with actual upload to S3/MinIO via services/storage.py
    # and trigger background segmentation via services/segmentation.py
    original_image_path = f"placeholder/{file.filename}"
 
    item = ClothingItem(
        owner_id=owner_id,
        name=name,
        category=category,
        color=color,
        description=description,
        original_image_path=original_image_path,
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
    db.delete(item)
    db.commit()
    return {"detail": "Deleted"}