from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any, List

from app.database import get_db
from app.models.user import User
from app.services.auth_service import auth_service
from app.repositories.user_repository import UserRepository

# Create router
router = APIRouter()

# Create user repository
user_repository = UserRepository()

@router.get("/me")
async def get_current_user_info(
    current_user: User = Depends(auth_service.get_current_active_user)
) -> Dict[str, Any]:
    """Get current user information."""
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "is_active": current_user.is_active,
        "is_admin": current_user.is_admin
    }

@router.put("/me")
async def update_current_user(
    user_data: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_active_user)
) -> Dict[str, Any]:
    """Update current user information."""
    # Prevent changing username or admin status
    if 'username' in user_data:
        del user_data['username']
    if 'is_admin' in user_data:
        del user_data['is_admin']
    
    # Hash password if provided
    if 'password' in user_data:
        user_data['hashed_password'] = auth_service.get_password_hash(user_data['password'])
        del user_data['password']
    
    # Update user
    updated_user = user_repository.update_user(
        db=db, 
        user_id=current_user.id, 
        user_data=user_data
    )
    
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {
        "id": updated_user.id,
        "username": updated_user.username,
        "email": updated_user.email,
        "is_active": updated_user.is_active,
        "is_admin": updated_user.is_admin
    }

@router.get("/users", dependencies=[Depends(auth_service.get_current_active_user)])
async def get_users(
    skip: int = 0, 
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_active_user)
) -> List[Dict[str, Any]]:
    """Get a list of users (admin only)."""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )
    
    users = user_repository.get_users(db=db, skip=skip, limit=limit)
    
    result = []
    for user in users:
        result.append({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "is_active": user.is_active,
            "is_admin": user.is_admin
        })
    
    return result