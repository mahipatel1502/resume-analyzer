import hashlib
import secrets
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import HTTPException, status

from app.core.config import ACCESS_TOKEN_EXPIRE_MINUTES, JWT_ALGORITHM, JWT_SECRET_KEY
from app.models.auth import AuthResponse, LoginRequest, SignupRequest, UserResponse
from app.repositories.auth_repository import AuthRepository


class AuthService:
    PASSWORD_HASH_ITERATIONS = 210_000

    def __init__(self) -> None:
        self.auth_repository = AuthRepository()

    def signup(self, request: SignupRequest) -> AuthResponse:
        existing_user = self.auth_repository.get_user_by_email(request.email)
        if existing_user is not None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="An account with this email already exists.")

        password_hash = self._hash_password(request.password)
        user_record = self.auth_repository.create_user(
            full_name=request.full_name or "",
            email=request.email,
            password_hash=password_hash,
        )
        token = self._create_access_token(user_record)
        return self._build_auth_response(token, user_record)

    def login(self, request: LoginRequest) -> AuthResponse:
        user_record = self.auth_repository.get_user_by_email(request.email)
        if user_record is None or not self._verify_password(request.password, str(user_record["password_hash"])):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password.")

        token = self._create_access_token(user_record)
        return self._build_auth_response(token, user_record)

    def decode_token(self, token: str) -> dict[str, object]:
        try:
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        except jwt.InvalidTokenError as exc:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials.") from exc

        if payload.get("token_type") != "access":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials.")

        return payload

    def _build_auth_response(self, token: str, user_record: dict[str, object]) -> AuthResponse:
        return AuthResponse(
            access_token=token,
            user=UserResponse(
                id=int(user_record["id"]),
                full_name=str(user_record.get("full_name", "") or ""),
                email=str(user_record["email"]),
                created_at=str(user_record["created_at"]),
            ),
        )

    def _create_access_token(self, user_record: dict[str, object]) -> str:
        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        payload = {
            "sub": str(user_record["id"]),
            "email": str(user_record["email"]),
            "full_name": str(user_record.get("full_name", "") or ""),
            "iat": int(now.timestamp()),
            "exp": int(expires_at.timestamp()),
            "token_type": "access",
        }
        return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

    def _hash_password(self, password: str) -> str:
        salt = secrets.token_bytes(16)
        derived_key = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            self.PASSWORD_HASH_ITERATIONS,
        )
        return f"{self.PASSWORD_HASH_ITERATIONS}${salt.hex()}${derived_key.hex()}"

    def _verify_password(self, password: str, stored_hash: str) -> bool:
        try:
            iterations_str, salt_hex, derived_key_hex = stored_hash.split("$", 2)
            iterations = int(iterations_str)
            salt = bytes.fromhex(salt_hex)
            expected_key = bytes.fromhex(derived_key_hex)
        except (ValueError, TypeError):
            return False

        candidate_key = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            iterations,
        )
        return secrets.compare_digest(candidate_key, expected_key)