from pydantic import BaseModel, EmailStr, Field, ConfigDict

from app.enums import UserRole

class UserLoginRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: int
    email: EmailStr
    is_active: bool
    role: UserRole

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"