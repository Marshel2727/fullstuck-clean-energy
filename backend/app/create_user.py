"""Operator entry point: python -m app.create_user."""
from getpass import getpass
from app.service.user import create_user, validate_user_input
from app.utils.database import SessionLocal


def main():
    email = input("Email: ").strip()
    name = input("Nama: ").strip()
    role = input("Role (admin/customer): ").strip()
    password = getpass("Password (minimal 12 karakter): ")
    try:
        validate_user_input(email, name, role, password)
        if getpass("Ulangi password: ") != password:
            raise ValueError("Password tidak cocok")
        with SessionLocal() as db:
            create_user(db, email, name, role, password)
    except ValueError as exc:
        raise SystemExit(str(exc)) from None
    print("User dibuat. Hubungkan customer ke user_id melalui proses administrasi sebelum akses sistem.")


if __name__ == "__main__":
    main()
