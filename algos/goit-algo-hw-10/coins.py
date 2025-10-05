#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#Завдання 1:
#- find_coins_greedy(amount, coins) -> dict
#- find_min_coins(amount, coins)    -> dict (динамічне програмування)
#Монетний ряд за замовчуванням: [50, 25, 10, 5, 2, 1]

from __future__ import annotations
from typing import Dict, List

COINS_DEFAULT = [50, 25, 10, 5, 2, 1]

def find_coins_greedy(amount: int, coins: List[int] = None) -> Dict[int, int]:
    #Жадібний алгоритм: завжди беремо найбільший доступний номінал
    #Повертаємо словник {номінал: кількість} (лише використані монети)
    if amount < 0:
        raise ValueError("Сума має бути невід’ємна")
    if coins is None:
        coins = COINS_DEFAULT
    coins = sorted(coins, reverse=True)

    res: Dict[int, int] = {}
    remaining = amount
    for c in coins:
        if remaining == 0:
            break
        k = remaining // c
        if k:
            res[c] = k
            remaining -= k * c
    return res


def find_min_coins(amount: int, coins: List[int] = None) -> Dict[int, int]:

    #Динамічне програмування (к-напповська схема):
    #dp[s] = мін. кількість монет на суму s
    #last[s] = який номінал узяли останнім, щоб отримати dp[s]
    #Складність: O(len(coins) * amount), пам'ять: O(amount)

    if amount < 0:
        raise ValueError("Сума має бути невід’ємна")
    if coins is None:
        coins = COINS_DEFAULT
    coins = sorted(coins)  # корисно для приємного порядку у відповіді

    INF = 10**18
    dp = [INF] * (amount + 1)
    last = [-1] * (amount + 1)
    dp[0] = 0

    for c in coins:
        for s in range(c, amount + 1):
            if dp[s - c] + 1 < dp[s]:
                dp[s] = dp[s - c] + 1
                last[s] = c

    if dp[amount] == INF:
        # теоретично з монетою "1" завжди досяжно, але залишимо для повноти
        raise ValueError("Неможливо скласти дану суму цими монетами")

    # Відновлення розв'язку
    res: Dict[int, int] = {}
    s = amount
    while s > 0:
        c = last[s]
        if c == -1:
            raise RuntimeError("Непослідовний стан dp")
        res[c] = res.get(c, 0) + 1
        s -= c

    # Відсортуємо ключі зростанням як у прикладі {1:..., 2:..., 10:..., 50:...}
    return dict(sorted(res.items()))

# CLI для швидкої перевірки
if __name__ == "__main__":
    import argparse, json
    ap = argparse.ArgumentParser(description="Change-making: greedy vs DP")
    ap.add_argument("amount", type=int, help="Сума для розміну")
    ap.add_argument(
        "--coins", nargs="*", type=int,
        help="Номінали монет (за замовчуванням 50 25 10 5 2 1)"
    )
    args = ap.parse_args()
    coins = args.coins if args.coins else COINS_DEFAULT

    g = find_coins_greedy(args.amount, coins)
    d = find_min_coins(args.amount, coins)
    print("[greedy]     ", json.dumps(g, ensure_ascii=False))
    print("[dynamic]    ", json.dumps(d, ensure_ascii=False))