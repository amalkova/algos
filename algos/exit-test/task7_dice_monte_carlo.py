#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#Завдання 7. Метод Монте-Карло: кидки двох кубиків.

#Функціональність:
#- Імітує велику кількість кидків двох гральних кубиків.
#- Рахує частоти та імовірності сум 2..12.
#- Порівнює з аналітичними імовірностями (1/36..6/36..1/36).
#- Друкує таблицю, обчислює абсолютні/відносні похибки.
#- Опційно: зберігає CSV з результатами, будує бар-діаграму.

#Приклади:
#    python3 task7_dice_monte_carlo.py
#    python3 task7_dice_monte_carlo.py --trials 500000 --seed 42 --csv dice_probs.csv
#    python3 task7_dice_monte_carlo.py --trials 200000 --plot dice_probs.png --show

from __future__ import annotations
import argparse
import csv
import math
import random
from collections import Counter
from typing import Dict, List, Tuple, Iterable, Optional

#Аналітичні імовірності

def theoretical_probs() -> Dict[int, float]:
    
    #Повертає аналітичні імовірності сум 2..12 для двох чесних d6.
    #К-сть комбінацій: 1,2,3,4,5,6,5,4,3,2,1 (усього 36).
    
    counts = {2:1, 3:2, 4:3, 5:4, 6:5, 7:6, 8:5, 9:4, 10:3, 11:2, 12:1}
    return {s: c/36.0 for s, c in counts.items()}


#Симуляція

def simulate_dice_rolls(trials: int, seed: Optional[int] = None) -> List[int]:
    """
    Симулює 'trials' кидків двох d6. Повертає список сум.
    Використовує стандартний 'random' — додаткових залежностей не потрібно.
    """
    if seed is not None:
        random.seed(seed)
    out: List[int] = []
    append = out.append
    for _ in range(trials):
        s = random.randint(1, 6) + random.randint(1, 6)
        append(s)
    return out

def frequencies_to_probs(freqs: Counter, total: int) -> Dict[int, float]:
    return {s: (freqs.get(s, 0) / total) for s in range(2, 13)}

#Таблиця/метрики

def format_table(sim: Dict[int, float], theo: Dict[int, float]) -> str:
    
    #Форматує таблицю з колонками:
    #  Сума | Емпірична | Аналітична | Абс. похибка | Відн. похибка (%)
    
    header = ("Сума", "Емпірична", "Аналітична", "Абс. похибка", "Відн. похибка, %")
    rows: List[Tuple[str, str, str, str, str]] = [header]
    for s in range(2, 13):
        p_sim = sim.get(s, 0.0)
        p_th = theo.get(s, 0.0)
        abs_err = abs(p_sim - p_th)
        rel_err = (abs_err / p_th * 100.0) if p_th > 0 else math.nan
        rows.append((
            str(s),
            f"{p_sim*100:6.2f}%",
            f"{p_th*100:6.2f}%",
            f"{abs_err*100:6.2f}%",
            f"{rel_err:8.2f}"
        ))
    # ширини колонок
    widths = [max(len(r[i]) for r in rows) for i in range(len(header))]
    lines = []
    for i, r in enumerate(rows):
        line = "  ".join(r[j].rjust(widths[j]) for j in range(len(header)))
        lines.append(line)
        if i == 0:
            lines.append("-" * len(line))
    return "\n".join(lines)


def overall_errors(sim: Dict[int, float], theo: Dict[int, float]) -> Tuple[float, float]:
    
    #Повертає (MAE, RMSE) у відсоткових пунктах (тобто *100).
    
    diffs = [(sim.get(s, 0.0) - theo.get(s, 0.0)) * 100.0 for s in range(2, 13)]
    mae = sum(abs(d) for d in diffs) / len(diffs)
    rmse = math.sqrt(sum(d*d for d in diffs) / len(diffs))
    return mae, rmse

#CSV збереження

def save_csv(path: str, sim: Dict[int, float], theo: Dict[int, float]) -> None:
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["sum", "empirical_prob", "theoretical_prob", "abs_error", "rel_error_percent"])
        for s in range(2, 13):
            p_sim = sim.get(s, 0.0)
            p_th = theo.get(s, 0.0)
            abs_err = abs(p_sim - p_th)
            rel_err = (abs_err / p_th * 100.0) if p_th > 0 else ""
            w.writerow([s, f"{p_sim:.6f}", f"{p_th:.6f}", f"{abs_err:.6f}", f"{rel_err:.6f}" if rel_err != "" else ""])

#Графік (matplotlib)

def plot_probs(sim: Dict[int, float], theo: Dict[int, float], outfile: Optional[str] = None, show: bool = False):

    #Будує бар-діаграму емпіричних і аналітичних імовірностей.
    #Не задаємо кастомні кольори — залишаємо дефолтні matplotlib.
    
    import matplotlib.pyplot as plt

    xs = list(range(2, 13))
    sim_vals = [sim.get(s, 0.0) for s in xs]
    th_vals = [theo.get(s, 0.0) for s in xs]

    width = 0.4
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.bar([x - width/2 for x in xs], sim_vals, width=width, label="Емпірична")
    ax.bar([x + width/2 for x in xs], th_vals, width=width, label="Аналітична")

    ax.set_xlabel("Сума на двох кубиках")
    ax.set_ylabel("Імовірність")
    ax.set_title("Імовірності сум (2..12): емпірична vs аналітична")
    ax.set_xticks(xs)
    ax.legend()
    ax.grid(True, alpha=0.3)

    if outfile:
        fig.savefig(outfile, dpi=200, bbox_inches="tight")
    if show:
        plt.show()
    plt.close(fig)

#CLI

def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Монте-Карло для двох кубиків: імовірності сум 2..12")
    ap.add_argument("--trials", type=int, default=100_000, help="Кількість кидків (за замовчуванням 100000)")
    ap.add_argument("--seed", type=int, help="Фіксований seed RNG для відтворюваності")
    ap.add_argument("--csv", type=str, help="Шлях до CSV з результатами")
    ap.add_argument("--plot", type=str, help="Шлях до PNG з графіком")
    ap.add_argument("--show", action="store_true", help="Показати вікно з графіком")
    return ap.parse_args()

def main() -> None:
    args = parse_args()
    trials = int(args.trials)
    if trials <= 0:
        raise ValueError("trials має бути додатнім цілим")

    #1) Симуляція
    sums = simulate_dice_rolls(trials, seed=args.seed)
    freqs = Counter(sums)
    sim_probs = frequencies_to_probs(freqs, trials)

    #2) Аналітичні
    th_probs = theoretical_probs()

    #3) Таблиця та метрики
    print(f"=== Два d6: Монте-Карло з {trials:,} кидків ===")
    print(format_table(sim_probs, th_probs))
    mae, rmse = overall_errors(sim_probs, th_probs)
    print("\nMAE (п.п.):  {:.3f}".format(mae))
    print("RMSE (п.п.): {:.3f}".format(rmse))

    #4) CSV/побудова графіка
    if args.csv:
        save_csv(args.csv, sim_probs, th_probs)
        print(f"\nCSV збережено → {args.csv}")
    if args.plot or args.show:
        plot_probs(sim_probs, th_probs, outfile=args.plot, show=args.show)
        if args.plot:
            print(f"PNG збережено → {args.plot}")

if __name__ == "__main__":
    main()