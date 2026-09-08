from auth import authenticate_user


def dashboard(username: str, password: str):
    if not authenticate_user(username, password):
        return {"error": "unauthorized"}

    return {"message": "private dashboard data"}
