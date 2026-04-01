from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from ..database import get_db
from ..models.user import User
from ..models.listing import Listing
from ..models.payment import Payment
from ..models.review import Review
from ..models.job import Job
from ..models.message import Message
from ..schemas.user import UserResponse
from ..schemas.listing import ListingResponse
from ..schemas.payment import PaymentResponse
from ..utils.dependencies import get_admin_user

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.get("/overview")
def get_admin_overview(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    total_users = db.query(User).count()
    total_sellers = db.query(User).filter(User.role == "seller").count()
    total_verified_sellers = db.query(User).filter(User.role == "verified_seller").count()
    total_listings = db.query(Listing).count()
    total_jobs = db.query(Job).count()
    total_payments = db.query(Payment).count()
    total_reviews = db.query(Review).count()
    total_messages = db.query(Message).count()
    total_revenue = db.query(func.sum(Payment.amount)).filter(
        Payment.status == "completed"
    ).scalar() or 0

    return {
        "total_users": total_users,
        "total_sellers": total_sellers,
        "total_verified_sellers": total_verified_sellers,
        "total_listings": total_listings,
        "total_jobs": total_jobs,
        "total_payments": total_payments,
        "total_reviews": total_reviews,
        "total_messages": total_messages,
        "total_revenue": total_revenue
    }

@router.get("/users", response_model=List[UserResponse])
def get_all_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    return db.query(User).all()

@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}

@router.get("/listings", response_model=List[ListingResponse])
def get_all_listings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    return db.query(Listing).all()

@router.delete("/listings/{listing_id}")
def delete_listing(
    listing_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    listing = db.query(Listing).filter(Listing.id == listing_id).first()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    db.delete(listing)
    db.commit()
    return {"message": "Listing deleted successfully"}

@router.put("/users/{user_id}/verify-seller")
def verify_seller(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.role != "seller":
        raise HTTPException(status_code=400, detail="User is not a seller")
    user.role = "verified_seller"
    db.commit()
    db.refresh(user)
    return {"message": f"{user.full_name} is now a verified seller"}

@router.get("/payments", response_model=List[PaymentResponse])
def get_all_payments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    return db.query(Payment).all()

@router.get("/all-jobs")
def get_all_jobs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    from ..models.job import Job
    jobs = db.query(Job).all()
    result = []
    for job in jobs:
        owner = db.query(User).filter(User.id == job.owner_id).first()
        result.append({
            "id": job.id,
            "title": job.title,
            "category": job.category,
            "budget": job.budget,
            "owner_id": job.owner_id,
            "owner_name": owner.full_name if owner else None,
            "is_open": job.is_open,
            "created_at": str(job.created_at)
        })
    return result