from starlette.requests import Request
import hashlib, secrets

def get_current_user(request: Request):
    return request.session.get("user")

def require_auth(request: Request):
    if not get_current_user(request):
        return False
    return True

def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.sha256((salt + password).encode()).hexdigest()
    return f"{salt}${digest}"

def verify_password(password: str, hashed: str) -> bool:
    try:
        salt, digest = hashed.split("$", 1)
        return hashlib.sha256((salt + password).encode()).hexdigest() == digest
    except Exception:
        return False
