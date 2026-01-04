import requests
import pytest
from constants import BASE_URL, HEADERS, REGISTER_ENDPOINT, LOGIN_ENDPOINT


class TestAuthAPI:
    def test_register_user(self, test_user):
        # URL для регистрации
        register_url = f"{BASE_URL}{REGISTER_ENDPOINT}"

        # Отправка запроса на регистрацию
        response = requests.post(register_url, json=test_user, headers=HEADERS)

        # Логируем ответ для диагностики
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text}")

        # Проверки
        assert response.status_code == 201, "Ошибка регистрации пользователя"
        response_data = response.json()
        assert response_data["email"] == test_user["email"], "Email не совпадает"
        assert "id" in response_data, "ID пользователя отсутствует в ответе"
        assert "roles" in response_data, "Роли пользователя отсутствуют в ответе"

        # Проверяем, что роль USER назначена по умолчанию
        assert "USER" in response_data["roles"], "Роль USER должна быть у пользователя"

    def test_auth_user(self, test_user):
        """
        Тест успешного логина зарегистрированного пользователя.
        Проверяет что возвращается статус 200, accessToken и user с email.
        """
        # 1. Сначала регистрируем пользователя
        register_url = f"{BASE_URL}{REGISTER_ENDPOINT}"
        register_response = requests.post(register_url, json=test_user, headers=HEADERS)

        # Если пользователь уже существует (409), это нормально - тестируем логин
        if register_response.status_code == 409:
            print(f"Пользователь {test_user['email']} уже существует, продолжаем тест логина")
        elif register_response.status_code != 201:
            pytest.fail(f"Не удалось создать пользователя: {register_response.text}")

        # 2 Тестируем логин
        login_url = f"{BASE_URL}{LOGIN_ENDPOINT}"
        login_data = {
            "email" : test_user["email"],
            "password": test_user["password"]
        }

        login_response = requests.post(login_url, json=login_data, headers=HEADERS)

        #logi
        print(f"Login request data: {login_data}")
        print(f"Login response status: {login_response.status_code}")
        print(f"Login response body: {login_response.text}")

        # 3. Проверки согласно заданию:
        # a) HTTP статус код 201
        assert login_response.status_code == 201, "Ожидался 201"

        # b) Проверяем структуру ответа
        response_data = login_response.json()

        # c) Поле accessToken
        assert "accessToken" in response_data, "В ответе отсутвует token"

        access_token = response_data["accessToken"]
        assert access_token is not None and len(access_token) > 10, \
            "accessToken пустой или слишком короткий"

        # d) Поле user с корректным email
        assert "user" in response_data, \
            "В ответе отсутствует поле user"

        user_data = response_data["user"]
        assert "email" in user_data, \
            "В объекте user отсутствует поле email"

        assert user_data["email"] == test_user["email"], \
            f"Email в ответе {user_data['email']} не совпадает с ожидаемым {test_user['email']}"

    def test_login_with_wrong_password(self, test_user):
        """
                Тест логина с неверным паролем.
        """
        # Сначала убедимся что пользователь существует
        register_url = f"{BASE_URL}{REGISTER_ENDPOINT}"
        response = requests.post(register_url, json=test_user, headers=HEADERS)

        if response.status_code not in [201, 409]:
            pytest.skip(f"Не удалось создать пользователя для теста: {response.status_code}")

        # Пытаемся залогиниться с неверным паролем
        login_url = f"{BASE_URL}{LOGIN_ENDPOINT}"
        wrong_login_data = {
            "email": test_user["email"],
            "password": "WRONG_PASSWORD_123!"
        }

        login_response = requests.post(login_url, json=wrong_login_data, headers=HEADERS)

        print(f"Wrong password login status: {login_response.status_code}")
        print(f"Wrong password login response: {login_response.text}")

        # Ожидаем ошибку (обычно 401, 400 или 403)
        assert login_response.status_code in [401, 400, 403, 422], \
            f"При неверном пароле ожидалась ошибка, получен {login_response.status_code}"

        # Проверяем что нет токена в ответе
        if login_response.status_code != 200:
            response_data = login_response.json()
            # Проверяем что в ответе нет accessToken (если есть сообщение об ошибке)
            if "accessToken" in response_data:
                print("Предупреждение: accessToken присутствует в ответе об ошибке")
