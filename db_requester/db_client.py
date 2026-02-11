import os

from sqlalchemy import create_engine # функция для создания "движка" базы данных
from sqlalchemy.orm import sessionmaker # фабрика для создания сессий (подключений)
from resources.db_creds import MoviesDbCreds # - класс с учетными данными для подключения к БД

USERNAME = MoviesDbCreds.USERNAME
PASSWORD = MoviesDbCreds.PASSWORD
HOST = MoviesDbCreds.HOST
PORT = MoviesDbCreds.PORT
DATABASE_NAME = MoviesDbCreds.DATABASE_NAME

engine = create_engine(
    f"postgresql+psycopg2://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DATABASE_NAME}",
    echo=True, # True для отладки
)

#  создаем фабрику сессий
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db_session():
    """Создаём сессию БД"""
    return SessionLocal()

















