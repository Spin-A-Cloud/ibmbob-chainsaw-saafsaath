from pydantic import BaseModel, EmailStr
from enum import Enum


class UserRole(str, Enum):
    customer = "customer"
    company = "company"


class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: UserRole
    name: str


class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str
    role: UserRole


class RegisterResponse(BaseModel):
    id: int
    name: str
    email: str
    role: UserRole
