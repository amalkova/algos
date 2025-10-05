#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#Завдання 6. Вибір їжі з максимальною калорійністю в межах бюджету.

#Дано:
#items = {
#  "pizza":     {"cost": 50, "calories": 300},
#  "hamburger": {"cost": 40, "calories": 250},
#  "hot-dog":   {"cost": 30, "calories": 200},
#  "pepsi":     {"cost": 10, "calories": 100},
#  "cola":      {"cost": 15, "calories": 220},
#  "potato":    {"cost": 25, "calories": 350},
#}

#Потрібно:
#- ЖАДІБНИЙ (greedy): максимізує співвідношення calories/cost, поки не перевищимо бюджет.
#- ДИНАМІЧНЕ ПРОГРАМУВАННЯ (DP, 0/1 knapsack): знаходить оптимальний набір під бюджет.

#Запуск прикладів:
#    python3 task6_food_selection.py --budget 100 --mode greedy
#    python3 task6_food_selection.py --budget 100 --mode dp
#    python3 task6_food_selection.py --budget 100 --mode both

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Tuple, Iterable
import argparse
import json
import sys

#Вхідні дані за замовчуванням

DEFAULT_ITEMS: Dict[str, Dict[str, int]] = {
    "pizza":     {"cost": 50, "calories": 300},
    "hamburger": {"cost": 40, "calories": 250},
    "hot-dog":   {"cost": 30, "calories": 200},
    "pepsi":     {"cost": 10, "calories": 100},
    "cola":      {"cost": 15, "calories": 220},
    "potato":    {"cost": 25, "calories": 350},
}

#Допоміжні типи

@dataclass(frozen=True)
class Item:
    name: str
    cost: int
    calories: int

    @property
    def ratio(self) -> float:
        return self.calories / self.cost if self.cost > 0 else 0.0

def _normalize_items(items: Dict[str, Dict[str, int]]) -> List[Item]:
    out: List[Item] = []
    for name, props in items.items():
        cost = int(props["cost"])
        cal = int(props["calories"])
        if cost < 0 or cal < 0:
            raise ValueError(f"Вартість/калорійність не може бути від'ємною: {name} -> {props}")
        out.append(Item(name=name, cost=cost, calories=cal))
    return out

#GREEDY

def greedy_algorithm(items: Dict[str, Dict[str, int]], budget: int) -> Tuple[List[Item], int, int]:
    
    #Жадібно обираємо за спаданням ratio = calories/cost, поки вистачає бюджету.
    #Повертає (список_вибраних, total_cost, total_calories).
    #Зауваження: це евристика і НЕ гарантує оптимум у 0/1 постановці.
    
    #budget = int(budget)
    #if budget < 0:
    #    raise ValueError("Бюджет має бути невід'ємним цілим числом")

    items_norm = sorted(_normalize_items(items), key=lambda it: it.ratio, reverse=True)
    chosen: List[Item] = []
    total_cost = 0
    total_cal = 0

    for it in items_norm:
        if total_cost + it.cost <= budget:
            chosen.append(it)
            total_cost += it.cost
            total_cal += it.calories

    return chosen, total_cost, total_cal

#DP (0/1)

def dynamic_programming(items: Dict[str, Dict[str, int]], budget: int) -> Tuple[List[Item], int, int]:
    
    #Класичний 0/1 knapsack: максимізуємо калорії при сумарній вартості ≤ budget.
    #Повертає (список_вибраних, total_cost, total_calories).
    #Складність: O(n * budget) пам'яті/часу, де n — кількість страв.
    
    budget = int(budget)
    if budget < 0:
        raise ValueError("Бюджет має бути невід'ємним цілим числом")

    items_norm = _normalize_items(items)
    n = len(items_norm)

    #dp[i][w] = макс. калорії зі страв перших i при бюджеті w
    dp = [[0] * (budget + 1) for _ in range(n + 1)]

    for i in range(1, n + 1):
        it = items_norm[i - 1]
        for w in range(budget + 1):
            dp[i][w] = dp[i - 1][w]  # не беремо it
            if it.cost <= w:
                dp[i][w] = max(dp[i][w], dp[i - 1][w - it.cost] + it.calories)

    #Відновимо розв'язок
    w = budget
    chosen: List[Item] = []
    for i in range(n, 0, -1):
        if dp[i][w] != dp[i - 1][w]:  # предмет узяли
            it = items_norm[i - 1]
            chosen.append(it)
            w -= it.cost
    chosen.reverse()

    total_cost = sum(it.cost for it in chosen)
    total_cal = sum(it.calories for it in chosen)
    return chosen, total_cost, total_cal

#Форматований друк

def _format_table(items: Iterable[Item]) -> str:
    rows = [("Назва", "Вартість", "Калорії", "Cal/Cost")]
    for it in items:
        rows.append((it.name, str(it.cost), str(it.calories), f"{it.ratio:.2f}"))
    # ширини колонок
    widths = [max(len(row[i]) for row in rows) for i in range(4)]
    lines = []
    for idx, row in enumerate(rows):
        line = "  ".join(row[i].ljust(widths[i]) for i in range(4))
        lines.append(line)
        if idx == 0:
            lines.append("-" * len(line))
    return "\n".join(lines)

def _print_solution(title: str, chosen: List[Item], total_cost: int, total_cal: int, budget: int) -> None:
    print(f"\n=== {title} ===")
    if not chosen:
        print("Нічого не обрано (або бюджет занадто малий).")
        return
    print(_format_table(chosen))
    print("-" * 48)
    print(f"Σ Вартість:  {total_cost}  (бюджет = {budget})")
    print(f"Σ Калорії:   {total_cal}")

#CLI

def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Вибір їжі під бюджет: greedy vs DP")
    ap.add_argument("--budget", type=int, required=True, help="Заданий бюджет (ціле число)")
    ap.add_argument(
        "--mode",
        choices=["greedy", "dp", "both"],
        default="both",
        help="Який метод запустити"
    )
    ap.add_argument(
        "--items-json",
        type=str,
        help="JSON-файл з об'єктом виду {name: {cost: int, calories: int}, ...}. Якщо не задано — використовується вбудований набір."
    )
    return ap.parse_args()

def load_items_from_json(path: str) -> Dict[str, Dict[str, int]]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    # валідація полів
    for k, v in data.items():
        if not isinstance(v, dict) or "cost" not in v or "calories" not in v:
            raise ValueError(f"Неправильний формат елемента '{k}': {v}")
    return data

def main() -> None:
    args = parse_args()
    if args.items_json:
        try:
            items = load_items_from_json(args.items_json)
        except Exception as e:
            print(f"[ERROR] Не вдалося прочитати {args.items_json}: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        items = DEFAULT_ITEMS

    budget = args.budget

    if args.mode in ("greedy", "both"):
        chosen, total_cost, total_cal = greedy_algorithm(items, budget)
        _print_solution("Жадібний алгоритм (ratio calories/cost)", chosen, total_cost, total_cal, budget)

    if args.mode in ("dp", "both"):
        chosen, total_cost, total_cal = dynamic_programming(items, budget)
        _print_solution("Динамічне програмування (0/1 knapsack)", chosen, total_cost, total_cal, budget)

if __name__ == "__main__":
    main()