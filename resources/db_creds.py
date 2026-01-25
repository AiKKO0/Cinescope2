import os
from dotenv import load_dotenv

def load_db_credentials():
    """
    Загружаем credentials для БД из .env файла
    """
    # Загружаем переменные из .env файла
    load_dotenv()

    credentials = {
        "host": os.getenv("HOST"),
        'port': os.getenv('PORT'),
        'database': os.getenv('DBNAME'),
        'user': os.getenv('USER'),
        'password': os.getenv('PASSWORD')
    }

    # Проверяем, что все переменные загружены
    for key, value in credentials.items():
        if value is None:
            raise ValueError(f"Переменная окружения {key} не найдена в .env файле")

    return credentials

