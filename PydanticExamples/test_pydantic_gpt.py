import pytest
import json
from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from constant.roles import Roles


class TestPydanticForFixture(BaseModel):
    """Модель для практической части с фикстурами из conftest"""
    email: str
    fullName: str
    password: str
    passwordRepeat: str
    roles: List[Roles]  # Список Enum
    banned: Optional[bool] = False
    verified: Optional[bool] = True

    # ОБЯЗАТЕЛЬНО для работы со строками из ваших фикстур!
    # model_config = ConfigDict(
    #     use_enum_values=True,
    #     json_encoders={
    #         Roles: lambda v: v.value
    #     }
    # )


def test_practical_part_with_conftest_fixtures(test_user, creation_user_data):
    """
    Практическая часть с использованием существующих фикстур
    1. Модель с опциональными полями ✅
    2. Поле roles как список Enum ✅
    3. Прогон обеих фикстур через валидацию ✅
    4. JSON анализ с exclude_unset=True и без ✅
    """

    print("\n" + "=" * 60)
    print("ПРАКТИЧЕСКАЯ ЧАСТЬ С ФИКСТУРАМИ ИЗ conftest.py")
    print("=" * 60)

    # Пункт 3: Валидация обеих фикстур
    print("\n3. ВАЛИДАЦИЯ ФИКСТУР:")

    # test_user
    print(f"\na) Фикстура test_user:")
    model1 = TestPydanticForFixture(**test_user)
    print(f"   ✅ Валидация пройдена")
    print(f"   banned (дефолт): {model1.banned}")
    print(f"   verified (дефолт): {model1.verified}")

    # creation_user_data
    print(f"\nb) Фикстура creation_user_data:")
    model2 = TestPydanticForFixture(**creation_user_data)
    print(f"   ✅ Валидация пройдена")
    print(f"   banned (явно): {model2.banned}")
    print(f"   verified (явно): {model2.verified}")

    # Пункт 4: JSON анализ
    print("\n4. JSON АНАЛИЗ:")

    print(f"\na) test_user с exclude_unset=True:")
    json1_exclude = model1.model_dump_json(exclude_unset=True)
    parsed1_exclude = json.loads(json1_exclude)
    print(f"   JSON: {json1_exclude}")
    print(f"   Поля: {list(parsed1_exclude.keys())}")

    print(f"\nb) test_user без exclude_unset=True:")
    json1_full = model1.model_dump_json()
    parsed1_full = json.loads(json1_full)
    print(f"   JSON: {json1_full}")
    print(f"   Поля: {list(parsed1_full.keys())}")

    print(f"\nв) creation_user_data без exclude_unset=True:")
    json2_full = model2.model_dump_json()
    parsed2_full = json.loads(json2_full)
    print(f"   JSON: {json2_full}")

    print(f"\nг) creation_user_data с exclude_unset=True:")
    json2_exclude = model2.model_dump_json(exclude_unset=True)
    parsed2_exclude = json.loads(json2_exclude)
    print(f"   JSON: {json2_exclude}")

    # Анализ
    print(f"\n🔍 АНАЛИЗ РАЗНИЦЫ exclude_unset=True:")
    print(f"   test_user: {set(parsed1_full.keys()) - set(parsed1_exclude.keys())}")
    print(f"   creation_user_data: {set(parsed2_full.keys()) - set(parsed2_exclude.keys())}")

    # Логирование результата
    print(f"\n📊 ИТОГ ПРАКТИЧЕСКОЙ ЧАСТИ:")
    print(f"✅ 1. Модель с опциональными полями banned и verified")
    print(f"✅ 2. Поле roles как список Enum Roles")
    print(f"✅ 3. Обе фикстуры прошли валидацию")
    print(f"✅ 4. JSON проанализирован с exclude_unset=True и без него")

    # Возвращаем True для успешного теста
    return True