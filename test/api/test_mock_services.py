from pytest_mock import mocker
from unittest.mock import Mock
import pytest
import datetime
import pytz
import requests
from constants import BASE_URL, HEADERS, REGISTER_ENDPOINT, MOVIES_ENDPOINT
from custom_requester.custom_requester import CustomRequester
from api_manager import ApiManager
from constant.roles import Enum
from models.base_models import BaseModel

from pydantic import BaseModel, Field
from datetime import datetime

# Модель Pydantic для ответа сервера worldclockapi
class WorldClockResponse(BaseModel):
    # id: str = Field(alias="$id")  # Используем алиас для поля "$id"
    # currentDateTime: str
    utc_time: str # / datetime str
    # utcOffset: str
    # isDayLightSavingsTime: bool
    # dayOfTheWeek: str
    # timeZoneName: str
    # currentFileTime: int
    # ordinalDate: str
    # serviceResponse: None

    class Config:
        # Разрешаем использование алиасов при парсинге JSON
        allow_population_by_field_name = True

# Модель для запроса к сервису TodayIsHoliday
class DateTimeRequest(BaseModel):
    currentDateTime: str  # Формат: "2025-02-13T21:43Z"

# Модель для ответа от сервиса TodayIsHoliday
class WhatIsTodayResponse(BaseModel):
    message: str

#Функция выолняющая запрос в сервис worldclockapi для получения текущей даты
def get_worldclockap_time() -> WorldClockResponse:
    # Выполняем GET-запрос https://timeapi.io/api/v1/time/current/utc / http://worldclockapi.com/api/json/utc/now
    response = requests.get("https://timeapi.io/api/v1/time/current/utc") # Запрос в реальный сервис
    # Проверяем статус ответа
    assert response.status_code == 200, "Удаленный сервис недоступен"
    # Парсим JSON-ответ с использованием Pydantic модели
    return  WorldClockResponse(**response.json())

def test_get_worldclockap_time():
    return get_worldclockap_time()



class TestTodayIsHolidayServiceAPI:
    # worldclockap
    def test_worldclockap(self):  # проверка работоспособности сервиса worldclockap
        world_clock_response = get_worldclockap_time()

        # Выводим текущую дату и время
        current_date_time = world_clock_response.utc_time
        print(f"Текущая дата и время: {current_date_time=}")

        assert current_date_time == datetime.now(pytz.utc), "Дата не совпадает"

    def test_what_is_today(self):  # проверка работоспособности Fake сервиса what_is_today
        # Запрашиваем текущее время у сервиса worldclockap
        world_clock_response = get_worldclockap_time()

        what_is_today_response = requests.post("http://127.0.0.1:16002/what_is_today",
                                               data=DateTimeRequest(
                                                   currentDateTime=world_clock_response.utc_time).model_dump_json()
                                               )

        # Проверяем статус ответа от тестируемогосервиса
        assert what_is_today_response.status_code == 200, "Удаленный сервис недоступен"
        # Парсим JSON-ответ от тестируемого сервиса с использованием Pydantic модели
        what_is_today_data = WhatIsTodayResponse(**what_is_today_response.json())
        # Проводим валидацию ответа тестируемого сервиса
        assert what_is_today_data.message == "Сегодня нет праздников в России.", "Сегодня нет праздника!"

    def test_datetime(self):
        # Запрашиваем текущее время у сервиса worldclockap
        world_clock_response = get_worldclockap_time()

        # Получаем дату и ОБРЕЗАЕМ миллисекунды и секунды
        full_datetime = world_clock_response.utc_time  # "2026-02-13T14:41:20.6942992Z"

        # Оставляем только до минут: "2026-02-13T14:41Z"
        # Берем первые 16 символов (2026-02-13T14:41) и добавляем Z
        formatted_datetime = full_datetime[:16] + 'Z'

        print(f"Исходная дата: {full_datetime}")
        print(f"Отправляем дату: {formatted_datetime}")

        # ВАЖНО: используем json=, а не data=
        what_is_today_response = requests.post(
            "http://127.0.0.1:16002/what_is_today",
            json={"currentDateTime": formatted_datetime}  # Прямая передача словаря
            # или через модель:
            # json=DateTimeRequest(currentDateTime=formatted_datetime).model_dump()
        )

        print(f"Статус ответа: {what_is_today_response.status_code}")
        print(f"Тело ответа: {what_is_today_response.text}")

        assert what_is_today_response.status_code == 200, f"Ошибка: {what_is_today_response.text}"

        what_is_today_data = WhatIsTodayResponse(**what_is_today_response.json())
        assert what_is_today_data.message == "Сегодня нет праздников в России.", \
            f"Получено: {what_is_today_data.message}"

        # Запрашиваем текущее время у сервиса worldclockap
        world_clock_response = get_worldclockap_time()

        # Получаем дату и ОБРЕЗАЕМ миллисекунды и секунды
        full_datetime = world_clock_response.utc_time  # "2026-02-13T14:41:20.6942992Z"

        # Оставляем только до минут: "2026-02-13T14:41Z"
        # Берем первые 16 символов (2026-02-13T14:41) и добавляем Z
        formatted_datetime = full_datetime[:16] + 'Z'

        print(f"Исходная дата: {full_datetime}")
        print(f"Отправляем дату: {formatted_datetime}")

        # ВАЖНО: используем json=, а не data=
        what_is_today_response = requests.post(
            "http://127.0.0.1:16002/what_is_today",
            json={"currentDateTime": formatted_datetime}  # Прямая передача словаря
            # или через модель:
            # json=DateTimeRequest(currentDateTime=formatted_datetime).model_dump()
        )

        print(f"Статус ответа: {what_is_today_response.status_code}")
        print(f"Тело ответа: {what_is_today_response.text}")

        assert what_is_today_response.status_code == 200, f"Ошибка: {what_is_today_response.text}"

        what_is_today_data = WhatIsTodayResponse(**what_is_today_response.json())
        assert what_is_today_data.message == "Сегодня нет праздников в России.", \
            f"Получено: {what_is_today_data.message}"


    def test_what_is_today_BY_MOCK(self, mocker):
        # Создаем мок для функции get_worldclockap_time
        mocker.patch(
            "test_mock_services.get_worldclockap_time",
            # Указываем путь к функции в нашем модуле (формат файл.класс.метод)
            # либо имя_файла.имя_метода если он находится в этом же файле
            return_value=Mock(
                currentDateTime="2025-01-01T00:00Z"  # Фиксированная дата для возврата из мок функции "1 января"
            )
        )

        # Выполним тело предыдущего теста еще раз
        world_clock_response = get_worldclockap_time()  # = "2025-01-01T00:00Z"

        what_is_today_response = requests.post("http://127.0.0.1:16002/what_is_today",
                                               data=DateTimeRequest(
                                                   currentDateTime=world_clock_response.currentDateTime).model_dump_json()
                                               )

        # Проверяем статус ответа от тестируемого сервиса
        assert what_is_today_response.status_code == 200, "Удаленный сервис недоступен"
        # Парсим JSON-ответ от тестируемого сервиса с использованием Pydantic модели
        what_is_today_data = WhatIsTodayResponse(**what_is_today_response.json())

        assert what_is_today_data.message == "Новый год", "ДОЛЖЕН БЫТЬ НОВЫЙ ГОД!"
