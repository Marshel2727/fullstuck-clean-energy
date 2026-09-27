"""Account provisioning used by the operator CLI."""
from sqlalchemy import select
from app.model.user import User
from app.utils.passwords import passwords


def validate_user_input(email, name, role, password):
    if role not in ("admin", "customer") or not email or not name:
        raise ValueError("Input tidak valid")
    if not 15 <= len(password) <= 1024:
        raise ValueError("Gunakan passphrase sepanjang 15 sampai 1024 karakter.")


def create_user(db, email, name, role, password):
    validate_user_input(email, name, role, password)
    if db.scalar(select(User.id).where(User.email == email)):
        raise ValueError("User sudah ada; tidak diubah.")
    db.add(User(name=name, email=email, password_hash=passwords.hash(password), role=role))
    db.commit()
