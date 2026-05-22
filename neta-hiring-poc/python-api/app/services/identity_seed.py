import logging

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.auth.security import get_password_hash
from app.core.config import get_settings
from app.models.user import User
from app.repositories.user_repository import UserRepository


logger = logging.getLogger(__name__)


def seed_admin_user(db: Session) -> None:
    settings = get_settings()
    repository = UserRepository(db)

    existing_user = repository.get_by_email(settings.admin_email)
    if existing_user is not None:
        return

    admin = User(
        email=settings.admin_email.lower(),
        full_name=settings.admin_full_name,
        hashed_password=get_password_hash(settings.admin_password),
        role="Admin",
        is_active=True,
    )
    repository.add(admin)

    try:
        db.commit()
        logger.info(
            "admin_user_seeded",
            extra={"_structured": {"email": admin.email, "role": admin.role}},
        )
    except SQLAlchemyError:
        db.rollback()
        logger.exception(
            "admin_user_seed_failed",
            extra={"_structured": {"email": settings.admin_email}},
        )
        raise
