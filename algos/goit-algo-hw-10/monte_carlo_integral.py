#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#Завдання 2: Обчислення визначеного інтеграла методом Монте-Карло:
#I = ∫_a^b f(x) dx ≈ (b - a) * mean( f(U[a,b]) )
#Допоміжно: оцінка стандартної похибки ~ (b-a) * std(f(U))/sqrt(n)
#Порівняння:
#- якщо SciPy доступний: scipy.integrate.quad
#- для f(x)=x^2: аналітичний результат (b^3 - a^3)/3
#Також є опція зберегти графік (--plot out.png)

from __future__ import annotations
import argparse
from typing import Callable, Tuple, Optional
import math
import random

try:
    import numpy as np
except Exception:
    np = None  # працюватиме і без numpy (повільніше через random.random)

#приклади функцій

def f_x2(x: float) -> float:
    return x * x

def f_sin(x: float) -> float:
    return math.sin(x)

def f_exp(x: float) -> float:
    return math.exp(x)

FUNCS = {
    "x2": f_x2,
    "sin": f_sin,
    "exp": f_exp,
}

def monte_carlo_integral(
    f: Callable[[float], float], a: float, b: float, n: int, seed: Optional[int] = 42
) -> Tuple[float, float]:
    #Монте-Карло оцінка інтеграла і приблизної похибки (стандартна).
    #Повертає (estimate, stderr).

    if n <= 0:
        raise ValueError("n має бути > 0")
    if a == b:
        return 0.0, 0.0
    if seed is not None:
        random.seed(seed)
        if np is not None:
            np.random.seed(seed)

    width = b - a
    if np is not None:
        xs = np.random.uniform(a, b, size=n)
        ys = np.vectorize(f)(xs)
        mean = float(np.mean(ys))
        std = float(np.std(ys, ddof=1)) if n > 1 else 0.0
        stderr = width * (std / math.sqrt(n))
        return width * mean, stderr
    else:
        vals = []
        for _ in range(n):
            x = a + (b - a) * random.random()
            vals.append(f(x))
        m = sum(vals) / n
        # std:
        if n > 1:
            var = sum((v - m) ** 2 for v in vals) / (n - 1)
            std = math.sqrt(var)
        else:
            std = 0.0
        return width * m, width * (std / math.sqrt(n))

def analytic_if_available(name: str, a: float, b: float) -> Optional[float]:
    #Повертає аналітичний інтеграл, якщо відомий для вибраної функції
    if name == "x2":
        return (b**3 - a**3) / 3.0
    # інші можна додати за потреби
    return None

def quad_if_available(f: Callable[[float], float], a: float, b: float) -> Optional[Tuple[float, float]]:
    try:
        import scipy.integrate as spi  # type: ignore
    except Exception:
        return None
    val, err = spi.quad(lambda x: f(x), a, b)
    return float(val), float(err)

def maybe_plot(f: Callable[[float], float], a: float, b: float, out_path: Optional[str]) -> None:
    if not out_path:
        return
    try:
        import matplotlib.pyplot as plt
        import numpy as np  # type: ignore
    except Exception:
        print("[plot] matplotlib/numpy недоступні — графік пропускаю")
        return

    X = np.linspace(min(a, b) - 0.5, max(a, b) + 0.5, 400)
    Y = np.vectorize(f)(X)
    fig, ax = plt.subplots()
    ax.plot(X, Y, linewidth=2)
    ix = np.linspace(a, b, 200)
    iy = np.vectorize(f)(ix)
    ax.fill_between(ix, iy, color="gray", alpha=0.3)
    ax.axvline(x=a, color="gray", linestyle="--")
    ax.axvline(x=b, color="gray", linestyle="--")
    ax.set_xlabel("x")
    ax.set_ylabel("f(x)")
    ax.set_title(f"Інтегрування методом Монте-Карло на [{a}, {b}]")
    ax.grid(True)
    fig.tight_layout()
    fig.savefig(out_path, dpi=200, bbox_inches="tight")
    print(f"[plot] saved -> {out_path}")

def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Monte-Carlo integral with comparison")
    ap.add_argument("--func", choices=sorted(FUNCS.keys()), default="x2", help="вибір функції")
    ap.add_argument("--a", type=float, default=0.0, help="нижня межа")
    ap.add_argument("--b", type=float, default=2.0, help="верхня межа")
    ap.add_argument("--n", type=int, default=100000, help="кількість випадкових точок")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--plot", type=str, help="шлях для PNG (необов’язково)")
    return ap.parse_args()

def main() -> None:
    args = parse_args()
    f = FUNCS[args.func]

    est, stderr = monte_carlo_integral(f, args.a, args.b, args.n, args.seed)
    print(f"[mc]  estimate = {est:.10f}  (stderr ≈ {stderr:.3e})")

    quad_res = quad_if_available(f, args.a, args.b)
    if quad_res:
        q_val, q_err = quad_res
        print(f"[quad] value = {q_val:.10f}  (reported abs err ≈ {q_err:.3e})")
        print(f"[diff mc-quad] = {est - q_val:.10f}")
    else:
        ana = analytic_if_available(args.func, args.a, args.b)
        if ana is not None:
            print(f"[analytic] value = {ana:.10f}")
            print(f"[diff mc-analytic] = {est - ana:.10f}")
        else:
            print("[info] SciPy недоступний і аналітичний результат не визначено для цієї функції")

    maybe_plot(f, args.a, args.b, args.plot)

if __name__ == "__main__":
    main()