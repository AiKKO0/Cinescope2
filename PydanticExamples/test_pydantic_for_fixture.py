from pydantic import BaseModel, Field, model_validator, field_validator
from typing import List, Optional
from constant.roles import Roles
from venv import logger


class TestUser(BaseModel):
    email: str
    fullName: str = Field(min_length=1, max_length=50)
    password: str = Field(min_length=8, max_length=20)
    passwordRepeat: str = Field(min_length=8, max_length=20)
    roles: List[Roles]
    banned: Optional[bool] = Field(default=None, description="Может быть null от API")
    verified: Optional[bool] = True

    # 1. Валидация email (должен содержать @)
    @field_validator('email')
    def validate_email(cls, value: str) -> str:
        '''"Проверяем, что email содержит символ @'''
        if '@' not in value:
            raise ValueError('Email должен содержать символ "@"')
        return value

    # 2. Валидация пароля (Доп. ПРОВЕРКИ ДЛЯ ПАРОЛЯ)
    @field_validator('password')
    def validate_password(cls, value: str) -> str:
        """Дополнительная валидация пароля"""
        if len(value) < 8:
            raise ValueError("Пароль должен быть больше 8 символов")

        if not any(c.isalnum() for c in value):
            logger.warning("Пароль должен содержать заглавные буквы")
        if not any(c.isdigit() for c in value):
            logger.warning("Пароль не содержит цифр (рекомендация)")

        return value

    # 3 Cравнение паролей
    @model_validator(mode='after')
    def validate_passwords_match(self) -> 'TestUser':
        """Проверяем что пароли совпадают"""
        if self.password != self.passwordRepeat:
            raise ValueError("Пароли не совпадают")
        return self



def test_pydantic_model(test_user):

    logger.info(f"\n{test_user.email=} \n{test_user.fullName=} \n{test_user.password=} \n{test_user.passwordRepeat=} "
                f"\nroles={[r.value for r in test_user.roles]}")

    test_user_jsnon = test_user
    json_data = test_user_jsnon.model_dump_json(exclude_unset=True)
    print(f"\n Это JSON \n {json_data}")


def test_pydantic_model2(creation_user_data):

    logger.info(f"{creation_user_data.email=} \n{creation_user_data.fullName=} \n{creation_user_data.password=} \n{creation_user_data.passwordRepeat=} "
                f"\nroles={[r.value for r in creation_user_data.roles]} \n{creation_user_data.banned} \n{creation_user_data.verified}")

    user_model_jsnon = creation_user_data
    json_data = user_model_jsnon.model_dump_json()
    print(f"\n\n Вывод без exclude_unset=True  {json_data}")

def test_pydantic_validation_quick():
    """Короткие тесты Валидации"""
    print("\n" + "="*30)
    print("КОРОТКИЕ ТЕСТЫ ВАЛИДАЦИИ")
    print("\n" + "="*30)
    # Валидный тест
    good_data = {
        "email": "test@example.com",
        "fullName": "John",
        "password": "Password123",
        "passwordRepeat": "Password123",
        "roles": [Roles.USER]
    }

    try:
        TestUser(**good_data)
        print("Валидные данные")
    except:
        print("Должно было пройти!")

    # 2. Email без @
    print("\n" + "=" * 30)
    print("Валидация email без  '@'")
    print("\n" + "=" * 30)

    bad_data = {
        "email": "testexa212.com",
        "fullName": "John2",
        "password": "Password1234",
        "passwordRepeat": "Password1234",
        "roles": [Roles.USER]
    }
    try:
        TestUser(**bad_data)
    except ValueError as e:
        print(f"Ошибка: {e}")


    # 3 Короткий пароль
    short_password = {
        "email": "test@example.com",
        "fullName": "John",
        "password": "123",
        "passwordRepeat": "123",
        "roles": [Roles.ADMIN]
    }
    try:
        TestUser(**short_password)
    except ValueError as e:
        print(f"Ошибка: {e}")


    # 4 Разные пароли
    diff_password = {
            "email": "test@example.com",
            "fullName": "John",
            "password": "12321Qwery12",
            "passwordRepeat": "12321Qwery",
            "roles": [Roles.ADMIN]
    }

    try:
        TestUser(**diff_password)
    except ValueError as e:
        print(f"Ошибка: {e}")



