from sqlalchemy.orm import Session
from typing import List, Optional

from app.models.user import User

class UserRepository:
    def get_user(self, db: Session, user_id: int) -> Optional[User]:
        """Get user by ID."""
        return db.query(User).filter(User.id == user_id).first()
    
    def get_user_by_username(self, db: Session, username: str) -> Optional[User]:
        """Get user by username."""
        return db.query(User).filter(User.username == username).first()
    
    def get_user_by_email(self, db: Session, email: str) -> Optional[User]:
        """Get user by email."""
        return db.query(User).filter(User.email == email).first()
    
    def get_users(self, db: Session, skip: int = 0, limit: int = 100) -> List[User]:
        """Get a list of users."""
        return db.query(User).offset(skip).limit(limit).all()
    
    def create_user(self, db: Session, username: str, email: str, hashed_password: str, is_admin: bool = False) -> User:
        """Create a new user."""
        db_user = User(
            username=username, 
            email=email, 
            hashed_password=hashed_password, 
            is_admin=is_admin
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    
    def update_user(self, db: Session, user_id: int, user_data: dict) -> Optional[User]:
        """Update user data."""
        db_user = self.get_user(db, user_id)
        if db_user:
            for key, value in user_data.items():
                if hasattr(db_user, key):
                    setattr(db_user, key, value)
            db.commit()
            db.refresh(db_user)
        return db_user
    
    def delete_user(self, db: Session, user_id: int) -> bool:
        """Delete a user."""
        db_user = self.get_user(db, user_id)
        if db_user:
            db.delete(db_user)
            db.commit()
            return True
        return False