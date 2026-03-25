from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..database import get_db
from ..models.listing import Listing
from ..models.payment import Payment
from ..models.review import Review
from ..utils.dependencies import get_current_user
from ..models.user import User

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("/dashboard")
def get_seller_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Total listings
    total_listings = db.query(Listing).filter(
        Listing.owner_id == current_user.id
    ).count()

    # Active listings
    active_listings = db.query(Listing).filter(
        Listing.owner_id == current_user.id,
        Listing.is_available == True
    ).count()

    # Total payments received
    total_payments = db.query(Payment).filter(
        Payment.seller_id == current_user.id
    ).count()

    # Total earnings
    total_earnings = db.query(func.sum(Payment.amount)).filter(
        Payment.seller_id == current_user.id,
        Payment.status == "completed"
    ).scalar() or 0

    # Total reviews received
    listing_ids = [l.id for l in db.query(Listing).filter(
        Listing.owner_id == current_user.id
    ).all()]

    total_reviews = db.query(Review).filter(
        Review.listing_id.in_(listing_ids)
    ).count()

    # Average rating
    avg_rating = db.query(func.avg(Review.rating)).filter(
        Review.listing_id.in_(listing_ids)
    ).scalar()

    avg_rating = round(float(avg_rating), 2) if avg_rating else 0.0

    return {
        "seller": current_user.full_name,
        "role": current_user.role,
        "total_listings": total_listings,
        "active_listings": active_listings,
        "total_payments_received": total_payments,
        "total_earnings": total_earnings,
        "total_reviews": total_reviews,
        "average_rating": avg_rating
    }