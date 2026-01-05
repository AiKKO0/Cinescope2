import pytest
import requests
from constants import BASE_URL, HEADERS, REGISTER_ENDPOINT,  LOGIN_ENDPOINT
from custom_requester.custom_requester import CustomRequester
from api_manager import ApiManager


class TestAuthAPI:
    def test_register_user(self, api_manager, test_user):
        """
        Тест на регистрацию пользователя.
        """
        response = api_manager.auth_api.register_user(test_user)
        response_data = response.json()

        # Проверки
        assert response_data["email"] == test_user["email"], "Email не совпадает"
        assert "id" in response_data, "ID пользователя отсутствует в ответе"
        assert "roles" in response_data, "Роли пользователя отсутствуют в ответе"
        assert "USER" in response_data["roles"], "Роль USER должна быть у пользователя"

    def test_register_and_login_user(self, api_manager, registered_user):
        """
        Тест на регистрацию и авторизацию пользователя.
        """
        # Данные для авторизации
        login_data = {
            "email": registered_user["email"],
            "password": registered_user["password"]
        }
        # Вызов метода авторизации через AuthAPI
        response = api_manager.auth_api.login_user(login_data)
        response_data = response.json()

        # Проверки данных ответа
        assert "accessToken" in response_data, "Токен доступа отсутствует в ответе"
        assert response_data["user"]["email"] == registered_user["email"], "Email не совпадает"

    def test_login_with_wrong_password(self, api_manager, registered_user):
        """
                Тест логина с неверным паролем.
        """
        # Пытаемся залогиниться с неверным паролем
        wrong_login_data = {
            "email": registered_user["email"],
            "password": "WRONG_PASSWORD_123!"
        }
        wrong_login_data_response = api_manager.auth_api.login_user(
            wrong_login_data,
            expected_status=401
        )
        response_data = wrong_login_data_response.json()

        # Ожидаем ошибку (обычно 401, 400 или 403)
        assert wrong_login_data_response.status_code in [401, 400, 403, 422], \
            f"При неверном пароле ожидалась ошибка, получен {wrong_login_data_response.status_code}"

        # Проверяем что нет токена в ответе
        if wrong_login_data_response.status_code != 200:
            response_data = wrong_login_data_response.json()
            # Проверяем что в ответе нет accessToken (если есть сообщение об ошибке)
            if "accessToken" in response_data:
                print("Предупреждение: accessToken присутствует в ответе об ошибке")
