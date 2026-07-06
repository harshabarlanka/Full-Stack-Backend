def test_signup_creates_user(client):
    response = client.post(
        "/users/signup",
        json={"email": "test@example.com", "password": "secret123"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "id" in data
    assert "hashed_password" not in data  # never leak this


def test_signup_duplicate_email_rejected(client):
    client.post("/users/signup", json={"email": "test@example.com", "password": "secret123"})
    response = client.post("/users/signup", json={"email": "test@example.com", "password": "different"})
    assert response.status_code == 400


def test_login_with_correct_credentials(client):
    client.post("/users/signup", json={"email": "test@example.com", "password": "secret123"})
    response = client.post("/users/login", json={"email": "test@example.com", "password": "secret123"})
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_with_wrong_password_rejected(client):
    client.post("/users/signup", json={"email": "test@example.com", "password": "secret123"})
    response = client.post("/users/login", json={"email": "test@example.com", "password": "wrongpassword"})
    assert response.status_code == 401