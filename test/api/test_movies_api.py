import random

import requests

from api_manager import ApiManager

# from utils.data_generator import DataGenerator

class TestMovieAPI:
    def test_movie_api_created(self, api_manager, created_movie):
        """
                Тест на создание фильма.
        """
        # Проверки:
        assert "id" in created_movie, "Фильм должен иметь ID"
        assert created_movie["id"] > 0, "ID фильма должен быть положительным"
        assert created_movie["name"], "Название фильма не должно быть пустым"
        assert created_movie["price"] > 0, "Цена должна быть положительной"

        # Дополнительные проверки:
        assert created_movie["location"] in ["MSK", "SPB"], "Локация должна быть MSK или SPB"
        assert "genreId" in created_movie, "Должен быть genreId"
        assert created_movie["genreId"] >= 1, "genreId должен быть > 1"

    def test_get_movie_by_id(self, api_manager, created_movie):
        """
        Тест получения фильма по ID.
        """
        movie_id = created_movie["id"]

        # Получаем фильм по ID
        response = api_manager.movies_api.get_movies_by_id(movie_id)
        movie_data = response.json()

        assert response.status_code == 200
        assert movie_data["id"] == movie_id
        assert movie_data["name"] == created_movie["name"]

    def test_get_movies_with_filters(self, created_movie, superadmin_auth):
        """
        Тест фильтрации фильмов.
        Требование: "Как минимум 1 тест на проверку фильтров"
        """
        # Получаем все фильмы
        response_all = superadmin_auth.movies_api.get_movies()
        all_movies = response_all.json()

        # Фильтруем по локации созданного фильма
        location = created_movie["location"]
        response_filtered = superadmin_auth.movies_api.get_movies(
            params={"location": location}
        )
        filtered_movies = response_filtered.json()

        # Проверяем что фильтрация работает
        assert len(filtered_movies["movies"]) <= len(all_movies["movies"])


    def test_get_movies_with_filters_genreId(self, created_movie, superadmin_auth):
        """
        Тест фильтрации фильмов.
        Требование: "Как минимум 1 тест на проверку фильтров"
        """
        # Получаем все фильмы
        response_all = superadmin_auth.movies_api.get_movies()
        all_movies = response_all.json()

        # Фильтруем по локации созданного фильма
        genreId = created_movie["genreId"]
        response_filtered = superadmin_auth.movies_api.get_movies(
            params={"genreId": genreId}
        )
        filtered_movies = response_filtered.json()

        # Проверяем что фильтрация работает
        assert len(filtered_movies["movies"]) <= len(all_movies["movies"])

        for movie in filtered_movies["movies"]:
            assert movie["genreId"] == genreId, \
                f"Фильм {movie['id']} имеет genreId={movie['genreId']}, ожидался {genreId}"

    def test_patch_movies_by_id(self, created_movie, superadmin_auth, movie_update_data):
        """
        Тест Редактирование фильма по ID
        """
        movie_id = created_movie["id"]

        # Сохраняем оригинальные значения полей, которые НЕ должны меняться
        original_location = created_movie["location"]
        original_genreId = created_movie["genreId"]
        original_imageUrl = created_movie["imageUrl"]

        response = superadmin_auth.movies_api.patch_movies(
            movie_id=created_movie["id"],
            update_data=movie_update_data
        )

        # Проверяем
        assert response.status_code == 200
        updated_movie = response.json()

        # 1. Проверяем что ОБНОВЛЁННЫЕ поля изменились
        for field in movie_update_data:
            assert updated_movie[field] == movie_update_data[field], \
                f"Поле '{field}' не обновилось: " \
                f"ожидалось {movie_update_data[field]}, " \
                f"получено {updated_movie[field]}"

        # 2. Проверяем что НЕобновляемые поля остались прежними
        assert updated_movie["location"] == original_location, \
            f"Location не должен был меняться! " \
            f"Было: {original_location}, Стало: {updated_movie['location']}"

        assert updated_movie["genreId"] == original_genreId, \
            f"GenreId не должен был меняться! " \
            f"Было: {original_genreId}, Стало: {updated_movie['genreId']}"

        assert updated_movie["imageUrl"] == original_imageUrl, \
            f"ImageUrl не должен был меняться! " \
            f"Было: {original_imageUrl}, Стало: {updated_movie['imageUrl']}"

    def test_delete_method(self, created_movie, superadmin_auth):
        """
        ТЕСТ на удалени фильма
        """
        movie_id = created_movie["id"]

        response = superadmin_auth.movies_api.delete_movie(movie_id)
        assert response.status_code == 200

        get_response = superadmin_auth.movies_api.get_movies_by_id(
            movie_id=movie_id,
            expected_status=404
        )
        assert get_response.status_code == 404

    def test_created_unauthorized(self, unauth_api_manager, test_movie):
        """
        Попытка создать фильм без авторизации (должна быть 401401)
        """
        response = unauth_api_manager.movies_api.create_movie(
            test_movie,
            expected_status=401
        )
        assert response.status_code == 401

    def test_get_nonexistent_movie(self, superadmin_auth):
        """
        Получение несуществующего фильма (должен быть 404)
        """
        nonexistent_id = random.randint(999999, 9999999)

        response = superadmin_auth.movies_api.get_movies_by_id(
            movie_id=nonexistent_id,
            expected_status=404
        )
        assert response.status_code == 404, \
            f"Ожидался 404 для несуществующего ID {nonexistent_id}, получен {response.status_code}"

    def test_patch_nonexisten_movie(self, superadmin_auth, movie_update_data):
        """
         Обновление несуществующего фильма.
        """
        nonexistent_id = random.randint(999999, 9999999)

        response = superadmin_auth.movies_api.patch_movies(
            movie_id=nonexistent_id,
            update_data=movie_update_data,
            expected_status=404
        )

        assert response.status_code == 404

    def test_create_movie_forbidden_for_user_role(self, common_user, test_movie):
        response = common_user.api.movies_api.create_movie(
            test_movie,
            expected_status=403
        )

        assert response.status_code == 403, "У User не должно быть прав для создания фильма"

    def test_create_movie_allowed_for_admin_role(self, admin_user, test_movie):
        response = admin_user.api.movies_api.create_movie(
            test_movie,
            expected_status=201
        )

        assert response == 201, "Admin должен иметь права для создания фильма"

        movies_data = response.json()
        admin_user.api.movies_api.delete_movie(movies_data["id"])













