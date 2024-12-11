import time
from locust import HttpUser, task, between
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

# Проверка основного маршрута
def test_read_main():
    response = client.get("/")
    assert response.status_code == 200

# Проверка получения списка пользователей
def test_get_users():
    response = client.get("/users/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["username"] == "string"

# Проверка создания нового пользователя
def test_create_user():
    response = client.post(
        "/register/",
        json={"username": "test", "email": "tester@mail.ru",
              "full_name": "Test", "password": "12345"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "test"
    assert data["email"] == "tester@mail.ru"

# Проверка успешной регистрации пользователя
def test_successful_registration():
    response = client.post(
        "/register/",
        json={"username": "test", "email": "tester@mail.ru", "full_name": "Test",
              "password": "12345"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "test"
    assert data["email"] == "tester@mail.ru"

# Проверка регистрации пользователя с дублирующимися данными
def test_duplicate_registration():
    client.post(
        "/register/",
        json={"username": "test", "email": "tester@mail.ru", "full_name": "Test",
              "password": "12345"}
    )
    response = client.post(
        "/register/",
        json={"username": "test", "email": "tester@mail.ru", "full_name": "Test",
              "password": "12345"}
    )
    assert response.status_code == 400

# Проверка успешной аутентификации пользователя
def test_successful_authentication():
    client.post(
        "/register/",
        json={"username": "test", "email": "tester@mail.ru", "full_name": "Test",
              "password": "12345"}
    )
    response = client.post(
        "/token",
        data={"username": "test", "password": "12345"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data

# Проверка неуспешной аутентификации пользователя
def test_failed_authentication():
    response = client.post(
        "/token",
        data={"username": "test", "password": "123"}
    )
    assert response.status_code == 401

# Проверка истекшего токена
def test_expired_token():
    client.post(
        "/register/",
        json={"username": "test", "email": "tester@mail.ru", "full_name": "Test",
              "password": "12345"}
    )
    response = client.post(
        "/token",
        data={"username": "test", "password": "12345"}
    )
    token = response.json()["access_token"]
    time.sleep(3600)
    response = client.get("/users/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401

# Проверка получения списка пользователей с деталями
def test_get_users_details():
    response = client.get("/users/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert "username" in data[0]
    assert "email" in data[0]

# Проверка получения текущего пользователя
def test_get_current_user():
    client.post(
        "/register/",
        json={"username": "test", "email": "tester@mail.ru", "full_name": "Test",
              "password": "12345"}
    )
    response = client.post(
        "/token",
        data={"username": "test", "password": "12345"}
    )
    token = response.json()["access_token"]
    response = client.get("/users/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "test"
    assert data["email"] == "tester@mail.ru"

# Проверка обновления данных пользователя
def test_update_user():
    client.post(
        "/register/",
        json={"username": "test", "email": "tester@mail.ru", "full_name": "Test",
              "password": "12345"}
    )
    response = client.post(
        "/token",
        data={"username": "test", "password": "12345"}
    )
    token = response.json()["access_token"]
    response = client.put(
        "/users/1",
        headers={"Authorization": f"Bearer {token}"},
        json={"full_name": "Updated"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["full_name"] == "Updated"

# Проверка обновления данных пользователя с некорректными данными
def test_update_user_invalid_data():
    client.post(
        "/register/",
        json={"username": "test", "email": "tester@mail.ru", "full_name": "Test",
              "password": "12345"}
    )
    response = client.post(
        "/token",
        data={"username": "test", "password": "12345"}
    )
    token = response.json()["access_token"]
    response = client.put(
        "/users/1",
        headers={"Authorization": f"Bearer {token}"},
        json={"full_name": ""}
    )
    assert response.status_code == 422

# Проверка обновления данных пользователя без токена
def test_update_user_without_token():
    response = client.put(
        "/users/1",
        json={"full_name": "Updated"}
    )
    assert response.status_code == 401

# Проверка удаления пользователя
def test_delete_user():
    client.post(
        "/register/",
        json={"username": "test", "email": "tester@mail.ru", "full_name": "Test",
              "password": "12345"}
    )
    response = client.post(
        "/token",
        data={"username": "test", "password": "12345"}
    )
    token = response.json()["access_token"]
    response = client.delete(
        "/users/1",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200

# Проверка повторного удаления пользователя
def test_delete_user_again():
    client.post(
        "/register/",
        json={"username": "test", "email": "tester@mail.ru", "full_name": "Test",
              "password": "12345"}
    )
    response = client.post(
        "/token",
        data={"username": "test", "password": "12345"}
    )
    token = response.json()["access_token"]
    client.delete(
        "/users/1",
        headers={"Authorization": f"Bearer {token}"}
    )
    response = client.delete(
        "/users/1",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 404

# Проверка CORS заголовков
def test_cors():
    response = client.options("/users/")
    assert response.status_code == 200
    assert "Access-Control-Allow-Origin" in response.headers
    assert response.headers["Access-Control-Allow-Origin"] == "*"

# Проверка CORS заголовков для неподдерживаемого домена
def test_cors_unsupported_domain():
    response = client.options("/users/", headers={"Origin": "http://localhost:8000"})
    assert response.status_code == 200
    assert "Access-Control-Allow-Origin" not in response.headers

# Проверка регистрации пользователя с отсутствующими полями
def test_missing_fields():
    response = client.post(
        "/register/",
        json={"username": "test", "email": "tester@mail.ru", "password": "12345"}
    )
    assert response.status_code == 422

class WebsiteUser(HttpUser):
    wait_time = between(1, 5)

    @task
    def register_user(self):
        self.client.post("/register/",
                         json={"username": "test", "email": "tester@mail.ru", "full_name": "Test",
                               "password": "12345"})

# Проверка доступа без авторизации
def test_unauthorized_access():
    response = client.get("/users/me")
    assert response.status_code == 401

# Проверка доступа с некорректным токеном
def test_invalid_token():
    response = client.get("/users/me", headers={"Authorization": "Bearer invalidtoken"})
    assert response.status_code == 401
