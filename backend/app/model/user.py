"""SQLAlchemy models for user data; DATETIME values use naive UTC."""
from sqlalchemy import (
    Boolean, CheckConstraint, Column, Enum, ForeignKey, Index, String, Text, UniqueConstraint, text,
)
from sqlalchemy.dialects.mysql import BIGINT, DATETIME

from app.model.base import Base


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint("email", name="uq_users_1"),
        UniqueConstraint("phone", name="uq_users_2"),
        CheckConstraint("email IS NOT NULL OR phone IS NOT NULL", name="ck_users_1"),
        Index("ix_users_1", "avatar_file_id"),
        {"mysql_engine": "InnoDB", "mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci"},
    )

    id = Column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    email = Column(String(254), nullable=True)
    phone = Column(String(32), nullable=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum("customer", "admin"), nullable=False, server_default="customer")
    is_active = Column(Boolean, nullable=False, server_default=text("1"))
    avatar_file_id = Column(BIGINT(unsigned=True), ForeignKey("files.id", name="fk_users_avatar_file_id", ondelete="RESTRICT", use_alter=True), nullable=True)
    email_verified_at = Column(DATETIME(fsp=6), nullable=True)
    phone_verified_at = Column(DATETIME(fsp=6), nullable=True)
    last_login_at = Column(DATETIME(fsp=6), nullable=True)
    created_at = Column(DATETIME(fsp=6), nullable=False, server_default=text("CURRENT_TIMESTAMP(6)"))
    updated_at = Column(DATETIME(fsp=6), nullable=False, server_default=text("CURRENT_TIMESTAMP(6)"), onupdate=text("CURRENT_TIMESTAMP(6)"))


class Customer(Base):
    __tablename__ = "customers"
    __table_args__ = (
        Index("ix_customers_1", "name"),
        Index("ix_customers_2", "phone"),
        {"mysql_engine": "InnoDB", "mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci"},
    )

    id = Column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    customer_code = Column(String(40), nullable=False, unique=True)
    user_id = Column(BIGINT(unsigned=True), ForeignKey("users.id", name="fk_customers_user_id", ondelete="RESTRICT", use_alter=True), nullable=True, unique=True)
    name = Column(String(255), nullable=False)
    email = Column(String(254), nullable=True)
    phone = Column(String(32), nullable=False)
    notes = Column(Text, nullable=True)
    is_active = Column(Boolean, nullable=False, server_default=text("1"))
    created_at = Column(DATETIME(fsp=6), nullable=False, server_default=text("CURRENT_TIMESTAMP(6)"))
    updated_at = Column(DATETIME(fsp=6), nullable=False, server_default=text("CURRENT_TIMESTAMP(6)"), onupdate=text("CURRENT_TIMESTAMP(6)"))


class AuthSession(Base):
    __tablename__ = "auth_sessions"
    __table_args__ = (
        Index("ix_auth_sessions_1", "user_id", "expires_at"),
        {"mysql_engine": "InnoDB", "mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci"},
    )

    id = Column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    user_id = Column(BIGINT(unsigned=True), ForeignKey("users.id", name="fk_auth_sessions_user_id", ondelete="RESTRICT", use_alter=True), nullable=False)
    refresh_token_hash = Column(String(64), nullable=False, unique=True)
    expires_at = Column(DATETIME(fsp=6), nullable=False)
    revoked_at = Column(DATETIME(fsp=6), nullable=True)
    last_used_at = Column(DATETIME(fsp=6), nullable=True)
    created_at = Column(DATETIME(fsp=6), nullable=False, server_default=text("CURRENT_TIMESTAMP(6)"))
    updated_at = Column(DATETIME(fsp=6), nullable=False, server_default=text("CURRENT_TIMESTAMP(6)"), onupdate=text("CURRENT_TIMESTAMP(6)"))


class AccountToken(Base):
    __tablename__ = "account_tokens"
    __table_args__ = (
        Index("ix_account_tokens_1", "user_id", "purpose"),
        {"mysql_engine": "InnoDB", "mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci"},
    )

    id = Column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    user_id = Column(BIGINT(unsigned=True), ForeignKey("users.id", name="fk_account_tokens_user_id", ondelete="RESTRICT", use_alter=True), nullable=False)
    purpose = Column(Enum("password_reset", "account_invitation"), nullable=False)
    token_hash = Column(String(64), nullable=False, unique=True)
    expires_at = Column(DATETIME(fsp=6), nullable=False)
    used_at = Column(DATETIME(fsp=6), nullable=True)
    created_at = Column(DATETIME(fsp=6), nullable=False, server_default=text("CURRENT_TIMESTAMP(6)"))
