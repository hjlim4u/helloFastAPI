from pydantic import BaseModel, EmailStr, Field

class UserCreate(BaseModel):
    fullname: str = Field(min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"