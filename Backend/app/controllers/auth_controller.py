from fastapi import APIRouter

from app.models.auth import AuthResponse, LoginRequest, SignupRequest
from app.services.auth_service import AuthService


router = APIRouter(prefix="/auth", tags=["Auth"])
auth_service = AuthService()


@router.post("/signup", response_model=AuthResponse)
def signup(request: SignupRequest) -> AuthResponse:
    return auth_service.signup(request)


@router.post("/login", response_model=AuthResponse)
def login(request: LoginRequest) -> AuthResponse:
    return auth_service.login(request)