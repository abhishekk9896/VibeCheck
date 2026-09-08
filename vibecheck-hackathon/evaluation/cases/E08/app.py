def validate_password(password: str) -> bool:
    # Intentionally incorrect: accepts passwords shorter than 12 characters.
    return len(password) >= 12
