USERS = {
    "alice": "password123",
}


def login(username: str, password: str) -> str | None:
    if USERS.get(username) != password:
        return None

    return f"authenticated-{username}"
