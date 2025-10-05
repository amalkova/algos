#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
from coins import find_coins_greedy, find_min_coins
from monte_carlo_integral import monte_carlo_integral, analytic_if_available, FUNCS

def run_task1():
    print("Завдання 1: монети")
    amount = 113
    greedy = find_coins_greedy(amount)
    dp = find_min_coins(amount)
    print(f"Сума: {amount}")
    print(f"Greedy: {greedy}")
    print(f"DP:     {dp}")
    print("Очікування: для канонічного ряду [50,25,10,5,2,1] Greedy == DP.\n")

def run_task2():
    print("Завдання 2: інтеграл (Монте-Карло)")
    f_name = "x2"
    f = FUNCS[f_name]
    a, b, n = 0.0, 2.0, 100000
    est, stderr = monte_carlo_integral(f, a, b, n, seed=42)
    print(f"f = {f_name}, interval = [{a}, {b}], n = {n}")
    print(f"Monte-Carlo: {est:.10f} (stderr ≈ {stderr:.3e})")
    ana = analytic_if_available(f_name, a, b)
    if ana is not None:
        print(f"Analytic:    {ana:.10f}")
        print(f"diff:        {est - ana:.10f}")
    print()

def main():
    run_task1()
    run_task2()

if __name__ == "__main__":
    main()