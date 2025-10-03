# tests/test_palindrome.py
import os
import sys
import pytest

# Додати src/ у шлях імпортів
ROOT = os.path.dirname(os.path.dirname(__file__))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from palindrome import is_palindrome  # noqa: E402


@pytest.mark.parametrize(
    "text,expected",
    [
        ("А роза упала на лапу Азора", True),
        ("Never odd or even", True),
        ("Was it a car or a cat I saw?", True),
        ("No lemon, no melon", True),
        ("Madam, I'm Adam", True),
        ("abba", True),
        ("abcba", True),
        ("abca", False),
        ("Hello, world!", False),
        ("", True),                      # порожній рядок трактуємо як паліндром
        ("   ", True),                   # тільки пробіли
        ("12321", True),                 # цифри
        ("1231", False),
    ],
)
def test_is_palindrome(text: str, expected: bool):
    assert is_palindrome(text) is expected