from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import uuid
from ..database import get_db
from ..models.payment import Payment
from ..models.listing import Listing
from ..schemas.payment import PaymentCreate, PaymentResponse
from ..utils.dependencies import get_current_user, get_admin_user
from ..models.user import User

router = APIRouter(prefix="/payments", tags=["Payments"])

@router.post("/", response_model=PaymentResponse)
def initiate_payment(
    payment: PaymentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    listing = db.query(Listing).filter(Listing.id == payment.listing_id).first()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    if listing.owner_id == current_user.id:
        raise HTTPException(status_code=400, detail="You cannot pay for your own listing")
    if not listing.is_available:
        raise HTTPException(status_code=400, detail="Listing is no longer available")

    reference = str(uuid.uuid4())

    new_payment = Payment(
        amount=listing.price,
        status="completed",
        reference=reference,
        listing_id=listing.id,
        buyer_id=current_user.id,
        seller_id=listing.owner_id
    )
    db.add(new_payment)
    db.commit()
    db.refresh(new_payment)

    # Send notification to seller
    from ..models.notification import Notification
    notification = Notification(
        message=f"{current_user.full_name} just paid for your listing: {listing.title} — ₦{listing.price:,.0f}",
        notification_type="payment",
        user_id=listing.owner_id
    )
    db.add(notification)
    db.commit()

    return new_payment
):
    listing = db.query(Listing).filter(Listing.id == payment.listing_id).first()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    if listing.owner_id == current_user.id:
        raise HTTPException(status_code=400, detail="You cannot pay for your own listing")
    if not listing.is_available:
        raise HTTPException(status_code=400, detail="Listing is no longer available")

    reference = str(uuid.uuid4())

    new_payment = Payment(
        amount=listing.price,
        status="completed",  # Simulated - auto complete
        reference=reference,
        listing_id=listing.id,
        buyer_id=current_user.id,
        seller_id=listing.owner_id
    )
    db.add(new_payment)
    db.commit()
    db.refresh(new_payment)
    return new_payment

@router.get("/my-payments", response_model=List[PaymentResponse])
def get_my_payments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(Payment).filter(Payment.buyer_id == current_user.id).all()

@router.get("/my-earnings", response_model=List[PaymentResponse])
def get_my_earnings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(Payment).filter(Payment.seller_id == current_user.id).all()

@router.get("/", response_model=List[PaymentResponse])
def get_all_payments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    return db.query(Payment).all()

@router.get("/{payment_id}", response_model=PaymentResponse)
def get_payment(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    if payment.buyer_id != current_user.id and payment.seller_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to view this payment")
    return payment