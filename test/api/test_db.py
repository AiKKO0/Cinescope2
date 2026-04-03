from conftest import created_test_user


class TestDBUser:

    def test_db_requests(self, super_admin, db_helper, created_test_user):
        assert created_test_user == db_helper.get_user_by_id(created_test_user.id)
        assert db_helper.user_exists_by_email("api1@gmail.com")

    def test_db_create_user(self, db_helper, common_user):
        assert db_helper.user_exists_by_email(common_user.email)

    def test_db_create_existing_admin_user(self, db_helper, existing_admin_user):
        assert db_helper.user_exists_by_email(existing_admin_user.email)

    def test_db_delete_user(self, super_admin, db_helper, created_test_user):
        """Тест удаления пользователя из БД"""
        super_admin.api.user_api.delete_user(created_test_user.id, expected_status=200)

        assert not db_helper.user_exists_by_email(created_test_user.email), \
            f"Пользователь {created_test_user.email} не удлаён из БД"


class TestDBMovie:
    def test_db_deleted_movie_superadmin(self, super_admin, db_helper, created_movie):
        """Тест удаления фильма из БД"""
        movie_id = created_movie["id"]

        super_admin.api.movies_api.delete_movie(movie_id, expected_status=200)

        assert not db_helper.get_movie_by_id(movie_id)