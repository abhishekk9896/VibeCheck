def authenticate_user(username: str, password: str) -> bool:
    return username == "alice" and password == "password123"


def dashboard():
    # Intentionally does not call authenticate_user().
    return {"message": "private dashboard data"}
