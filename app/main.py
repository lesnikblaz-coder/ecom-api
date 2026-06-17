from fastapi import FastAPI, Depends
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from sqlalchemy.orm import Session
from collections.abc import Sequence

from app import schemas
from app import auth
from app import models

from app.database import get_db
from app.exception_handlers import register_exception_handlers
from app.services import auth_services, user_services, category_services

app = FastAPI()
register_exception_handlers(app)

db_session = Annotated[Session, Depends(get_db)]

# USER AUTH
@app.post("/auth/register", response_model=schemas.TokenResponse)
def register(request: schemas.UserLoginRegister, db: db_session) -> schemas.TokenResponse:
    return auth_services.register(db, request.email, request.password)

@app.post("/auth/login", response_model=schemas.TokenResponse)
def login(request: schemas.UserLoginRegister, db: db_session) -> schemas.TokenResponse:
    return auth_services.login(db, request.email, request.password)

@app.post("/auth/token", response_model=schemas.TokenResponse)
def token(db: db_session, form_data: OAuth2PasswordRequestForm=Depends()) -> schemas.TokenResponse:
    return auth_services.login(db, form_data.username, form_data.password)

# USERS (admin+)
@app.get("/users", response_model=list[schemas.UserResponse])
def users_get(db: db_session, _: models.User=Depends(auth.require_admin)) -> Sequence[models.User]:
    return user_services.users_get(db)

@app.get("/users/{user_id}", response_model=schemas.UserResponse)
def user_get(user_id: int, db: db_session, _: models.User=Depends(auth.require_admin)) -> models.User:
    return user_services.user_get(db, user_id)

@app.put("/users/{user_id}", response_model=schemas.UserResponse)
def user_update(user_id: int, data: schemas.UserUpdate, db: db_session, _: models.User=Depends(auth.require_admin)) -> models.User:
    return user_services.user_update(db, user_id, data)

@app.delete("/users/{user_id}", status_code=204)
def user_delete(user_id: int, db: db_session, _: models.User=Depends(auth.require_admin)) -> None:
    user_services.user_delete(db, user_id)


# CATEGORIES (staff+)
@app.get("/categories", response_model=list[schemas.CategoryResponse])
def categories_get(db: db_session, _: models.User=Depends(auth.require_staff)) -> Sequence[models.Category]:
    return category_services.categories_get(db)

@app.get("/categories/{category_id}", response_model=schemas.CategoryResponse)
def category_get(category_id: int, db: db_session, _: models.User=Depends(auth.require_staff)) -> models.Category:
    return category_services.category_get(db, category_id)

@app.put("/categories/{category_id}", response_model=schemas.CategoryResponse)
def category_update(category_id: int, db: db_session, data: schemas.CategoryUpdate, _: models.User=Depends(auth.require_staff)) -> models.Category:
    return category_services.category_update(db, category_id, data)

@app.delete("/categories/{category_id}", status_code=204)
def category_delete(category_id: int, db: db_session, _: models.User=Depends(auth.require_staff)) -> None:
    category_services.category_delete(db, category_id)