from __future__ import annotations
from dataclasses import dataclass, field
from queue import Queue, Empty
from time import sleep, time
import itertools
import random


@dataclass
class Request:
    id: int
    payload: str
    created_at: float = field(default_factory=time)


class ServiceCenter:
    """Симулятор сервісного центру з чергою заявок."""

    def __init__(self) -> None:
        self.queue: Queue[Request] = Queue()
        self._id_counter = itertools.count(1)

    # === generate_request() ===
    def generate_request(self, payload: str | None = None) -> Request:
        """Створює нову заявку і додає її до черги."""
        req = Request(
            id=next(self._id_counter),
            payload=payload or f"issue-{random.randint(1000, 9999)}",
        )
        self.queue.put(req)
        print(f"[GEN] додано заявку #{req.id} (payload={req.payload}) — у черзі: {self.queue.qsize()}")
        return req

    # === process_request() ===
    def process_request(self) -> None:
        """Обробляє 1 заявку з черги, якщо вона є."""
        try:
            req = self.queue.get_nowait()
        except Empty:
            print("[PROC] черга порожня — немає що обробляти")
            return
        # тут могла бути реальна логіка обробки
        sleep(0.1)
        print(f"[PROC] опрацьовано заявку #{req.id} (payload={req.payload}) — залишилось у черзі: {self.queue.qsize()}")


def demo_loop(ticks: int = 30, gen_minmax: tuple[int, int] = (0, 3), seed: int | None = 42) -> None:
    """Головний цикл симуляції: генерація та обробка заявок.
    - ticks: кількість ітерацій;
    - gen_minmax: у кожній ітерації додаємо випадково N заявок у [min, max);
    - seed: для відтворюваності.
    """
    if seed is not None:
        random.seed(seed)

    sc = ServiceCenter()
    print("\n=== СТАРТ СИМУЛЯЦІЇ СЕРВІСНОГО ЦЕНТРУ ===")
    for _ in range(ticks):
        to_generate = random.randrange(*gen_minmax)
        for _ in range(to_generate):
            sc.generate_request()
        sc.process_request()
        sleep(0.2)
    print("=== КІНЕЦЬ СИМУЛЯЦІЇ ===\n")


if __name__ == "__main__":
    demo_loop()