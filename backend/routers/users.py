from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.user import User
from ..schemas.user import UserResponse
from ..schemas.profile import ProfileUpdate, RoleUpdate
from ..utils.dependencies import get_current_user, get_admin_user

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/me", response_model=UserResponse)
def get_my_profile(current_user: User = Depends(get_current_user)):
    return current_user

@router.put("/me", response_model=UserResponse)
def update_my_profile(
    profile: ProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if profile.full_name:
        current_user.full_name = profile.full_name
    if profile.email:
        current_user.email = profile.email
    if profile.matric_number:
        current_user.matric_number = profile.matric_number
    if profile.phone_number is not None:
        current_user.phone_number = profile.phone_number
    
    db.commit()
    db.refresh(current_user)
    return current_user

@router.put("/me/become-seller", response_model=UserResponse)
def become_seller(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "user":
        raise HTTPException(status_code=400, detail="You are already a seller or higher")
    
    current_user.role = "seller"
    db.commit()
    db.refresh(current_user)
    return current_user

@router.get("/", response_model=list[UserResponse])
def get_all_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    return db.query(User).all()

@router.put("/{user_id}/role", response_model=UserResponse)
def update_user_role(
    user_id: int,
    role: RoleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.role = role.role
    db.commit()
    db.refresh(user)
    return user
    
@router.get("/search", response_model=list[UserResponse])
def search_users(
    q: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    users = db.query(User).filter(
        User.full_name.ilike(f"%{q}%"),
        User.id != current_user.id
    ).limit(10).all()
    return users