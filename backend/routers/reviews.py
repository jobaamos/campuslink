from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models.review import Review
from ..models.listing import Listing
from ..schemas.review import ReviewCreate, ReviewResponse
from ..utils.dependencies import get_current_user
from ..models.user import User

router = APIRouter(prefix="/reviews", tags=["Reviews"])

@router.post("/{listing_id}", response_model=ReviewResponse)
def create_review(
    listing_id: int,
    review: ReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    listing = db.query(Listing).filter(Listing.id == listing_id).first()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    if listing.owner_id == current_user.id:
        raise HTTPException(status_code=400, detail="You cannot review your own listing")
    
    existing_review = db.query(Review).filter(
        Review.listing_id == listing_id,
        Review.reviewer_id == current_user.id
    ).first()
    if existing_review:
        raise HTTPException(status_code=400, detail="You have already reviewed this listing")
    
    new_review = Review(
        rating=review.rating,
        comment=review.comment,
        listing_id=listing_id,
        reviewer_id=current_user.id
    )
    db.add(new_review)
    db.commit()
    db.refresh(new_review)

    # Send notification to listing owner
    from ..models.notification import Notification
    notification = Notification(
        message=f"{current_user.full_name} left a {review.rating}⭐ review on your listing: {listing.title}",
        notification_type="review",
        user_id=listing.owner_id
    )
    db.add(notification)
    db.commit()

    return new_review
    listing = db.query(Listing).filter(Listing.id == listing_id).first()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    if listing.owner_id == current_user.id:
        raise HTTPException(status_code=400, detail="You cannot review your own listing")
    
    existing_review = db.query(Review).filter(
        Review.listing_id == listing_id,
        Review.reviewer_id == current_user.id
    ).first()
    if existing_review:
        raise HTTPException(status_code=400, detail="You have already reviewed this listing")
    
    new_review = Review(
        rating=review.rating,
        comment=review.comment,
        listing_id=listing_id,
        reviewer_id=current_user.id
    )
    db.add(new_review)
    db.commit()
    db.refresh(new_review)
    return new_review

@router.get("/{listing_id}", response_model=List[ReviewResponse])
def get_listing_reviews(listing_id: int, db: Session = Depends(get_db)):
    listing = db.query(Listing).filter(Listing.id == listing_id).first()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    return db.query(Review).filter(Review.listing_id == listing_id).all()

@router.delete("/{review_id}")
def delete_review(
    review_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    if review.reviewer_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to delete this review")
    
    db.delete(review)
    db.commit()
    return {"message": "Review deleted successfully"}