USERS = {}


def register_user(username: str, password: str) -> dict:
    if not username or not password:
        return {"success": False, "error": "invalid credentials"}

    # Intentionally insecure: password is stored in plaintext.
    # Intentionally missing: duplicate username check.
    USERS[username] = password

    return {"success": True}
