"""Password hashing configuration."""
from pwdlib import PasswordHash

passwords = PasswordHash.recommended()
DUMMY_HASH = passwords.hash("dummy-password-not-a-real-user")
