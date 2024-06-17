from sqlalchemy.orm import Session
from database.models import User
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from schemas import UserCreate
async def create_user(body: UserCreate, db: Session):
    pass

async def get_user_by_email(email: str, db: Session):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

async def confirmed_email(email: str, db: Session):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.confirmed = True
    db.commit()

async def update_avatar(email, url: str, db: Session) -> User:
    user = await get_user_by_email(email, db)
    user.avatar = url
    db.commit()
    return user