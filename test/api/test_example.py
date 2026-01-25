import pytest


@pytest.mark.parametrize("a,b,c", [(1, 2, 3), (4, 5, "t")])
def test1(a, b, c):
    print(a, b, c)


def test2():
    print("Test2")
