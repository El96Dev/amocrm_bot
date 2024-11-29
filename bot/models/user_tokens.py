from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import BigInteger

from .base import Base


class UserTokens(Base):
    __tablename__ = "user_tokens"
    chat_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, unique=True, nullable=False)
    access_token: Mapped[str] = mapped_column(nullable=False)
    refresh_token: Mapped[str] = mapped_column(nullable=False)