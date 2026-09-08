USERS = {}


def create_user(username: str, password: str) -> None:
    # Intentionally insecure: plaintext password is stored directly.
    USERS[username] = password
