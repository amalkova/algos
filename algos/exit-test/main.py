#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#GOIT Final Project — launcher

#Інтерактивне меню для запуску завдань:
#  1) Однозв’язний список: reverse, merge-sort, merge two sorted
#  2) Рекурсія: фрактал «дерево Піфагора» (PNG/показ)
#  3) Дейкстра з бінарною купою (демо-граф)
#  4) Візуалізація бінарної купи (PNG/показ)
#  5) Візуалізація обходів BFS/DFS (PNG/показ) — без рекурсії
#  6) Вибір їжі: greedy vs DP (0/1 knapsack)
#  7) Монте-Карло: кидки двох кубиків (таблиця, CSV/PNG опційно)

#Порада: встановити залежності для візуалізацій:
#    pip install matplotlib networkx numpy
#(для інших — стандартної бібліотеки достатньо)

from __future__ import annotations
import os
from pathlib import Path

#Імпорти з файлів завдань
#Task 1
import task1_linked_list as t1

#Task 2
from task2_pythagoras_tree import draw_pythagoras_tree

#Task 3
from task3_dijkstra_heap import make_graph, dijkstra_heap, reconstruct_path, DEMO_EDGES

#Task 4
from task4_heap_visualize import build_heap_tree, draw_tree as draw_heap_tree

#Task 5
from task5_tree_traversal_viz import (
    build_tree_from_array, traverse_bfs, traverse_dfs,
    colorize_by_order, draw_tree as draw_traversal_tree,
    parse_tree_string
)

#Task 6
from task6_food_selection import greedy_algorithm, dynamic_programming, DEFAULT_ITEMS, _format_table as fmt_food_table

#Task 7
from task7_dice_monte_carlo import (
    simulate_dice_rolls, frequencies_to_probs, theoretical_probs,
    format_table as fmt_dice_table, overall_errors, plot_probs
)
from collections import Counter

OUTDIR = Path("out")

#helpers (input)

def ask(prompt: str, default: str | None = None) -> str:
    s = input(f"{prompt}" + (f" [{default}]" if default is not None else "") + ": ").strip()
    return s if s else (default if default is not None else "")

def ask_int(prompt: str, default: int | None = None, min_val: int | None = None, max_val: int | None = None) -> int:
    while True:
        s = ask(prompt, str(default) if default is not None else None)
        try:
            v = int(s)
            if min_val is not None and v < min_val:
                print(f"  Значення має бути ≥ {min_val}")
                continue
            if max_val is not None and v > max_val:
                print(f"  Значення має бути ≤ {max_val}")
                continue
            return v
        except Exception:
            print("  Введи ціле число.")

def ask_float(prompt: str, default: float | None = None, min_val: float | None = None, max_val: float | None = None) -> float:
    while True:
        s = ask(prompt, str(default) if default is not None else None)
        try:
            v = float(s)
            if min_val is not None and v < min_val:
                print(f"  Значення має бути ≥ {min_val}")
                continue
            if max_val is not None and v > max_val:
                print(f"  Значення має бути ≤ {max_val}")
                continue
            return v
        except Exception:
            print("  Введи число.")

def ask_bool(prompt: str, default: bool = False) -> bool:
    s = ask(prompt + " (y/n)", "y" if default else "n").lower()
    return s in ("y", "yes", "д", "так", "t", "true", "1")

def ensure_outdir() -> Path:
    OUTDIR.mkdir(parents=True, exist_ok=True)
    return OUTDIR

#Task 1 runner

def run_task1() -> None:
    print("\nЗавдання 1: Однозв’язний список")
    data = [7, 3, 9, 1, 5, 8, 10]
    head = t1.build_list(data)
    print("Початковий:", t1.to_pylist(head))

    rev = t1.reverse_inplace(head)
    print("Реверс:", t1.to_pylist(rev))

    head = t1.reverse_inplace(rev)  # повернули до оригінального
    sorted_head = t1.merge_sort(head)
    print("Після merge-sort:", t1.to_pylist(sorted_head))

    a = t1.build_list([1, 4, 6, 9])
    b = t1.build_list([0, 2, 3, 7, 10])
    merged = t1.merge_two_sorted(a, b)
    print("Злиття двох відсортованих:", t1.to_pylist(merged))

#Task 2 runner

