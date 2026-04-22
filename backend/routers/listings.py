from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models.listing import Listing
from ..models.user import User
from ..schemas.listing import ListingCreate, ListingUpdate, ListingResponse
from ..utils.dependencies import get_current_user
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
import httpx
import os
from ..config import settings

router = APIRouter(prefix="/listings", tags=["Listings"])
@router.post("/upload-image")
async def upload_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Validate file type
    if file.content_type not in ["image/jpeg", "image/png", "image/webp", "image/jpg"]:
        raise HTTPException(status_code=400, detail="Only JPEG, PNG and WebP images are allowed")
    
    # Validate file size (max 5MB)
    contents = await file.read()
    if len(contents) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Image must be less than 5MB")
    
    # Generate unique filename
    import uuid
    ext = file.filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    
    # Upload to Supabase Storage
    url = f"{settings.SUPABASE_URL}/storage/v1/object/Listing-images/{filename}"
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            url,
            content=contents,
            headers={
                "Authorization": f"Bearer {settings.SUPABASE_KEY}",
                "Content-Type": file.content_type
            }
        )

    if response.status_code not in [200, 201]:
        print(f"Supabase error: {response.status_code} - {response.text}")  # ← ADD THIS
        raise HTTPException(status_code=500, detail="Failed to upload image")
    
    
    
    # Return public URL
    public_url = f"{settings.SUPABASE_URL}/storage/v1/object/public/Listing-images/{filename}"
    return {"image_url": public_url}


@router.post("/", response_model=ListingResponse)
def create_listing(
    listing: ListingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in ["seller", "verified_seller", "admin"]:
        raise HTTPException(status_code=403, detail="Only sellers can create listings")
    
    new_listing = Listing(**listing.dict(), owner_id=current_user.id)
    db.add(new_listing)
    db.commit()
    db.refresh(new_listing)

    new_listing.owner_name = current_user.full_name
    new_listing.owner_role = current_user.role
    new_listing.owner_phone = current_user.phone_number
    return new_listing

@router.get("/", response_model=List[ListingResponse])
def get_all_listings(db: Session = Depends(get_db)):
    listings = db.query(Listing).filter(Listing.is_available == True).all()
    for listing in listings:
        owner = db.query(User).filter(User.id == listing.owner_id).first()
        if owner:
            listing.owner_name = owner.full_name
            listing.owner_role = owner.role
            listing.owner_phone = owner.phone_number
    return listings

@router.get("/{listing_id}", response_model=ListingResponse)
def get_listing(listing_id: int, db: Session = Depends(get_db)):
    listing = db.query(Listing).filter(Listing.id == listing_id).first()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    owner = db.query(User).filter(User.id == listing.owner_id).first()
    if owner:
        listing.owner_name = owner.full_name
        listing.owner_role = owner.role
        listing.owner_phone = owner.phone_number
    return listing

@router.put("/{listing_id}", response_model=ListingResponse)
def update_listing(
    listing_id: int,
    listing_update: ListingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    listing = db.query(Listing).filter(Listing.id == listing_id).first()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    if listing.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this listing")
    
    for key, value in listing_update.dict(exclude_unset=True).items():
        setattr(listing, key, value)
    
    db.commit()
    db.refresh(listing)

    listing.owner_name = current_user.full_name
    listing.owner_role = current_user.role
    return listing

@router.delete("/{listing_id}")
def delete_listing(
    listing_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    listing = db.query(Listing).filter(Listing.id == listing_id).first()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    if listing.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to delete this listing")
    
    # Delete related records first
    from ..models.payment import Payment
    from ..models.review import Review
    db.query(Payment).filter(Payment.listing_id == listing_id).delete()
    db.query(Review).filter(Review.listing_id == listing_id).delete()
    db.delete(listing)
    db.commit()
    return {"message": "Listing deleted successfully"}