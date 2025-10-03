#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations
from math import sqrt
from pathlib import Path

try:
    import matplotlib.pyplot as plt
except ModuleNotFoundError:
    print("❌ Не знайдено matplotlib. Встанови: pip3 install matplotlib")
    raise

LEVEL = 3
OUTFILE = Path(__file__).parent / f"koch_snowflake_level{LEVEL}.png"

def koch_curve(p1: complex, p2: complex, level: int) -> list[complex]:
    if level == 0:
        return [p1, p2]
    s = p1 + (p2 - p1) / 3
    t = p1 + 2 * (p2 - p1) / 3
    u = s + (t - s) * complex(0.5, sqrt(3) / 6)  # поворот +60°
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

def main():
    pts = snowflake(LEVEL)
    xs, ys = [z.real for z in pts], [z.imag for z in pts]
    plt.figure(figsize=(6, 6))
    plt.axis("equal"); plt.axis("off")
    plt.plot(xs + [xs[0]], ys + [ys[0]], linewidth=1)
    plt.savefig(OUTFILE, dpi=200, bbox_inches="tight", pad_inches=0)
    print(f"✅ Saved: {OUTFILE}")

if __name__ == "__main__":
    main()