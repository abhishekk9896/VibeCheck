USERS = {
    "alice": "password123",
}


def login(username: str, password: str) -> str | None:
    if USERS.get(username) != password:
        return None

    return generate_token(username)


def generate_token(username: str) -> str:
    return f"token-{username}"


def process_payment(user_id: str, amount: float) -> bool:
    return amount > 0


def get_recommendations(user_id: str) -> list[str]:
    return ["item-a", "item-b"]
