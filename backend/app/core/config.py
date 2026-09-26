from functools import lru_cache
from typing import Literal
from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    support_contact: str = "juspjchaco@gmail.com"
    app_name: str = "junta_electoral"
    app_env: str = "development"
    debug: bool = False

    api_v1_prefix: str = "/api/v1"

    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7

    jwt_issuer: str = "junta-electoral"
    jwt_audience: str = "junta-electoral-web"
    jwt_key_id: str = "current"
    jwt_previous_keys: dict[str, str] = {}
    session_idle_hours: int = 24
    reauth_minutes: int = 5
    cookie_secure: bool = False
    frontend_url: str = "http://localhost:5173"
    login_max_failures: int = 3
    login_window_minutes: int = 15
    login_lock_minutes: int = 30
    auth_ip_limit: int = 100
    auth_identifier_limit: int = 20
    invitation_expire_hours: int = 48
    invitation_hourly_limit: int = 20
    reset_expire_minutes: int = 30
    mail_cooldown_seconds: int = 60
    smtp_host: str = "127.0.0.1"
    smtp_port: int = 1025
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_tls: Literal["none", "starttls", "ssl"] = "none"
    smtp_timeout: int = 10
    smtp_from: str = "Junta Electoral <no-reply@junta.local>"
    mail_outbox_key: str = ""
    mail_max_attempts: int = 5
    mail_lease_seconds: int = 120
    security_retention_days: int = 30

    @model_validator(mode="after")
    def secure_configuration(self):
        from urllib.parse import urlsplit

        if (
            self.algorithm != "HS256"
            or len(self.secret_key.encode()) < 32
            or "REEMPLAZAR" in self.secret_key
            or len(set(self.secret_key)) < 8
        ):
            raise ValueError(
                "HS256 requiere SECRET_KEY aleatoria de al menos 32 bytes."
            )
        if any(len(v.encode()) < 32 for v in self.jwt_previous_keys.values()):
            raise ValueError("Clave JWT anterior débil.")
        if self.jwt_key_id in self.jwt_previous_keys:
            raise ValueError("kid actual duplicado.")
        if any(
            "*" in origin or urlsplit(origin).scheme not in ("http", "https")
            for origin in self.cors_origins
        ):
            raise ValueError("CORS requiere orígenes explícitos.")
        if not self.mail_outbox_key:
            raise ValueError(
                "Configure MAIL_OUTBOX_KEY (Fernet) antes de iniciar API o worker."
            )
        from cryptography.fernet import Fernet

        Fernet(self.mail_outbox_key.encode())
        if self.app_env != "development" and self.app_env != "test":
            if (
                self.debug
                or not self.cookie_secure
                or not self.frontend_url.startswith("https://")
                or any(not o.startswith("https://") for o in self.cors_origins)
                or self.smtp_tls == "none"
                or not self.mail_outbox_key
            ):
                raise ValueError(
                    "Producción requiere HTTPS, cookie Secure, SMTP TLS y clave outbox."
                )
        if self.smtp_tls == "none" and self.smtp_host not in (
            "localhost",
            "127.0.0.1",
            "mailpit",
        ):
            raise ValueError("SMTP sin TLS solo permitido para capturador local.")
        for name in (
            "access_token_expire_minutes",
            "refresh_token_expire_days",
            "session_idle_hours",
            "reauth_minutes",
            "login_max_failures",
            "login_window_minutes",
            "login_lock_minutes",
            "auth_ip_limit",
            "auth_identifier_limit",
            "reset_expire_minutes",
            "invitation_expire_hours",
            "invitation_hourly_limit",
            "mail_cooldown_seconds",
            "smtp_timeout",
            "mail_max_attempts",
            "security_retention_days",
        ):
            if getattr(self, name) <= 0:
                raise ValueError(f"{name} debe ser positivo.")
        if self.mail_lease_seconds <= self.smtp_timeout * 4:
            raise ValueError("Lease SMTP debe superar cuatro timeouts.")
        return self

    database_url: str

    cors_origins: list[str] = ["http://localhost:5173"]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        hide_input_in_errors=True,
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
