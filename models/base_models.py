from typing import Optional
import datetime
from typing import List
from pydantic import BaseModel, Field, field_validator
from constant.roles import Roles



class TestUser(BaseModel):
    email: str
    fullName: str
    password: str
    passwordRepeat: str = Field(..., min_length=1, max_length=20, description="passwordRepeat должен вполностью совпадать с полем password")
    roles: list[Roles] = [Roles.USER]
    verified: Optional[bool] = None
    banned: Optional[bool] = None

    @field_validator("passwordRepeat")
    def validate_password_repeat(cls, value: str, info) -> str:
        # Проверяем, совпадение паролей
        if "password" in info.data and value != info.data["password"]:
            raise ValueError("Пароли не совпадают")
        return value

    # Добавляем кастомный JSON-сериализатор для Enum
    class Config:
        json_encoders = {
            Roles: lambda v: v.value
        }


class RegisterUserResponse(BaseModel):
    id: str
    email: str = Field(pattern=r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", description="Email пользователя")
    fullName: str = Field(min_length=1, max_length=100, description="Полное имя пользователя")
    verified: bool
    banned: Optional[bool] = Field(default=False, description="Флаг бана")
    # roles: list[Roles] = [Roles.USER]
    roles: List[Roles]
    createdAt: str = Field(description="Дата и время создания пользователя в формате ISO 8601")

    @field_validator("createdAt")
    def validate_created_at_format(cls, value: str) -> str:
        # Валидатор для проверки формата даты и времени (ISO 8601).
        try:
            datetime.datetime.fromisoformat(value)
        except ValueError:
            raise ValueError("Некорректный формат даты и времени. Ожидается формат ISO 8601.")
        return value

class MoviesSchema(BaseModel):
    """
    Pydantic модель для валидации ответа API /movies
    """
    id: int = Field(..., gt=0, description="Уникальный идентификатор фильма")
    name: str = Field(..., min_length=1, max_length=255, description="Название фильма")
    price: float = Field(..., gt=0, description="Цена билета")
    location: str = Field(..., description="Локация показа (MSK или SPB)")
    genreId: int = Field(..., ge=1, alias="genreId", description="ID жанра")
    imageUrl: Optional[str] = Field(None, alias="imageUrl", description="URL постера")
    description: Optional[str] = Field(None, description="Описание фильма")
    published: Optional[bool] = Field(None, description="Опубликован ли фильм")

    class Config:
        # Разрешаем использовать alias (genreId вместо genre_id)
        populate_by_name = True

    @field_validator("location")
    def validate_location(cls, value: str) -> str:
        """Проверка допустимых локаций"""
        allowed = ["MSK", "SPB"]
        if value not in allowed:
            raise ValueError(f"Локация должна быть одной из: {allowed}")
        return value

class MoviesListResponse(BaseModel):
    """Pydantic модель для ответа GET /movies (список фильмов)"""
    movies: List[MoviesSchema] = Field(..., description="Список фильмов")
    total: Optional[int] = Field(None, description="Общее количество фильмов (может отсутствовать)")