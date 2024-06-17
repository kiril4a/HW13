from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, File, UploadFile, Form
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from datetime import datetime, timedelta
from database.db import get_db
from database.models import User
from schemas import UserCreate, UserLogin, User as UserSchema, AvatarUploadRequest
from auth.utils import hash_password, verify_password, create_email_token, verify_email_token
from config import settings
from fastapi_limiter.depends import RateLimiter
from repository.users import create_user, get_user_by_email, confirmed_email, update_avatar
from services.email import send_email
from schemas import UserCreate
from routes.contacts import get_current_user
router = APIRouter()

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict, expires_delta: timedelta) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@router.post("/register/", response_model=UserSchema, dependencies=[Depends(RateLimiter(times=10, seconds=60))])
def register_user(
    user: UserCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = hash_password(user.password)
    db_user = User(username=user.username, email=user.email, password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    # Відправка листа для підтвердження
    background_tasks.add_task(send_confirmation_email, db_user.email, db_user.username)
    
    return db_user

async def send_confirmation_email(email: str, username: str):
    host = settings.APP_HOST
    token = create_email_token({"sub": email})
    confirmation_url = f"{host}/auth/confirm_email/{token}"
    await send_email(email, username, confirmation_url)

@router.get('/confirm_email/{token}')
async def confirm_email(token: str, db: Session = Depends(get_db)):
    email = verify_email_token(token)
    if not email:
        raise HTTPException(status_code=400, detail="Invalid token")
    
    await confirmed_email(email, db)
    return {"message": "Email confirmed"}

@router.post("/login/", dependencies=[Depends(RateLimiter(times=10, seconds=60))])
def login_user(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": db_user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}