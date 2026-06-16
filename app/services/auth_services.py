from sqlalchemy.orm import Session

from app import auth
from app import repository
from app import exceptions
from app.models import User
from app.schemas import TokenResponse

def register(db: Session, email: str, password: str) -> TokenResponse:
    if repository.user_get_by_email(db, email):
        raise exceptions.EmailAlreadyRegisteredError("A user with this email already exists.")

    user = User(email=email, hashed_password=auth.get_password_hash(password))
    repository.user_create(db, user)
    return TokenResponse(
        access_token=auth.get_token(user.user_id)
    )

def login(db: Session, email: str, password: str) -> TokenResponse:
    user = repository.user_get_by_email(db, email)
    if not user or not auth.verify_password(password, user.hashed_password):
        raise exceptions.InvalidCredentialsError("Invalid credentials.")

    return TokenResponse(
        access_token=auth.get_token(user.user_id)
    )