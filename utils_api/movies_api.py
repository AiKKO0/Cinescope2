from custom_requester.custom_requester import CustomRequester
from constants import Movies_URL, MOVIES_ENDPOINT

class MoviesApi(CustomRequester):
    """
        Класс для работы с API фильмов.
    """
    def __init__(self, session):
        super().__init__(session=session, base_url=Movies_URL)

    def create_movie(self, movie_data, expected_status=201):
        """
        Создание нового фильма.
        :param movie_data: Данные фильма.
        :param expected_status: Ожидаемый статус-код.
        """
        return self.send_request(
            method="POST",
            endpoint=MOVIES_ENDPOINT,
            data=movie_data,
            expected_status=expected_status
        )

    def get_movies(self, params=None, expected_status=200):
        return self.send_request(
            method="GET",
            endpoint=MOVIES_ENDPOINT,
            params=params,
            expected_status=expected_status
        )

    def get_movies_by_id(self, movie_id, expected_status=200):
        """
        Получение фильма по ID.
        :param movie_id: ID фильма.
        :param expected_status: Ожидаемый статус-код.
        """
        return self.send_request(
            method="GET",
            endpoint=f"{MOVIES_ENDPOINT}/{movie_id}",
            expected_status=expected_status
        )
    def patch_movies(self, movie_id, update_data, expected_status=200):
        """
        Обновление фильма.
        :param movie_id: ID фильма.
        :param update_data: Данные для обновления.
        :param expected_status: Ожидаемый статус-код.
        """
        return self.send_request(
            method="PATCH",
            endpoint=f"{MOVIES_ENDPOINT}/{movie_id}",
            data=update_data,
            expected_status=expected_status
        )

    def delete_movie(self, movie_id, expected_status=200):
        """
        Удаление фильма.
        :param movie_id: ID фильма.
        :param expected_status: Ожидаемый статус-код.
        """
        return self.send_request(
            method="DELETE",
            endpoint=f"{MOVIES_ENDPOINT}/{movie_id}",
            expected_status=expected_status
        )

