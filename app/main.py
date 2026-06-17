from fastapi import FastAPI, Depends
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from sqlalchemy.orm import Session
from collections.abc import Sequence

from app.database import get_db
from app.exception_handlers import register_exception_handlers
from app import schemas
from app.services import auth_services, user_services
from app.models import User

app = FastAPI()
register_exception_handlers(app)

db_session = Annotated[Session, Depends(get_db)]

# AUTH
@app.post("/auth/register", response_model=schemas.TokenResponse)
def register(request: schemas.UserLoginRegister, db: db_session) -> schemas.TokenResponse:
    return auth_services.register(db, request.email, request.password)

@app.post("/auth/login", response_model=schemas.TokenResponse)
def login(request: schemas.UserLoginRegister, db: db_session) -> schemas.TokenResponse:
    return auth_services.login(db, request.email, request.password)

@app.post("/auth/token", response_model=schemas.TokenResponse)
def token(db: db_session, form_data: OAuth2PasswordRequestForm = Depends()) -> schemas.TokenResponse:
    return auth_services.login(db, form_data.username, form_data.password)

# USERS
@app.get("/users", response_model=list[schemas.UserResponse])
def users_get(db: db_session) -> Sequence[User]:
    return user_services.users_get(db)

@app.get("/users/{user_id}", response_model=schemas.UserResponse)
def user_get(user_id: int, db: db_session) -> User:
    return user_services.user_get(db, user_id)

@app.put("/users/{user_id}", response_model=schemas.UserResponse)
def user_update(user_id: int, data: schemas.UserUpdate, db: db_session) -> User:
    return user_services.user_update(db, user_id, data)

@app.delete("/users/{user_id}", status_code=204)
def user_delete(user_id: int, db: db_session) -> User:
    return user_services.user_delete(db, user_id)