def run_task2() -> None:
    print("\nЗавдання 2: Дерево Піфагора")
    level = ask_int("Рівень рекурсії", default=9, min_val=1)
    angle = ask_float("Кут (градуси)", default=45.0, min_val=1.0, max_val=89.9)
    show = ask_bool("Показати вікно графіка", default=False)
    ensure_outdir()
    outfile = OUTDIR / f"pythagoras_level{level}_angle{int(angle)}.png"
    saved = draw_pythagoras_tree(level=level, angle_deg=angle, outfile=str(outfile), show=show)
    if saved:
        print(f"✅ Збережено: {saved}")

#Task 3 runner

def run_task3() -> None:
    print("\nЗавдання 3: Дейкстра з бінарною купою")
    directed = ask_bool("Орієнтований граф?", default=False)

    # Створюємо демо-граф і показуємо, які вершини доступні
    g = make_graph(DEMO_EDGES, directed=directed)
    vertices = sorted(g.keys())
    print("Доступні вершини:", ", ".join(vertices))

    # Валідуємо старт
    while True:
        start = ask("Початкова вершина", "A").strip()
        if start in g:
            break
        print(f"  ⚠️ Вершини '{start}' немає. Обери з: {', '.join(vertices)}")

    # Валідуємо goal (необов’язково)
    goal = ask("Цільова вершина (Enter = не шукати шлях)", "").strip()
    if goal and goal not in g:
        print(f"  ⚠️ Вершини '{goal}' немає. Пропускаю пошук шляху.")
        goal = ""

    # Обчислюємо Дейкстрою
    dist, prev = dijkstra_heap(g, start)

    print(f"\nНайкоротші відстані від {start}:")
    for v in vertices:
        d = dist.get(v, float("inf"))
        print(f"  {v}: {'∞' if d == float('inf') else round(d, 6)}")

    if goal:
        path = reconstruct_path(prev, start, goal)
        if path:
            print(f"\nШлях {start}→{goal}: {' -> '.join(path)} (довжина = {round(dist[goal], 6)})")
        else:
            print(f"\nШлях {start}→{goal}: недосяжно")

#Task 4 runner

def _parse_heap_string(s: str) -> list[float]:
    parts = s.replace(",", " ").split()
    out = []
    for p in parts:
        try:
            out.append(int(p))
        except ValueError:
            out.append(float(p))
    return out

def run_task4() -> None:
    print("\nЗавдання 4: Візуалізація бінарної купи")
    mode_min = ask_bool("Це min-heap? (інакше max)", default=True)
    heap_str = ask("Список значень (порожньо — дефолт '10 14 20 28 18 25 32')", "")
    if heap_str.strip():
        arr = _parse_heap_string(heap_str)
    else:
        arr = [10, 14, 20, 28, 18, 25, 32]
    do_heapify = ask_bool("Вирівняти масив до валідної купи (heapify)?", default=False)
    show_index = ask_bool("Показувати індекси у вузлах?", default=False)
    show = ask_bool("Показати вікно графіка?", default=False)

    #Використаємо CLI-функції з task4 через імпортовані будівельники
    if do_heapify:
        #Легка нормалізація через власний main — тут не тягнемо heapify-обгортки,
        #просто вкажемо користувачу про виділення порушень червоним.
        print("⚠️ heapify не застосовано в main.py; порушення heap-властивості будуть підсвічені томатовим.")
    root = build_heap_tree(arr, mode="min" if mode_min else "max", show_index=show_index, cmap_name="Blues")
    if root is None:
        print("Порожній масив — нема що малювати.")
        return
    ensure_outdir()
    outfile = OUTDIR / f"heap_{'min' if mode_min else 'max'}.png"
    draw_heap_tree(root, title=f"Бінарна купа ({'min' if mode_min else 'max'})", outfile=str(outfile), show=show)
    print(f"✅ Збережено: {outfile}")

#Task 5 runner

