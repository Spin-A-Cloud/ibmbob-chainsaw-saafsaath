from fastapi import APIRouter, HTTPException, status
from models.schemas import (
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    RegisterResponse,
    UserRole,
)
from db.store import get_user, create_user, verify_password
from core.security import create_access_token

router = APIRouter(tags=["auth"])


@router.post("/login", response_model=LoginResponse)
def login(body: LoginRequest):
    user = get_user(body.email)
    if not user or not verify_password(body.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    token = create_access_token({"sub": body.email, "role": user["role"]})
    return LoginResponse(
        access_token=token,
        role=user["role"],
        name=user["name"],
    )


@router.post("/register", response_model=RegisterResponse, status_code=201)
def register(body: RegisterRequest):
    try:
        user = create_user(body.name, body.email, body.password, body.role)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    return RegisterResponse(
        id=user["id"],
        name=user["name"],
        email=body.email,
        role=user["role"],
    )
