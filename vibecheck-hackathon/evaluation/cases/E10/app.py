def authenticate_user(username: str, password: str) -> bool:
    return username == "alice" and password == "password123"


def login(username: str, password: str) -> bool:
    return authenticate_user(username, password)
