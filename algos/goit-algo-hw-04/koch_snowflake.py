#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Task 2. Сніжинка Коха (гібридний режим).

Режими:
1) Авто-режим (без аргументів):
   python3 koch_snowflake.py
   → LEVEL = 3, OUTFILE = ./koch_snowflake_level3.png

2) CLI-режим (для перевірки ментором):
   python3 koch_snowflake.py --level 5 --outfile myflake.png
"""
from __future__ import annotations
from math import sqrt
from pathlib import Path
import sys

# мʼяке повідомлення, якщо matplotlib не встановлено
try:
    import matplotlib.pyplot as plt
except ModuleNotFoundError as e:
    print("❌ Не знайдено matplotlib. Встанови: pip3 install matplotlib")
    raise

AUTO_LEVEL = 3
AUTO_OUTFILE = Path(__file__).parent / f"koch_snowflake_level{AUTO_LEVEL}.png"

def koch_curve(p1: complex, p2: complex, level: int) -> list[complex]:
    if level == 0:
        return [p1, p2]
    s = p1 + (p2 - p1) / 3
    t = p1 + 2 * (p2 - p1) / 3
    # вершина рівностороннього трикутника (поворот +60° у комплексній площині)
    u = s + (t - s) * complex(0.5, sqrt(3) / 6)
    return (
        koch_curve(p1, s, level - 1)[:-1]
        + koch_curve(s, u, level - 1)[:-1]
        + koch_curve(u, t, level - 1)[:-1]
        + koch_curve(t, p2, level - 1)
    )

def snowflake(level: int) -> list[complex]:
    a, b, c = complex(0, 0), complex(1, 0), complex(0.5, sqrt(3) / 2)
    return (
        koch_curve(a, b, level)[:-1]
        + koch_curve(b, c, level)[:-1]
        + koch_curve(c, a, level)
    )

def parse_args_or_none():
    """Якщо аргументів немає — повертає (None, None) для авто-режиму."""
    if len(sys.argv) == 1:
        return None, None
    import argparse
    ap = argparse.ArgumentParser(description="Koch snowflake renderer (CLI)")
    ap.add_argument("--level", type=int, default=3, help="Рівень рекурсії (default: 3)")
    ap.add_argument("--outfile", type=str, default=None, help="Шлях до PNG-файлу")
    args = ap.parse_args()
    level = max(0, int(args.level))
    outfile = Path(args.outfile) if args.outfile else Path(__file__).parent / f"koch_snowflake_level{level}.png"
    return level, outfile

def render_and_save(level: int, outfile: Path):
    pts = snowflake(level)
    xs, ys = [z.real for z in pts], [z.imag for z in pts]
    plt.figure(figsize=(6, 6))
    plt.axis("equal"); plt.axis("off")
    plt.plot(xs + [xs[0]], ys + [ys[0]], linewidth=1)
    outfile.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(outfile, dpi=200, bbox_inches="tight", pad_inches=0)
    print(f"✅ Saved: {outfile}")

def main():
    level, outfile = parse_args_or_none()
    if level is None:
        # авто-режим
        level, outfile = AUTO_LEVEL, AUTO_OUTFILE
        print(f"[mode] auto | level={level} | outfile={outfile}")
    else:
        print(f"[mode] cli  | level={level} | outfile={outfile}")
    render_and_save(level, outfile)

if __name__ == "__main__":
    main()