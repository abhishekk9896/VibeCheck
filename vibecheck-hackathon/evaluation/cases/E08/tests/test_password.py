from app import validate_password


def test_short_password_is_rejected():
    assert validate_password("abcdefgh") is False
