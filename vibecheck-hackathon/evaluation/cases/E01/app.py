USERS = {
    "alice": "password123",
}


def login(username: str, password: str) -> str | None:
    if USERS.get(username) != password:
        return None

    return generate_token(username)


def generate_token(username: str) -> str:
    return f"token-{username}"