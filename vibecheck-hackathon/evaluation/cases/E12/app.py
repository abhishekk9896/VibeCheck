def authenticate_user(username: str, password: str) -> bool:
    return username == "alice" and password == "password123"


def require_authentication(username: str, password: str) -> bool:
    return authenticate_user(username, password)


def get_account_data(username: str, password: str) -> dict:
    # Intentionally incorrect:
    # the authentication guard exists but is never called.
    return {
        "username": username,
        "balance": 5000,
        "private_data": "sensitive"
    }
