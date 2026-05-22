from sqlalchemy.orm import Session

from app.auth.security import create_access_token, get_password_hash, verify_password
from app.core.config import get_settings
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import AuthResponse
from app.schemas.user import UserCreate
from app.services.exceptions import DuplicateUserError


class AuthService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.user_repository = UserRepository(db)

    def register_user(self, user_in: UserCreate) -> User:
        email = str(user_in.email).strip().lower()
        if self.user_repository.get_by_email(email) is not None:
            raise DuplicateUserError("Ya existe un usuario con ese email.")

        user = User(
            full_name=user_in.full_name.strip(),
            email=email,
            hashed_password=get_password_hash(user_in.password),
            role="User",
            is_active=True,
        )
        self.user_repository.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def authenticate_user(self, email: str, password: str) -> User | None:
        user = self.user_repository.get_by_email(email)
        if user is None or not user.is_active:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    def create_login_token(self, user: User) -> AuthResponse:
        settings = get_settings()
        access_token = create_access_token(
            subject=str(user.id),
            claims={
                "email": user.email,
                "name": user.full_name,
                "role": user.role,
            },
        )
        return AuthResponse(
            access_token=access_token,
            expires_in_minutes=settings.jwt_expires_minutes,
        )
