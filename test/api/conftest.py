from faker import Faker
import pytest
import requests

from api_manager import ApiManager
from constants import BASE_URL, REGISTER_ENDPOINT, LOGIN_ENDPOINT
from custom_requester.custom_requester import CustomRequester
from utils.data_generator import DataGenerator

faker = Faker()

@pytest.fixture(scope="session")
def test_user():
    """
    Генерация случайного пользователя для тестов.
    """
    random_email = DataGenerator.generate_random_email()
    random_name = DataGenerator.generate_random_name()
    random_password = DataGenerator.generate_random_password()

    return {
        "email": random_email,
        "fullName": random_name,
        "password": random_password,
        "passwordRepeat": random_password,
        "roles": ["USER"]
    }

@pytest.fixture(scope="session")
def registered_user(api_manager, test_user):
    """
        Фикстура для регистрации и получения данных зарегистрированного пользователя.
        Регистрирует пользователя через AuthAPI, после теста удаляет через UserAPI.
    """
    response = api_manager.auth_api.register_user(test_user)
    response_data = response.json()

    registered_user = test_user.copy()
    registered_user["id"] = response_data["id"]
    yield registered_user

    # 3. Пост-обработка: удаление пользователя через API-класс
    try:
        api_manager.user_api.delete_user(registered_user["id"])
    except Exception as e:
        # Логируем ошибку, но не падаем
        print(f"⚠️ Не удалось удалить пользователя {registered_user['id']}: {e}")


@pytest.fixture(scope="session")
def requester():
    """
    Фикстура для создания экземпляра CustomRequester.
    """
    session = requests.Session()
    return CustomRequester(session=session, base_url=BASE_URL)

@pytest.fixture(scope="session")
def session():
    """
    Фикстура для создания HTTP-сессии.
    """
    http_session = requests.Session()
    yield http_session
    http_session.close()

@pytest.fixture(scope="session")
def api_manager(session):
    """
    Фикстура для создания экземпляра ApiManager.
    """
    return ApiManager(session)