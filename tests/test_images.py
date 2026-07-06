def _get_auth_token(client, email="test@example.com", password="secret123"):
    client.post("/users/signup", json={"email": email, "password": password})
    response = client.post("/users/login", json={"email": email, "password": password})
    return response.json()["access_token"]


def test_upload_requires_authentication(client):
    response = client.post("/images/upload", data={"title": "No auth test"})
    assert response.status_code == 401


def test_list_images_only_shows_own_images(client, monkeypatch):
    # Patch where the function is USED (routers/images.py), not where it's defined (storage.py)
    monkeypatch.setattr("app.routers.images.save_file_locally", lambda file: "fake-filename.jpg")

    token_user1 = _get_auth_token(client, "user1@example.com", "secret123")
    token_user2 = _get_auth_token(client, "user2@example.com", "secret123")

    client.post(
        "/images/upload",
        headers={"Authorization": f"Bearer {token_user1}"},
        data={"title": "User1 Image"},
        files={"file": ("test.jpg", b"fake image bytes", "image/jpeg")},
    )

    response = client.get("/images/", headers={"Authorization": f"Bearer {token_user2}"})
    assert response.status_code == 200
    assert response.json() == []


def test_delete_someone_elses_image_returns_404(client, monkeypatch):
    monkeypatch.setattr("app.routers.images.save_file_locally", lambda file: "fake-filename.jpg")
    monkeypatch.setattr("app.routers.images.delete_file_locally", lambda filename: None)

    token_user1 = _get_auth_token(client, "user1@example.com", "secret123")
    token_user2 = _get_auth_token(client, "user2@example.com", "secret123")

    upload_response = client.post(
        "/images/upload",
        headers={"Authorization": f"Bearer {token_user1}"},
        data={"title": "User1 Image"},
        files={"file": ("test.jpg", b"fake image bytes", "image/jpeg")},
    )
    image_id = upload_response.json()["id"]

    response = client.delete(f"/images/{image_id}", headers={"Authorization": f"Bearer {token_user2}"})
    assert response.status_code == 404