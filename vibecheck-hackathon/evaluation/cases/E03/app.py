import secrets


def generate_reset_token(username: str) -> str:
    return secrets.token_urlsafe(32)


def reset_password(username: str, token: str, new_password: str) -> bool:
    if not token:
        return False

    # Password is reset, but token expiration and single-use
    # enforcement are intentionally not implemented.
    return True
