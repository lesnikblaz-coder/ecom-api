import os

from dotenv import load_dotenv
from pwdlib import PasswordHash
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timezone, timedelta
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from app import exceptions
from app import enums

from app.database import get_db
from app.repositories import user_repository
from app.models import User
from app.logging_config import logger

load_dotenv(".env")

secret_key = os.getenv("SECRET_KEY")
if not secret_key:
    raise RuntimeError("Secret key not found")

SECRET_KEY = secret_key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 20

pwd_hash = PasswordHash.recommended()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

def get_password_hash(password: str) -> str:
    return pwd_hash.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_hash.verify(plain_password, hashed_password)

def get_token(user_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": str(user_id), "exp": expire}
    return jwt.encode(payload, SECRET_KEY, ALGORITHM)

def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    try:
        decoded_payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(decoded_payload["sub"])
    except(JWTError, KeyError):
        raise exceptions.InvalidTokenError("Invalid token.")

    user = user_repository.user_get_by_id(db, user_id)
    if not user:
        raise exceptions.UserNotFoundError("User not found.")
    return user

def required_roles(*roles):
    def checker(current_user: User = Depends(get_current_user)):
        if current_user.role not in roles:
            logger.info("User %s attempted to access endpoint without sufficient permissions.", current_user.user_id)
            raise exceptions.InsufficientPermissions("Insufficient permissions.")
        return current_user
    return checker

require_admin = required_roles(
    enums.UserRole.ADMIN
)

require_staff = required_roles(
    enums.UserRole.ADMIN,
    enums.UserRole.STAFF
)