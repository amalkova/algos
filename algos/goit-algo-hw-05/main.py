#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Авто-запуск бенчмарку з фіксованими URL (Google Drive view → direct):
- Стаття 1: https://drive.google.com/file/d/18_R5vEQ3eDuy2VdV3K5Lu-R-B-adxXZh/view
- Стаття 2: https://drive.google.com/file/d/18BfXyQcmuinEI_8KDSnQm4bLx6yIFS_w/view

Запуск:  python3 main.py
(нічого вказувати не треба; якщо захочеш ручний режим — запускай bench_search.py з аргументами)
"""

from __future__ import annotations
from pathlib import Path
import csv

# Імпортуємо реалізації та утиліти з bench_search.py (який уже в репо)
from bench_search import (
    fetch_text_from_url,
    auto_present,
    ensure_absent,
    bench_once,
    ALGOS,  # {"KMP": ..., "Boyer–Moore–Horspool": ..., "Rabin–Karp": ...}
)

# ==== Налаштування за замовчуванням (можеш змінити за потреби) ====
URL_ARTICLE_1 = "https://drive.google.com/file/d/18_R5vEQ3eDuy2VdV3K5Lu-R-B-adxXZh/view"
URL_ARTICLE_2 = "https://drive.google.com/file/d/18BfXyQcmuinEI_8KDSnQm4bLx6yIFS_w/view"

REPEATS = 5                    # скільки разів міряти timeit (беремо мінімум)
CSV_PATH = Path("results.csv") # куди зберігати підсумкову таблицю


def run_benchmark_from_urls() -> None:
    print("[info] Завантажую тексти з URL (Google Drive)...")
    text1 = fetch_text_from_url(URL_ARTICLE_1)
    text2 = fetch_text_from_url(URL_ARTICLE_2)

    # Підбираємо підрядки: present (існуючий) і absent (вигаданий)
    present1 = auto_present(text1, 24)
    present2 = auto_present(text2, 18)

    absent1 = ensure_absent(text1, "космічний єдиноріг 4242")
    absent2 = ensure_absent(text2, "квантовий бабуїн 31337")

    rows = []
    cases = [
        ("стаття 1", text1, present1, "present"),
        ("стаття 1", text1, absent1,  "absent"),
        ("стаття 2", text2, present2, "present"),
        ("стаття 2", text2, absent2,  "absent"),
    ]

    print(f"[info] repeats: {REPEATS}\n")

    # Запускаємо всі алгоритми на кожному кейсі
    for label, txt, pat, ptype in cases:
        for name, fn in ALGOS.items():
            t = bench_once(fn, txt, pat, repeats=REPEATS)
            rows.append({
                "file": label,
                "pattern_type": ptype,
                "pattern": pat,
                "algo": name,
                f"time_s_min_of_{REPEATS}": t,
            })
            print(f"[run] {label:8s} | {ptype:7s} | {name:21s} -> {t:.6f} s")

    # Зберігаємо CSV
    CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
    key_field = f"time_s_min_of_{REPEATS}"
    with CSV_PATH.open("w", newline="", encoding="utf-8") as f:
        fieldnames = list(rows[0].keys())
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)

    # Переможці per (file, pattern_type)
    by_key = {}
    for r in rows:
        k = (r["file"], r["pattern_type"])
        if k not in by_key or r[key_field] < by_key[k][key_field]:
            by_key[k] = r

    print("\n=== Winners by file/pattern ===")
    for k, r in by_key.items():
        print(f"{k[0]} | {k[1]} -> {r['algo']} ({r[key_field]:.6f} s)")

    # Найшвидший по КОЖНОМУ файлу (усереднюємо present+absent)
    per_file = {}
    for r in rows:
        k = (r["file"], r["algo"])
        per_file.setdefault(k, []).append(r[key_field])

    print("\n=== Fastest per file (avg present+absent) ===")
    for file_lbl in {"стаття 1", "стаття 2"}:
        pairs = []
        for (f, algo), times in per_file.items():
            if f == file_lbl:
                pairs.append((algo, sum(times)/len(times)))
        pairs.sort(key=lambda x: x[1])
        winner_algo, winner_time = pairs[0]
        print(f"{file_lbl}: {winner_algo} ({winner_time:.6f} s)")

    # Глобальні середні по алгоритмах
    sums, cnts = {}, {}
    for r in rows:
        algo = r["algo"]
        sums[algo] = sums.get(algo, 0.0) + r[key_field]
        cnts[algo] = cnts.get(algo, 0) + 1
    means = sorted(((a, sums[a]/cnts[a]) for a in sums), key=lambda x: x[1])

    print("\n=== Algo means (lower = better) ===")
    for a, v in means:
        print(f"{a:21s} : {v:.6f} s")

    print(f"\nSaved CSV -> {CSV_PATH.resolve()}")


if __name__ == "__main__":
    run_benchmark_from_urls()