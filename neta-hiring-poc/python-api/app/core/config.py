import os
from functools import lru_cache
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]
ENV_FILE = BASE_DIR / ".env"


def load_env_file(path: Path = ENV_FILE) -> None:
    if not path.exists():
        return

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")

        os.environ.setdefault(key, value)


class Settings:
    def __init__(self) -> None:
        load_env_file()
        self.database_url = os.getenv(
            "DATABASE_URL",
            "mysql+pymysql://root:password@localhost:3306/hiring",
        )
        self.backblaze_endpoint = os.getenv("BACKBLAZE_ENDPOINT", "")
        self.backblaze_bucket = os.getenv("BACKBLAZE_BUCKET", "")
        self.backblaze_access_key = os.getenv("BACKBLAZE_ACCESS_KEY", "")
        self.backblaze_secret_key = os.getenv("BACKBLAZE_SECRET_KEY", "")
        self.jwt_secret_key = os.getenv("JWT_SECRET_KEY", "")
        self.jwt_algorithm = os.getenv("JWT_ALGORITHM", "HS256")
        self.jwt_audience = os.getenv("JWT_AUDIENCE")
        self.jwt_issuer = os.getenv("JWT_ISSUER")
        self.jwt_expires_minutes = int(os.getenv("JWT_EXPIRES_MINUTES", "60"))
        self.admin_email = os.getenv("ADMIN_EMAIL", "admin@neta.local")
        self.admin_password = os.getenv("ADMIN_PASSWORD", "Neta1234")
        self.admin_full_name = os.getenv("ADMIN_FULL_NAME", "Administrador POC")


@lru_cache
def get_settings() -> Settings:
    return Settings()
