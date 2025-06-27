from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate
from app.utils.security import hash_password, verify_password, create_access_token

def create_user(user_data: UserCreate, db: Session):
    hashed_pw = hash_password(user_data.password)
    user = User(
        email=user_data.email,
        username=user_data.username,
        password_hash=hashed_pw,
        full_name=user_data.full_name
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def authenticate_user(username: str, password: str, db: Session):
    user = db.query(User).filter(User.username == username).first()
    if user and verify_password(password, user.password_hash):
        return user
    return None

def generate_token(user_id: int):
    return create_access_token({"sub": str(user_id)})
