from sample_app.auth import generate_token, login


def test_login_success():
    result = login("admin", "secret123")
    assert result["status"] == "success"
    assert "token" in result


def test_login_failure():
    result = login("admin", "wrongpass")
    assert result["status"] == "error"


def test_generate_token():
    token = generate_token("user_42")
    assert token is not None
