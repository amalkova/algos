#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#Завдання 2. Рекурсія — фрактал «дерево Піфагора».

#- Малює дерево Піфагора з довільним кутом розгалуження (за замовчуванням 45°)
#- Користувач задає рівень рекурсії --level (наприклад, 9)
#- Можна зберегти в PNG (--outfile) і/або показати вікно (--show)

#Приклади:
#    python3 task2_pythagoras_tree.py --level 10 --angle 45 --outfile tree.png --show
#    python3 task2_pythagoras_tree.py --level 8  --angle 35 --outfile tree35.png

from __future__ import annotations
import math
from typing import List, Tuple

import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from matplotlib import cm

def _square_from_base(z: complex, w: complex) -> List[Tuple[float, float]]:
    
    #Повертає 4 вершини квадрата, у якого нижня сторона — відрізок z->w.
    #Використовує множення на 1j (поворот на +90° у комплексній площині).
    
    v = w - z
    a = z
    b = w
    c = w + 1j * v  # верх-право
    d = z + 1j * v  # верх-ліво
    return [(a.real, a.imag), (b.real, b.imag), (c.real, c.imag), (d.real, d.imag)]

def _branch(
    z: complex,
    w: complex,
    depth: int,
    angle_rad: float,
    polys: List[List[Tuple[float, float]]],
    colors: List[Tuple[float, float, float, float]],
    level_max: int,
    cmap_name: str = "Reds",
) -> None:
    """
    Рекурсивно додає квадрати у списки polys/ colors.
    База рекурсії: depth == 0.
    """
    if depth == 0:
        return

    #1) Додаємо квадрат для базового відрізка
    polys.append(_square_from_base(z, w))

    #колір — градієнт за глибиною
    t = (level_max - depth) / max(1, level_max - 1)
    color = cm.get_cmap(cmap_name)(0.25 + 0.65 * t)  # трохи зміщуємо до «тепліших»
    colors.append(color)

    #2) Розрахунок наступних двох «баз» (ліва і права гілки)
    #Вершини верхньої сторони квадрата: d (ліворуч) і c (праворуч)
    v = w - z
    c = w + 1j * v
    d = z + 1j * v

    #Вектор верхньої сторони (дорівнює v)
    top = c - d

    #Точка-«верх» трикутника на квадраті:
    #p = d + top * (cosθ + i sinθ)
    #Далі з відрізків (d->p) та (p->c) рекурсивно будуємо дочірні квадрати
    rot = complex(math.cos(angle_rad), math.sin(angle_rad))
    p = d + top * rot

    #Ліва гілка: база d->p
    _branch(d, p, depth - 1, angle_rad, polys, colors, level_max, cmap_name)
    #Права гілка: база p->c
    _branch(p, c, depth - 1, angle_rad, polys, colors, level_max, cmap_name)

def draw_pythagoras_tree(
    level: int = 9,
    angle_deg: float = 45.0,
    width: int = 9,
    height: int = 9,
    line_width: float = 1.2,
    outfile: str | None = None,
    show: bool = False,
    cmap: str = "Reds",
) -> str | None:
    
    #Малює дерево Піфагора.
    #Повертає шлях до збереженого файлу (якщо outfile задано).
    
    if level < 1:
        raise ValueError("level має бути >= 1")
    if not (1 <= angle_deg < 89.9):
        raise ValueError("angle_deg має бути у (1°, 89.9°)")

    #Початковий базовий відрізок: [0, 1] на осі X (довжина 1)
    z0 = 0 + 0j
    w0 = 1 + 0j

    #Рекурсивно збираємо полігони
    polys: List[List[Tuple[float, float]]] = []
    colors: List[Tuple[float, float, float, float]] = []
    _branch(z0, w0, level, math.radians(angle_deg), polys, colors, level, cmap)

    #Малювання одним PolyCollection (значно швидше за поодинокі patch’і)
    fig, ax = plt.subplots(figsize=(width, height), layout="constrained")
    pc = PolyCollection(polys, facecolors="none", edgecolors=colors, linewidths=line_width)
    ax.add_collection(pc)

    ax.set_aspect("equal", adjustable="datalim")
    ax.autoscale()
    ax.axis("off")
    ax.set_title(f"Дерево Піфагора — level={level}, angle={angle_deg}°", pad=10)

    saved = None
    if outfile:
        fig.savefig(outfile, dpi=200, bbox_inches="tight")
        saved = outfile
    if show:
        plt.show()
    plt.close(fig)
    return saved

def _cli():
    import argparse
    ap = argparse.ArgumentParser(description="Фрактал «дерево Піфагора»")
    ap.add_argument("--level", type=int, default=9, help="рівень рекурсії (рекомендовано 7–12)")
    ap.add_argument("--angle", type=float, default=45.0, help="кут розгалуження у градусах (1..89)")
    ap.add_argument("--outfile", type=str, default=None, help="шлях до PNG (наприклад, tree.png)")
    ap.add_argument("--show", action="store_true", help="показати вікно з графіком")
    ap.add_argument("--cmap", type=str, default="Reds", help="назва колормепу matplotlib (напр., Reds, viridis)")
    ap.add_argument("--lw", type=float, default=1.2, help="товщина ліній")
    args = ap.parse_args()

    path = draw_pythagoras_tree(
        level=args.level,
        angle_deg=args.angle,
        outfile=args.outfile,
        show=args.show,
        cmap=args.cmap,
        line_width=args.lw,
    )
    if path:
        print(f"✅ saved: {path}")

if __name__ == "__main__":
    _cli()