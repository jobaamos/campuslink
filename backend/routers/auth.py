from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.user import User
from ..schemas.user import UserCreate, UserLogin, UserResponse, Token
from ..utils.hashing import hash_password, verify_password
from ..utils.jwt import create_access_token
from ..utils.email import generate_verification_token, verify_token, send_verification_email, send_password_reset_email

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    # Check if email already exists
    existing_email = db.query(User).filter(User.email == user.email).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Check if matric number already exists
    existing_matric = db.query(User).filter(User.matric_number == user.matric_number).first()
    if existing_matric:
        raise HTTPException(status_code=400, detail="Matric number already registered")
    
    # Generate verification token
    token = generate_verification_token(user.email)

    # Create new user
    new_user = User(
        full_name=user.full_name,
        email=user.email,
        matric_number=user.matric_number,
        password=hash_password(user.password),
        is_verified=False,
        verification_token=token
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Send verification email
    send_verification_email(user.email, token)

    return new_user

@router.get("/verify/{token}")
def verify_email(token: str, db: Session = Depends(get_db)):
    email = verify_token(token)
    if not email:
        raise HTTPException(status_code=400, detail="Invalid or expired verification link")
    
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.is_verified:
        return {"message": "Email already verified. Please login."}
    
    user.is_verified = True
    user.verification_token = None
    db.commit()
    return {"message": "Email verified successfully! You can now login."}

@router.post("/login", response_model=Token)
def login(user: UserLogin, db: Session = Depends(get_db)):
    # Check if user exists
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Check password
    if not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Check if verified
    if not db_user.is_verified:
        raise HTTPException(status_code=401, detail="Please verify your email before logging in. Check your inbox for the verification link.")
    
    # Create token
    access_token = create_access_token(data={"sub": db_user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/forgot-password")
def forgot_password(email: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        # Return success even if email not found for security reasons
        return {"message": "If this email is registered, a reset link has been sent."}
    
    token = generate_verification_token(email)
    user.verification_token = token
    db.commit()

    send_password_reset_email(email, token)
    return {"message": "If this email is registered, a reset link has been sent."}

@router.post("/reset-password")
def reset_password(token: str, new_password: str, db: Session = Depends(get_db)):
    email = verify_token(token)
    if not email:
        raise HTTPException(status_code=400, detail="Invalid or expired reset link")
    
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.password = hash_password(new_password)
    user.verification_token = None
    db.commit()
    return {"message": "Password reset successfully! You can now login."}