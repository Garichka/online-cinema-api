from tests.conftest import register_and_activate


def test_register_success(client):
    response = client.post(
        "/auth/register",
        json={"email": "newuser@test.com", "password": "TestPass123!"},
    )
    assert response.status_code == 201
    assert "id" in response.json()


def test_register_duplicate_email(client):
    email = "dup@test.com"
    client.post("/auth/register", json={"email": email, "password": "TestPass123!"})

    response = client.post(
        "/auth/register", json={"email": email, "password": "TestPass123!"}
    )
    assert response.status_code == 400


def test_login_success(client):
    email = "login_ok@test.com"
    register_and_activate(client, email)

    response = client.post(
        "/auth/login", json={"email": email, "password": "TestPass123!"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_invalid_credentials(client):
    response = client.post(
        "/auth/login", json={"email": "no@test.com", "password": "WrongPass99!"}
    )
    assert response.status_code == 401


def test_login_inactive_account(client):
    email = "inactive@test.com"
    client.post("/auth/register", json={"email": email, "password": "TestPass123!"})

    response = client.post(
        "/auth/login", json={"email": email, "password": "TestPass123!"}
    )
    assert response.status_code == 403
