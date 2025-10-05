#!/usr/bin/env python3
# -*- coding: utf-8 -*-


#Завдання 3 (купи/heap):
#Дано довжини кабелів. За раз можна з'єднати два кабелі; вартість = сума їх довжин.
#Потрібно мінімізувати сумарну вартість усіх з'єднань.

#Рішення: завжди з'єднувати ДВА НАЙКОРОТШІ (мін-купа)
#класична задача optimal merge pattern (аналог побудови дерева Хаффмана без ваг)

#Функція:
#- min_total_cost_cables(lengths) -> (total_cost, steps)
#де steps — список кроків [(a, b, a+b), ...] у порядку з'єднань

from __future__ import annotations
import heapq
from typing import Iterable, List, Tuple

def min_total_cost_cables(lengths: Iterable[int]) -> Tuple[int, List[Tuple[int, int, int]]]:
    # підготуємо мін-купу
    heap: List[int] = []
    for x in lengths:
        if x < 0:
            raise ValueError("Довжини кабелів мають бути невід'ємні.")
        heap.append(int(x))
    if not heap:
        return 0, []
    heapq.heapify(heap)

    total_cost = 0
    steps: List[Tuple[int, int, int]] = []

    #поки більше одного кабелю — об'єднуємо два найкоротші
    while len(heap) > 1:
        a = heapq.heappop(heap)
        b = heapq.heappop(heap)
        cost = a + b
        total_cost += cost
        steps.append((a, b, cost))
        heapq.heappush(heap, cost)

    return total_cost, steps