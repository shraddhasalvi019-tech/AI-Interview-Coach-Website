from datetime import datetime
from pydantic import BaseModel, EmailStr, Field

class UserRegister(BaseModel):
    name: str = Field(..., min_length=2, example="Demo Candidate")
    email: EmailStr = Field(..., example="candidate@example.com")
    password: str = Field(..., min_length=6, example="password123")

class UserLogin(BaseModel):
    email: EmailStr = Field(..., example="candidate@example.com")
    password: str = Field(..., example="password123")

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    user_name: str
    email: str

class UserOut(BaseModel):
    id: int
    name: str
    email: str
    created_at: datetime

    class Config:
        from_attributes = True
