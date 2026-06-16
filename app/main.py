from fastapi import FastAPI, Depends
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from sqlalchemy.orm import Session

from app.database import get_db
from app.exception_handlers import register_exception_handlers
from app import schemas
from app.services import auth_services

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