import pytest
from models.base_models import RegisterUserResponse


class TestUser:
    def test_created_user(self, super_admin, creation_user_data):
        response = super_admin.api.user_api.create_user(user_data=creation_user_data, expected_status=201)
        response_data = response.json()
        created_user = RegisterUserResponse(**response_data)
        response_data = response.json()

        user_response = RegisterUserResponse(**response_data)

        assert user_response.email == creation_user_data.email
        assert user_response.fullName == creation_user_data.fullName

        # Правильное сравнение ролей (Enum vs строка)
        expected_roles = [role.value for role in creation_user_data.roles]  # Enum -> строки
        assert user_response.roles == expected_roles

        assert user_response.verified is True
        assert user_response.banned is False


    @pytest.mark.slow
    def test_get_user_by_locator(self, super_admin, creation_user_data):
        response = super_admin.api.user_api.create_user(user_data=creation_user_data, expected_status=201)
        response_data = response.json()

        created_user = RegisterUserResponse(**response.json())

        # Проверки создания
        assert created_user.email == creation_user_data.email
        assert created_user.fullName == creation_user_data.fullName
        assert created_user.verified is True

        # 2. Получаем пользователя по ID и валидируем
        response_by_id = super_admin.api.user_api.get_user(created_user.id)
        user_by_id = RegisterUserResponse(**response_by_id.json())

        # 3. Получаем пользователя по email и валидируем
        response_by_email = super_admin.api.user_api.get_user(created_user.email)
        user_by_email = RegisterUserResponse(**response_by_id.json())

        # 4. Сравниваем модели (или их словарные представления)
        assert user_by_id.model_dump() == user_by_email.model_dump(), \
            "Данные по ID и email должны совпадать"

        # 5. Проверяем что полученные данные совпадают с созданными
        assert user_by_id.email == creation_user_data.email
        assert user_by_id.fullName == creation_user_data.fullName
        assert user_by_id.verified is True
        assert user_by_id.banned is False

        # 6. Дополнительно: проверяем ID
        assert user_by_id.id == created_user.id
        assert user_by_email.id == created_user.id


    @pytest.mark.slow
    def test_get_user_by_id_common_user(self, common_user):
        response = common_user.api.user_api.get_user(
            user_locator=common_user.email,
            expected_status=403
        )


