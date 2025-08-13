from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..core.auth import AuthService, get_current_user
from ..core.schemas import UserCreate, UserLogin, Token, UserResponse, APIResponse
from ..models import User

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=Token)
async def register(request: Request, user_data: UserCreate, db: Session = Depends(get_db)):
    import logging
    logger = logging.getLogger(__name__)
    
    logger.info(f"Register request from: {request.client.host}")
    logger.info(f"Headers: {dict(request.headers)}")
    logger.info(f"Register attempt: username={user_data.username}, password_len={len(user_data.password)}")
    
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        logger.warning(f"Registration failed: username {user_data.username} already exists")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    hashed_password = AuthService.get_password_hash(user_data.password)
    user = User(
        username=user_data.username,
        hashed_password=hashed_password,
        balance=10000.0
    )
    
    db.add(user)
    db.commit()
    
    access_token = AuthService.create_access_token(data={"sub": user.username})
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login", response_model=Token)
async def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    import logging
    logger = logging.getLogger(__name__)
    
    logger.info(f"Login request from: {request.client.host}")
    logger.info(f"Headers: {dict(request.headers)}")
    logger.info(f"Login attempt: username={form_data.username}, password_len={len(form_data.password)}")
    
    user = AuthService.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        logger.warning(f"Login failed: incorrect credentials for {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    access_token = AuthService.create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    return current_user

@router.post("/refresh", response_model=Token)
async def refresh_token(current_user: User = Depends(get_current_user)):
    access_token = AuthService.create_access_token(data={"sub": current_user.username})
    return {"access_token": access_token, "token_type": "bearer"}
