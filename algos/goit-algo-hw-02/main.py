from src.request_queue import demo_loop
from src.palindrome import is_palindrome

if __name__ == "__main__": 
    # Демо Завдання 1
    demo_loop(ticks=20, gen_minmax=(0, 3), seed=7)

    # Демо Завдання 2
    samples = [
        "А роза упала на лапу Азора",
        "Never odd or even",
        "Was it a car or a cat I saw?",
        "Hello, world!",
    ]
    for s in samples:
        print(f"'{s}' -> {is_palindrome(s)}")
