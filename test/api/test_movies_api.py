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

    def test_create_movie_directly(self, superadmin_auth, test_movie):
        """
        Тест прямого создания фильма (без фикстуры).
        """
        # Создаём фильм вручную
        response = superadmin_auth.movies_api.create_movie(test_movie)

        # Проверяем ответ
        assert response.status_code == 201
        movie_data = response.json()

        # Проверяем данные
        assert movie_data["name"] == test_movie["name"]
        assert movie_data["location"] == test_movie["location"]

        # Очистка
        movie_id = movie_data["id"]
        superadmin_auth.movies_api.delete_movie(movie_id)