def run_task5() -> None:
    print("\nЗавдання 5: Обходи дерева (BFS/DFS)")
    mode = "bfs" if ask_bool("Обхід BFS? (інакше DFS)", default=True) else "dfs"
    tree_str = ask("Елементи дерева (напр. '0 4 1 5 10 3' або 'A B C D None E')", "")
    if tree_str.strip():
        arr = parse_tree_string(tree_str)
    else:
        arr = ["0", "4", "1", "5", "10", "3"]
    annotate = ask_bool("Дописувати порядковий номер відвідування?", default=True)
    show_index = ask_bool("Показувати індекс вузла у підписі?", default=False)
    show = ask_bool("Показати вікно графіка?", default=False)

    root = build_tree_from_array(arr, show_index=show_index)
    if root is None:
        print("Порожнє дерево — нема що обходити.")
        return

    order = traverse_bfs(root) if mode == "bfs" else traverse_dfs(root)
    colorize_by_order(root, order, annotate=annotate)

    ensure_outdir()
    outfile = OUTDIR / f"traversal_{mode}.png"
    draw_traversal_tree(root, title=f"Обхід {mode.upper()}", outfile=str(outfile), show=show)
    print(f"✅ Збережено: {outfile}")

#Task 6 runner

def _print_food_solution(title: str, chosen, total_cost: int, total_cal: int, budget: int) -> None:
    print(f"\n{title}")
    if not chosen:
        print("Нічого не обрано (або замалий бюджет).")
        return
    print(fmt_food_table(chosen))
    print("-" * 48)
    print(f"Σ Вартість:  {total_cost}  (бюджет = {budget})")
    print(f"Σ Калорії:   {total_cal}")

def run_task6() -> None:
    print("\n=== Завдання 6: Їжа — greedy vs DP ===")
    budget = ask_int("Бюджет", default=100, min_val=0)
    #Використаємо вбудований набір
    chosen, tc, tcal = greedy_algorithm(DEFAULT_ITEMS, budget)
    _print_food_solution("Жадібний алгоритм (cal/cost)", chosen, tc, tcal, budget)

    chosen2, tc2, tcal2 = dynamic_programming(DEFAULT_ITEMS, budget)
    _print_food_solution("Динамічне програмування (0/1 knapsack)", chosen2, tc2, tcal2, budget)

#Task 7 runner

def run_task7() -> None:
    print("\nЗавдання 7: Два d6 — Монте-Карло")
    trials = ask_int("Кількість кидків", default=100_000, min_val=1)
    seed_s = ask("Seed (порожньо — без фіксації)", "")
    seed = int(seed_s) if seed_s.strip() else None
    do_plot = ask_bool("Побудувати графік (PNG)?", default=True)
    show = ask_bool("Показати вікно графіка?", default=False)

    sums = simulate_dice_rolls(trials, seed=seed)
    freqs = Counter(sums)
    sim_probs = frequencies_to_probs(freqs, trials)
    th_probs = theoretical_probs()

    print("\n" + fmt_dice_table(sim_probs, th_probs))
    mae, rmse = overall_errors(sim_probs, th_probs)
    print("\nMAE (п.п.):  {:.3f}".format(mae))
    print("RMSE (п.п.): {:.3f}".format(rmse))

    if do_plot or show:
        ensure_outdir()
        outfile = OUTDIR / "dice_probs.png" if do_plot else None
        plot_probs(sim_probs, th_probs, outfile=str(outfile) if outfile else None, show=show)
        if outfile:
            print(f"✅ Збережено: {outfile}")

#Menu

def menu() -> None:
    print(
#GOIT Final Project
#  1) Однозв’язний список (reverse / merge-sort / merge-two-sorted)
#  2) Дерево Піфагора (PNG/показ)
#  3) Дейкстра (heap) — демо-граф
#  4) Візуалізація бінарної купи
#  5) Візуалізація обходів BFS/DFS
#  6) Їжа: greedy vs DP
#  7) Два d6: Монте-Карло
#  0) Вихід
)
    while True:
        choice = ask("Обери пункт", "1")
        if choice == "1":
            run_task1()
        elif choice == "2":
            run_task2()
        elif choice == "3":
            run_task3()
        elif choice == "4":
            run_task4()
        elif choice == "5":
            run_task5()
        elif choice == "6":
            run_task6()
        elif choice == "7":
            run_task7()
        elif choice == "0":
            print("Бувай 👋")
            return
        else:
            print("  Невідомий пункт. Обери 0..7")
        print("\nГотово. Ще щось?")

if __name__ == "__main__":
    try:
        menu()
    except KeyboardInterrupt:
        print("\nВихід по Ctrl+C. Бувай 👋")