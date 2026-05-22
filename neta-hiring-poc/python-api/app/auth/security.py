from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import get_settings


password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return password_context.hash(password)


def create_access_token(subject: str, claims: dict | None = None) -> str:
    settings = get_settings()
    if not settings.jwt_secret_key:
        raise RuntimeError("JWT_SECRET_KEY is not configured.")

    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(minutes=settings.jwt_expires_minutes)

    payload = {
        "sub": subject,
        "iat": int(now.timestamp()),
        "exp": expires_at,
    }
    if settings.jwt_issuer:
        payload["iss"] = settings.jwt_issuer
    if settings.jwt_audience:
        payload["aud"] = settings.jwt_audience
    if claims:
        payload.update(claims)

    return jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )


def decode_access_token(token: str) -> dict:
    settings = get_settings()
    if not settings.jwt_secret_key:
        raise JWTError("JWT_SECRET_KEY is not configured.")

    options = {
        "verify_aud": bool(settings.jwt_audience),
        "verify_iss": bool(settings.jwt_issuer),
    }
    kwargs = {
        "key": settings.jwt_secret_key,
        "algorithms": [settings.jwt_algorithm],
        "options": options,
    }
    if settings.jwt_audience:
        kwargs["audience"] = settings.jwt_audience
    if settings.jwt_issuer:
        kwargs["issuer"] = settings.jwt_issuer

    try:
        return jwt.decode(token, **kwargs)
    except JWTError:
        raise
