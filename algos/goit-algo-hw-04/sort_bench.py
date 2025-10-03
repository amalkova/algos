#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Task 3. Порівняння insertion sort, merge sort та timsort.

Режими:
1) Авто-режим (без аргументів):
   python3 sort_bench.py
   → sizes=[2000,5000,10000], repeats=3, results.csv збережеться поруч

2) CLI-режим:
   python3 sort_bench.py --sizes 1000 2000 3000 --repeats 5
"""

from __future__ import annotations
import csv, random, timeit, sys, argparse
from statistics import mean
from typing import List, Callable, Iterable
from pathlib import Path

# дефолтні параметри (для авто-режиму)
AUTO_SIZES = [2000, 5000, 10000]
AUTO_REPEATS = 3
CSV_PATH = Path(__file__).parent / "results.csv"

# ---------- Алгоритми ----------
def insertion_sort(arr: List[int]) -> List[int]:
    a = arr[:]
    for i in range(1, len(a)):
        key = a[i]; j = i - 1
        while j >= 0 and a[j] > key:
            a[j + 1] = a[j]; j -= 1
        a[j + 1] = key
    return a

def merge_sort(arr: List[int]) -> List[int]:
    if len(arr) <= 1: return arr[:]
    mid = len(arr)//2
    left, right = merge_sort(arr[:mid]), merge_sort(arr[mid:])
    return _merge(left, right)

def _merge(left: List[int], right: List[int]) -> List[int]:
    i = j = 0; merged: List[int] = []
    while i < len(left) and j < len(right):
        if left[i] <= right[j]: merged.append(left[i]); i += 1
        else: merged.append(right[j]); j += 1
    return merged + left[i:] + right[j:]

def timsort(arr: List[int]) -> List[int]:
    return sorted(arr)

# ---------- Дані ----------
def make_random(n: int) -> List[int]:   return random.sample(range(n*10), n)
def make_sorted(n: int) -> List[int]:   return list(range(n))
def make_reversed(n: int) -> List[int]: return list(range(n,0,-1))
def make_nearly_sorted(n: int, swaps: int|None=None) -> List[int]:
    a = list(range(n)); swaps = swaps or max(1, n//100)
    for _ in range(swaps):
        i, j = random.randrange(n), random.randrange(n)
        a[i], a[j] = a[j], a[i]
    return a

# ---------- Бенчмарк ----------
def bench_once(fn: Callable[[List[int]], List[int]], data: List[int]) -> float:
    return timeit.Timer(lambda: fn(data)).timeit(number=1)

def bench_suite(sizes: Iterable[int], repeats: int):
    datasets = {
        "random": make_random,
        "sorted": make_sorted,
        "reversed": make_reversed,
        "nearly_sorted": make_nearly_sorted,
    }
    algos = {"insertion": insertion_sort, "merge": merge_sort, "timsort": timsort}
    rows = []
    for n in sizes:
        for ds_name, maker in datasets.items():
            base = maker(n)
            for algo_name, algo in algos.items():
                print(f"[run] {algo_name:9s} | n={n:6d} | dataset={ds_name}")
                times = [bench_once(algo, base) for _ in range(repeats)]
                rows.append({"n": n, "dataset": ds_name, "algo": algo_name,
                             "time_s_avg": round(mean(times), 6)})
    return rows

def print_table(rows):
    headers = ["n","dataset","algo","time_s_avg"]
    print("\n=== Результати бенчмарку ===")
    print("\t".join(headers))
    for r in rows:
        print("\t".join(str(r[h]) for h in headers))

def save_csv(rows, path: Path):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["n","dataset","algo","time_s_avg"])
        w.writeheader(); w.writerows(rows)

def parse_args_or_auto():
    if len(sys.argv) == 1:
        return AUTO_SIZES, AUTO_REPEATS
    ap = argparse.ArgumentParser(description="Benchmark sorting algorithms")
    ap.add_argument("--sizes", type=int, nargs="+", default=AUTO_SIZES,
                    help="Розміри масивів (наприклад: --sizes 1000 2000 3000)")
    ap.add_argument("--repeats", type=int, default=AUTO_REPEATS,
                    help="Кількість повторів для усереднення (default=3)")
    args = ap.parse_args()
    return args.sizes, args.repeats

def main():
    sizes, repeats = parse_args_or_auto()
    print(f"[mode] sizes={sizes} | repeats={repeats}")
    rows = bench_suite(sizes, repeats)
    print_table(rows)
    save_csv(rows, CSV_PATH)
    print(f"\n✅ Saved CSV: {CSV_PATH}")

if __name__ == "__main__":
    main()