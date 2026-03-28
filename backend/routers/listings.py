from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models.listing import Listing
from ..models.user import User
from ..schemas.listing import ListingCreate, ListingUpdate, ListingResponse
from ..utils.dependencies import get_current_user

router = APIRouter(prefix="/listings", tags=["Listings"])

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