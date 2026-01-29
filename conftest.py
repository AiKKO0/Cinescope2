from faker import Faker
import pytest
import requests
import os

from api_manager import ApiManager
from constants import BASE_URL, REGISTER_ENDPOINT, LOGIN_ENDPOINT
from custom_requester.custom_requester import CustomRequester
from entities.user import User
from utils.data_generator import DataGenerator
from dotenv import load_dotenv
from resources.user_creds import SuperAdminCreds
from constant.roles import Roles

load_dotenv()
faker = Faker()

@pytest.fixture(scope="session")
def test_user():
    random_password = DataGenerator.generate_random_password()

    return {
        "email": DataGenerator.generate_random_email(),
        "fullName": DataGenerator.generate_random_name(),
        "password": random_password,
        "passwordRepeat": random_password,
        "roles": [Roles.USER.value]
    }


@pytest.fixture(scope="session")
def registered_user(api_manager):
    """
    Фикстура для регистрации и получения данных зарегистрированного пользователя.
    """
    # Создаём данные пользователя прямо здесь
    random_password = DataGenerator.generate_random_password()
    user_data = {
        "email": DataGenerator.generate_random_email(),
        "fullName": DataGenerator.generate_random_name(),
        "password": random_password,
        "passwordRepeat": random_password,
        "roles": [Roles.USER.value]
    }

    response = api_manager.auth_api.register_user(user_data)
    response_data = response.json()

    registered_user_data = user_data.copy()
    registered_user_data["id"] = response_data["id"]
    yield registered_user_data

    # Пост-обработка: удаление пользователя
    try:
        api_manager.user_api.delete_user(registered_user_data["id"])
    except Exception as e:
        print(f"⚠️ Не удалось удалить пользователя {registered_user_data['id']}: {e}")

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

@pytest.fixture(scope="function")
def unauth_api_manager():
    """
    Неавторизованный менеджер для тестов без токена
    """
    session = requests.Session()  # Создаём новую сессию
    manager = ApiManager(session)
    return manager

@pytest.fixture(scope="session")
def test_movie():
    """
    Генерация случайного фильма
    """
    return DataGenerator.gererate_random_film()

@pytest.fixture(scope="session")
def created_movie(api_manager, test_movie, superadmin_auth):
    response = api_manager.movies_api.create_movie(test_movie)
    movie_data = response.json()

    yield movie_data

    try:
        api_manager.movies_api.delete_movie(
            movie_data["id"],
            expected_status=[200, 404]  # Принимаем и 200, и 404
        )
    except:
        pass  # Игнорируем любые ошибки при удалении

@pytest.fixture(scope="session")
def movie_update_data():
    """
    Генерация данных для обновления фильма.
    """
    full_data = DataGenerator.gererate_random_film()

    return {
        "name": full_data["name"],
        "price": full_data["price"],
        "description": full_data["description"],
        "published": full_data["published"]
        # НЕ включаем: location, genreId, imageUrl
    }



@pytest.fixture(scope="session")
def superadmin_credentials():
    email = os.getenv("SUPERADMIN_EMAIL")
    password = os.getenv("SUPERADMIN_PASSWORD")

    if not email or not password:
        pytest.skip("Superadmin credentials not found in .env file")

    return {"email": email, "password": password}

@pytest.fixture(scope="session")
def superadmin_auth(api_manager, superadmin_credentials):
        """
        Фикстура для авторизации суперадмина.
        Использует заранее известные креды или создаёт суперадмина.
        """
        # Логин с креды суперадмина
        response = api_manager.auth_api.login_user(superadmin_credentials)
        response_data = response.json()

        # Установка токена в сессию
        token = response_data["accessToken"]

        # Возврат session с заголовками
        api_manager.auth_api._update_session_headers(
            authorization=f"Bearer {token}"
        )

        return api_manager

@pytest.fixture
def user_session():
    user_pool = []

    def _create_user_session():
        session = requests.Session()
        user_session = ApiManager(session)
        user_pool.append(user_session)
        return user_session

    yield _create_user_session

    for user in user_pool:
        user.close_session()

@pytest.fixture
def super_admin(user_session):
    new_session = user_session()

    super_admin = User(
        SuperAdminCreds.USERNAME,
        SuperAdminCreds.PASSWORD,
        [Roles.SUPER_ADMIN.value],
        new_session)

    super_admin.api.auth_api.authenticate(super_admin.creds)
    return super_admin

# @pytest.fixture(scope="function")
# def creation_user_data(test_user):
#     udated_data = test_user.copy()
#     udated_data.update({
#         "verified": True,
#         "banned": False
#     })
#     return udated_data

@pytest.fixture(scope="function")
def creation_user_data():
    """
    Генерация уникальных данных пользователя для каждого теста.
    Не зависит от test_user фикстуры.
    """

    return {
        "email": DataGenerator.generate_random_email(),
        "fullName": DataGenerator.generate_random_name(),
        "password": DataGenerator.generate_random_password(),
        "passwordRepeat": DataGenerator.generate_random_password(),
        "roles": [Roles.USER.value],
        "verified": True,
        "banned": False
    }

@pytest.fixture
def common_user(user_session, super_admin, creation_user_data):
    new_session = user_session()

    common_user = User(
        creation_user_data['email'],
        creation_user_data['password'],
        [Roles.USER.value],
        new_session)

    super_admin.api.user_api.create_user(creation_user_data)
    common_user.api.auth_api.authenticate(common_user.creds)
    return common_user

@pytest.fixture
def existing_admin_user(user_session):
    email = os.getenv("ADMIN_EMAIL")
    password = os.getenv("ADMIN_PASSWORD")

    new_session = user_session()

    # Создаём admin user
    admin_user = User(
        email,
        password,
        [Roles.ADMIN.value],  # Роль ADMIN
        new_session
    )

    admin_user.api.auth_api.authenticate(admin_user.creds)
    return admin_user

