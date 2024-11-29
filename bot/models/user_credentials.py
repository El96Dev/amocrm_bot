from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import BigInteger

from .base import Base


class UserCredentials(Base):
    __tablename__ = "user_credentials"
    chat_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, unique=True, nullable=False)
    client_id: Mapped[str] = mapped_column(nullable=False)
    secret_key: Mapped[str] = mapped_column(nullable=False)
    redirect_url: Mapped[str] = mapped_column(nullable=False)
    subdomain: Mapped[str] = mapped_column(nullable=False)
    auth_code: Mapped[str] = mapped_column(nullable=False)