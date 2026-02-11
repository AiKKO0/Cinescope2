from sqlalchemy.orm import Session
import pytest

from db_models.movie import AccountTransactionTemplate
from utils.data_generator import DataGenerator


def test_accounts_transaction_template(db_session: Session):
    # ====================================================================== Подготовка к тесту
    # Создаем новые записи в базе данных (чтоб точно быть уверенными что в базе присутствуют данные для тестирования)
    '''
    Переделайте test_accounts_transaction_template так чтоб у Стена не было достаточно денег для перевода Бобу и отвалидируйте
    что результат в базе не изменился и деньги остались на месте у каждого.
    '''
    stan = AccountTransactionTemplate(user=f"Stan_{DataGenerator.generate_random_int(10)}", balance=500)
    bob = AccountTransactionTemplate(user=f"Bob_{DataGenerator.generate_random_int(10)}", balance=1000)

    # Добавляем записи в сессию
    db_session.add_all([stan, bob])
    # Фиксируем изменения в базе данных
    db_session.commit()

    def transfer_money(session, from_account, to_account, amount):
        # пример функции выполняющей транзакцию
        # представим что она написана на стороне тестируемого сервиса
        # и вызывая метод transfer_money, мы какбудтобы делем запрос в api_manager.movies_api.transfer_money
        """
        Переводит деньги с одного счета на другой.
        :param session: Сессия SQLAlchemy.
        :param from_account_id: ID счета, с которого списываются деньги.
        :param to_account_id: ID счета, на который зачисляются деньги.
        :param amount: Сумма перевода.
        """
        # Получаем счета
        from_account = session.query(AccountTransactionTemplate).filter_by(user=from_account).one()
        to_account = session.query(AccountTransactionTemplate).filter_by(user=to_account).one()

        # Проверяем, что на счете достаточно средств
        if from_account.balance < amount:
            raise ValueError("Недостаточно средств на счете")

        # Выполняем перевод
        from_account.balance -= amount
        to_account.balance += amount

        # Сохраняем изменения
        session.commit()

    # ====================================================================== Тест
    # Проверяем начальные балансы
    assert stan.balance == 500
    assert bob.balance == 1000

    try:
        # Выполняем перевод 200 единиц от stan к bob
        transfer_money(db_session, from_account=stan.user, to_account=bob.user, amount=1000)
        pytest.fail("❌ Ожидалась ошибка 'Недостаточно средств', но перевод прошел успешно!")

        # Проверяем, что балансы изменились

    except ValueError as e:
        print(f"✅ Ожидаемая ошибка: {e}")
        # Если произошла ошибка, откатываем транзакцию

        db_session.rollback()  # откат всех введеных нами изменений

        # Обновляем данные из БД
        db_session.refresh(stan)
        db_session.refresh(bob)

        # Проверяем, что балансы изменились
        assert stan.balance == 500
        assert bob.balance == 1000

        print(f"✅ Балансы не изменились: Stan = {stan.balance}, Bob = {bob.balance}")

    except Exception as e:
        # ❌ Неожиданная ошибка - тест падает
        pytest.fail(f"❌ Неожиданная ошибка: {type(e).__name__}: {e}")

    finally:
        # Удаляем данные для тестирования из базы
        db_session.delete(stan)
        db_session.delete(bob)
        # Фиксируем изменения в базе данных
        db_session.commit()

