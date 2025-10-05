#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#Єдиний вхід для швидкого запуску (без обов'язкових аргументів).
#- Демонструє Завдання 1–3 з готовими прикладами.
#- За бажанням можна передати свої числа через CLI:
#  python3 main.py --bst 7 3 9 1 5 8 10 --cables 8 4 6 12

from __future__ import annotations
import argparse
from typing import List

from bst import build_bst, find_min_value, sum_values
from heap_cables import min_total_cost_cables


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="HW-07/08 demos: BST/AVL & heap (cables).")
    ap.add_argument("--bst", nargs="*", type=int, help="Значення для побудови BST (напр. --bst 7 3 9 1 5 8 10)")
    ap.add_argument("--cables", nargs="*", type=int, help="Довжини кабелів (напр. --cables 8 4 6 12)")
    return ap.parse_args()


def demo_bst(values: List[int]) -> None:
    print("Завдання 1–2: BST")
    print(f"[дані] BST values: {values}")
    root = build_bst(values)

    #Завдання 1: мінімальне значення
    min_val = find_min_value(root)
    print(f"[min] Найменше значення у BST: {min_val}")

    #Завдання 2: сума значень
    total = sum_values(root)
    print(f"[sum] Сума всіх значень у BST: {total}\n")


def demo_heap_cables(lengths: List[int]) -> None:
    print("Завдання 3: Купа (мін. вартість з'єднання кабелів)")
    print(f"[дані] Кабелі: {lengths}")
    total_cost, steps = min_total_cost_cables(lengths)
    print("[кроки] порядок з'єднання (a + b -> cost):")
    for i, (a, b, c) in enumerate(steps, 1):
        print(f"  {i:>2}: {a} + {b} -> {c}")
    print(f"[result] Мінімальна сумарна вартість: {total_cost}\n")

def main() -> None:
    args = parse_args()

    # Значення за замовчуванням, якщо аргументи не передані
    bst_values = args.bst if args.bst else [7, 3, 9, 1, 5, 8, 10]
    cables = args.cables if args.cables else [8, 4, 6, 12]

    demo_bst(bst_values)
    demo_heap_cables(cables)

if __name__ == "__main__":
    main()