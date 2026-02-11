from sqlalchemy import Column, String, Boolean, DateTime, Integer, Float, ForeignKey
from sqlalchemy.orm import declarative_base
from typing import Dict, Any


Base = declarative_base()

class MovieDBModel(Base):
    __tablename__ = 'movies'

    id = Column(Integer, primary_key=True)
    name = Column(String)  # text в БД
    price = Column(Integer) # int4 В БД
    director = Column(String) # text в БД
    image_url = Column(String) # text в БД
    location = Column(String) # int4 В БД
    published = Column(Boolean) # bool в БД
    rating = Column(Float) # float8 в БД
    genre_id = Column(Integer) # int4 В БД
    created_at = Column(DateTime) # timestamp в БД

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь"""
        return {
            'id': self.id,
            'name': self.name,
            'price': self.price,
            'director': self.director,
            'image_url': self.image_url,
            'location': self.location,
            'published': self.published,
            'rating': self.rating,
            'genre_id': self.genre_id,
            'created_at': self.created_at
        }

    def __repr__(self) -> str:
        return f"<Movie id='{self.id}', name='{self.name}', price='{self.price}'>"

class AccountTransactionTemplate(Base):
    __tablename__ = 'accounts_transaction_template'
    user = Column(String, primary_key=True)
    balance = Column(Integer, nullable=False)
