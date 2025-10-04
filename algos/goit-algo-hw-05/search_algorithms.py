#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Реалізації алгоритмів пошуку підрядка:
- KMP (Кнут—Морріс—Пратт)
- Boyer–Moore–Horspool (спрощений Бойера—Мура)
- Rabin–Karp (ролінг-хеш)
"""

from __future__ import annotations

def kmp_search(text: str, pattern: str) -> int:
    if pattern == "":
        return 0
    lps = [0] * len(pattern)
    j = 0
    for i in range(1, len(pattern)):
        while j > 0 and pattern[i] != pattern[j]:
            j = lps[j - 1]
        if pattern[i] == pattern[j]:
            j += 1
            lps[i] = j
    j = 0
    for i, ch in enumerate(text):
        while j > 0 and ch != pattern[j]:
            j = lps[j - 1]
        if ch == pattern[j]:
            j += 1
            if j == len(pattern):
                return i - j + 1
    return -1


def bmh_search(text: str, pattern: str) -> int:
    m = len(pattern)
    n = len(text)
    if m == 0:
        return 0
    if m > n:
        return -1

    default = m
    skip = {}
    for i in range(m - 1):
        skip[pattern[i]] = m - 1 - i

    i = 0
    while i <= n - m:
        if text[i + m - 1] == pattern[m - 1]:
            if text[i:i + m] == pattern:
                return i
            i += default
        else:
            i += skip.get(text[i + m - 1], default)
    return -1


def rabin_karp_search(text: str, pattern: str, base: int = 256, mod: int = 10**9 + 7) -> int:
    m = len(pattern)
    n = len(text)
    if m == 0:
        return 0
    if m > n:
        return -1

    high = pow(base, m - 1, mod)
    ph = 0
    th = 0
    for i in range(m):
        ph = (ph * base + ord(pattern[i])) % mod
        th = (th * base + ord(text[i])) % mod

    for i in range(n - m + 1):
        if ph == th and text[i:i + m] == pattern:
            return i
        if i < n - m:
            th = ((th - ord(text[i]) * high) * base + ord(text[i + m])) % mod
            if th < 0:
                th += mod
    return -1