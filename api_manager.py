# from .api.api.auth_api import AuthAPI
# from .api.api.user_api import UserAPI
# from .api.api.movies_api import MoviesApi
from utils_api.auth_api import AuthAPI
from utils_api.movies_api import MoviesApi
from utils_api.user_api import UserApi

class ApiManager:
    """
    Класс для управления API-классами с единой HTTP-сессией.
    """
    def __init__(self, session):
        """
        Инициализация ApiManager.
        :param session: HTTP-сессия, используемая всеми API-классами.
        """
        self.session = session
        self.auth_api = AuthAPI(session)
        self.user_api = UserApi(session)
        self.movies_api = MoviesApi(session)

    def close_session(self):
        self.session.close()
