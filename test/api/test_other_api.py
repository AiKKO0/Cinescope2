from sqlalchemy.orm import Session
import pytest
import allure
from db_models.movie import AccountTransactionTemplate
from utils.data_generator import DataGenerator


@allure.epic("Тестирование транзакций")
@allure.feature("Тестирование транзакций между счетами")
class TestAccountTransactionTemplate:

    @allure.story("Тестирование транзакций")
    @allure.description("""
    Этот тест проверяет корректность перевода денег между двумя счетами.
    Шаги:
    1. Создание двух счетов: Stan и Bob.
    2. Перевод 200 единиц от Stan к Bob.
    3. Проверка изменения балансов.
    4. Очистка тестовых данных.
    """)
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.label("qa_name", "Ivan Ivan")
    @allure.title("Тест перевода денег между счетами 200 рублей")
    def test_accounts_transaction_template(self, db_session: Session):

        # Функция перевода денег (определена ДО использования)
        @allure.step("Функция перевода денег")
        @allure.description("""
            Функция выполняющая транзакцию, имитация вызова функции на стороне тестируемого сервиса
            """)
        def transfer_money(session, from_account, to_account, amount):
            with allure.step("Получаем счета"):
                from_acc = session.query(AccountTransactionTemplate).filter_by(user=from_account).one()
                to_acc = session.query(AccountTransactionTemplate).filter_by(user=to_account).one()

            with allure.step("Проверяем, что на счёте достаточно денег"):
                if from_acc.balance < amount:
                    raise ValueError("Недостаточно средств на счете")

            with allure.step("Выполняем перевод"):
                from_acc.balance -= amount
                to_acc.balance += amount

            with allure.step("Сохраняем изменения"):
                session.commit()

            return from_acc, to_acc

        # ====================================================================== ПОДГОТОВКА К ТЕСТУ
        with allure.step("Создание тестовых данных в базе данных: счета Stan и Bob"):
            stan = AccountTransactionTemplate(
                user=f"Stan_{DataGenerator.generate_random_int(10)}",
                balance=500
            )
            bob = AccountTransactionTemplate(
                user=f"Bob_{DataGenerator.generate_random_int(10)}",
                balance=1000
            )
            db_session.add_all([stan, bob])
            db_session.commit()

            # Сохраняем значения для проверок
            initial_stan_balance = stan.balance
            initial_bob_balance = bob.balance
            stan_user = stan.user
            bob_user = bob.user

        # ====================================================================== ТЕСТ
        with allure.step("Проверяем начальные балансы"):
            assert stan.balance == 500, f"Stan: ожидалось 500, получено {stan.balance}"
            assert bob.balance == 1000, f"Bob: ожидалось 1000, получено {bob.balance}"

        try:
            with allure.step("Выполняем перевод 200 единиц от Stan к Bob"):
                transfer_money(db_session, from_account=stan_user, to_account=bob_user, amount=200)

            with allure.step("Проверяем, что балансы изменились"):
                # Обновляем объекты из БД
                db_session.refresh(stan)
                db_session.refresh(bob)

                expected_stan = 500 - 200  # 300
                expected_bob = 1000 + 200  # 1200

                assert stan.balance == expected_stan, \
                    f"Stan: ожидалось {expected_stan}, получено {stan.balance}"
                assert bob.balance == expected_bob, \
                    f"Bob: ожидалось {expected_bob}, получено {bob.balance}"

        except Exception as e:
            with allure.step(f"ОШИБКА: {str(e)}"):
                db_session.rollback()
                pytest.fail(f"Ошибка при переводе денег: {e}")

        finally:
            with allure.step("Удаляем данные для тестирования из базы"):
                db_session.delete(stan)
                db_session.delete(bob)
                db_session.commit()
                print(f"✅ Тестовые данные удалены: {stan_user}, {bob_user}")






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

