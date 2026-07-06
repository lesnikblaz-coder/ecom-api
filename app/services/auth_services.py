from sqlalchemy.orm import Session

from app import auth
from app.repositories import user_repository
from app import exceptions
from app.models import User
from app.schemas import TokenResponse
from app.logging_config import logger

def register(db: Session, email: str, password: str) -> TokenResponse:
    if user_repository.user_get_by_email(db, email):
        raise exceptions.EmailAlreadyRegisteredError("A user with this email already exists.")

    user = User(email=email, hashed_password=auth.get_password_hash(password))
    user_repository.user_create(db, user)

    logger.info("New user registered (id=%s)", user.user_id)

    return TokenResponse(
        access_token=auth.get_token(user.user_id)
    )

def login(db: Session, email: str, password: str) -> TokenResponse:
    user = user_repository.user_get_by_email(db, email)

    if not user or not auth.verify_password(password, user.hashed_password):
        logger.warning("Invalid login attempt for email=%s", email)
        raise exceptions.InvalidCredentialsError("Invalid credentials.")

    logger.info("User %s logged in successfully.", user.user_id)

    return TokenResponse(
        access_token=auth.get_token(user.user_id)
    )