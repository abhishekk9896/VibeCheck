def login(username, password):
    if username == "admin" and password == "secret123":
        return {"status": "success", "token": "fake_token_123"}
    return {"status": "error", "message": "Invalid credentials"}

def generate_token(user_id):
    if not user_id:
        return None
    return f"token_{user_id}_valid"
