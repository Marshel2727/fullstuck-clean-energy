"""Session cookie name and opaque token digest."""
import hashlib

COOKIE = "solarsync_session"


def digest(value):
    return hashlib.sha256(value.encode()).hexdigest()
