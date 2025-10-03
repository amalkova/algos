from collections import deque
import sys


def _normalize(s: str) -> str:
    """Лишаємо тільки букви/цифри, знижуємо регістр."""
    return "".join(ch.casefold() for ch in s if ch.isalnum())


def is_palindrome(text: str) -> bool:
    """Перевірка паліндрома через двосторонню чергу (deque)."""
    norm = _normalize(text)
    dq = deque(norm)
    while len(dq) > 1:
        if dq.popleft() != dq.pop():
            return False
    return True


def cli() -> None:
    if len(sys.argv) == 1:
        print('Використання: python src/palindrome.py "рядок"')
        return
    text = " ".join(sys.argv[1:])
    print(f"Текст: {text}")
    print("Паліндром" if is_palindrome(text) else "Не паліндром")


if __name__ == "__main__":
    cli()
