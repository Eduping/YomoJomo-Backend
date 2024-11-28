from sqlalchemy.orm import Session
from schemas import UserCreate
from models import User as UserModel

def create_user(db: Session, user: UserCreate):
    db_user = UserModel(username=user.username, password=user.password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user