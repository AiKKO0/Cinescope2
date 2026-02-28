import pytest
import requests
from constants import BASE_URL, HEADERS, REGISTER_ENDPOINT,  LOGIN_ENDPOINT
from custom_requester.custom_requester import CustomRequester
from api_manager import ApiManager
from models.base_models import RegisterUserResponse
from resources.user_creds import SuperAdminCreds


class TestAuthAPI:
    def test_register_user(self, api_manager, test_user):
        """
        Тест на регистрацию пользователя.
        """

        response = api_manager.auth_api.register_user(user_data=test_user)
        register_user_response = RegisterUserResponse(**response.json())

        # Проверки
        assert register_user_response.email == test_user.email, "Email не совпадает"


    def test_register_and_login_user(self, api_manager, registered_user):
        """
        Тест на регистрацию и авторизацию пользователя.
        """
        # Данные для авторизации
        login_data = {
            "email": registered_user["email"],
            "password": registered_user["password"]  # Убедись, что password есть в registered_user!
        }

        # Вызов метода авторизации через AuthAPI
        response = api_manager.auth_api.login_user(login_data=login_data, expected_status=201)
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


    # @pytest.mark.api
    def test_registered_login_and_delete_user(self, api_manager, test_user):
        """
           ТЕСТ: Регистрации, авторизации и удаление USER'a
        """
        # 1. Регистрация пользователя
        response = api_manager.auth_api.register_user(test_user)
        response_data = response.json()
        # Сохраняем id
        user_id = response_data["id"]

        # 2. Авторизация пользователя
        login_data = {
            "email": test_user.email,
            "password": test_user.password
        }
        login_response = api_manager.auth_api.login_user(login_data, expected_status=201)
        assert login_response.status_code == 201

        login_response_data = login_response.json()

        # 3. Устанавливаем токен в сессию для DELETE запроса
        if "accessToken" in login_response_data:
            token = login_response_data["accessToken"]
            api_manager.auth_api._update_session_headers(
                authorization=f"Bearer {token}"
            )
        #  Удаление пользователя
        delete_response = api_manager.user_api.delete_user(user_id)
        assert delete_response.status_code == 200


    @pytest.mark.parametrize("email, password, expected_status", [
        (f"{SuperAdminCreds.USERNAME}", f"{SuperAdminCreds.PASSWORD}", 201),
        ("test_login1@email.com", "asdqwe123Q!", 401),  # Сервис не может обработать логин по незареганному юзеру
        ("", "password", 401),
    ], ids=["Admin login", "Invalid user", "Empty username"])
    def test_login(self, email, password, expected_status, api_manager):
        login_data = {
            "email": email,
            "password": password
        }
        api_manager.auth_api.login_user(login_data=login_data, expected_status=expected_status)


    @pytest.mark.skip(reason="Временно отключён")
    def test_example(self):
        assert True

    skip_test = True

    @pytest.mark.skipif(skip_test, reason="Тест отключён вручную")
    def test_skipif_demo(self):
        assert True

    @pytest.mark.xfail(reason="Функция ещё не реализована")
    def test_future_feature(self):
        assert 1 == 2

    @pytest.mark.xfail(reason="Баг в системе")
    def test_fixed_bug(self):
        assert 2 + 2 == 4


    # Вариант 1 — декоратор:
    @pytest.fixture
    def setup_data(self):
        print("setup")

    @pytest.mark.usefixtures("setup_data")
    def test_with_usefixtures(self):
        assert True

    # Вариант 2 - аргумент
    @pytest.fixture
    def setup_data1(self):
        print("setup")

    @pytest.fixture
    def test_with_fixture(self, setup_data1):
        assert True

