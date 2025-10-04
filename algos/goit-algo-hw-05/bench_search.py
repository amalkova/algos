#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Бенчмарк пошуку підрядка: KMP / Boyer–Moore–Horspool / Rabin–Karp

Джерела текстів:
- або локальні файли (CLI: --file двічі, або авто-режим з ./data/стаття 1.txt і ./data/стаття 2.txt),
- або URL (CLI: --url двічі). Підтримуються Google Drive “view”-посилання:
  https://drive.google.com/file/d/<ID>/view
  → конвертуємо в пряме завантаження:
  https://drive.google.com/uc?export=download&id=<ID>

Приклади:
1) З URL (конкретно твої):
   python3 bench_search.py \
     --url "https://drive.google.com/file/d/18_R5vEQ3eDuy2VdV3K5Lu-R-B-adxXZh/view" \
     --url "https://drive.google.com/file/d/18BfXyQcmuinEI_8KDSnQm4bLx6yIFS_w/view" \
     --repeats 5 --csv results.csv

2) З файлами:
   python3 bench_search.py --file "data/стаття 1.txt" --file "data/стаття 2.txt" --repeats 5

Алгоритми та логіка вимірювань: timeit, мінімум із N повторів.
"""

from __future__ import annotations
import argparse
import csv
import re
import timeit
from pathlib import Path
from typing import Callable, Dict, List, Tuple
from urllib import request, parse, error

from search_algorithms import kmp_search, bmh_search, rabin_karp_search


ALGOS: Dict[str, Callable[[str, str], int]] = {
    "KMP": kmp_search,
    "Boyer–Moore–Horspool": bmh_search,
    "Rabin–Karp": rabin_karp_search,
}

# -------------------- Завантаження тексту з URL (Drive view → direct) -------------------- #

_DRIVE_FILE_RE = re.compile(r"/file/d/([^/]+)/")

def _drive_direct_url(url: str) -> str:
    try:
        u = parse.urlparse(url)
        if "drive.google.com" in u.netloc:
            m = _DRIVE_FILE_RE.search(u.path or "")
            if m:
                file_id = m.group(1)
                return f"https://drive.google.com/uc?export=download&id={file_id}"
            qs = parse.parse_qs(u.query or "")
            if "id" in qs:
                return f"https://drive.google.com/uc?export=download&id={qs['id'][0]}"
    except Exception:
        pass
    return url

def _fetch_bytes(url: str, timeout: int = 30) -> bytes:
    req = request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (compatible; bench_search/1.0)"},
    )
    with request.urlopen(req, timeout=timeout) as resp:
        return resp.read()

def fetch_text_from_url(url: str) -> str:
    direct = _drive_direct_url(url)
    raw = _fetch_bytes(direct)
    for enc in ("utf-8", "utf-16", "cp1251", "latin-1"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")

# -------------------------------- Утиліти -------------------------------- #

def read_text(p: Path, encoding: str = "utf-8") -> str:
    return p.read_text(encoding=encoding, errors="replace")

def auto_present(text: str, length: int = 24) -> str:
    if not text:
        return ""
    start = max(0, len(text) // 2)
    candidate = text[start : start + length]
    if not candidate.strip():
        candidate = text[:length]
    return candidate

def ensure_absent(text: str, seed: str) -> str:
    s = seed
    while s in text:
        s += "x"
    return s

def bench_once(fn: Callable[[str, str], int], text: str, pattern: str, repeats: int) -> float:
    timer = timeit.Timer(lambda: fn(text, pattern))
    return min(timer.repeat(repeat=repeats, number=1))

# ----------------------------------- CLI ------------------------------------ #

def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Substring search benchmark (KMP/BMH/RK) — files or URLs")
    ap.add_argument("--file", action="append", help="Шлях до текстового файлу (вкажи ДВІЧІ для двох статей)", default=[])
    ap.add_argument("--url",  action="append", help="URL до тексту (вкажи ДВІЧІ). Підтримує Drive 'view'.", default=[])
    ap.add_argument("--present1", type=str, help="Існуючий підрядок у статті 1")
    ap.add_argument("--absent1",  type=str, help="Вигаданий (відсутній) підрядок у статті 1")
    ap.add_argument("--present2", type=str, help="Існуючий підрядок у статті 2")
    ap.add_argument("--absent2",  type=str, help="Вигаданий (відсутній) підрядок у статті 2")
    ap.add_argument("--repeats",  type=int, default=5, help="Кількість повторів у timeit (беремо мінімум)")
    ap.add_argument("--csv",      type=str, default="search_benchmark_results.csv", help="Куди зберегти CSV")
    return ap.parse_args()

def main() -> None:
    args = parse_args()
    texts: List[str] = []

    # 1) URL
    if args.url:
        if len(args.url) != 2:
            raise SystemExit("Для URL потрібно рівно 2 значення — дві статті. Використай --url двічі.")
        sources = [("URL#1", args.url[0]), ("URL#2", args.url[1])]
        for label, u in sources:
            try:
                txt = fetch_text_from_url(u)
            except error.HTTPError as e:
                raise SystemExit(f"HTTP {e.code} при завантаженні {label}: {u}")
            except error.URLError as e:
                raise SystemExit(f"Помилка мережі при завантаженні {label}: {u} ({e})")
            texts.append(txt)
        print(f"[info] джерела: URL [{args.url[0]}] | URL [{args.url[1]}]")

    # 2) FILES
    elif args.file:
        if len(args.file) != 2:
            raise SystemExit("Для файлів потрібно рівно 2 значення — дві статті. Використай --file двічі.")
        paths = [Path(args.file[0]), Path(args.file[1])]
        for p in paths:
            if not p.exists():
                raise SystemExit(f"Файл не знайдено: {p}")
            texts.append(read_text(p))
        print(f"[info] джерела: FILE [{paths[0]}] | FILE [{paths[1]}]")

    # 3) AUTO (data/…)
    else:
        cand1 = Path("data") / "стаття 1.txt"
        cand2 = Path("data") / "стаття 2.txt"
        if not (cand1.exists() and cand2.exists()):
            raise SystemExit("Авто-режим: поклади 'стаття 1.txt' і 'стаття 2.txt' у ./data, або використай --file / --url.")
        texts = [read_text(cand1), read_text(cand2)]
        print(f"[info] джерела: FILE [{cand1}] | FILE [{cand2}]")

    text1, text2 = texts

    # present/absent
    present1 = args.present1 if args.present1 else auto_present(text1, 24)
    present2 = args.present2 if args.present2 else auto_present(text2, 18)
    absent1  = ensure_absent(text1, args.absent1 if args.absent1 else "космічний єдиноріг 4242")
    absent2  = ensure_absent(text2, args.absent2 if args.absent2 else "квантовий бабуїн 31337")

    repeats = max(1, int(args.repeats))
    rows: List[dict] = []

    cases: List[Tuple[str, str, str]] = [
        ("стаття 1", text1, present1),
        ("стаття 1", text1, absent1),
        ("стаття 2", text2, present2),
        ("стаття 2", text2, absent2),
    ]
    case_types = {
        ("стаття 1", present1): "present",
        ("стаття 1", absent1 ): "absent",
        ("стаття 2", present2): "present",
        ("стаття 2", absent2 ): "absent",
    }

    print(f"[info] repeats: {repeats}\n")

    for label, txt, pat in cases:
        ptype = case_types[(label, pat)]
        for name, fn in ALGOS.items():
            t = bench_once(fn, txt, pat, repeats=repeats)
            rows.append({
                "file": label,
                "pattern_type": ptype,
                "pattern": pat,
                "algo": name,
                f"time_s_min_of_{repeats}": t,
            })
            print(f"[run] {label:8s} | {ptype:7s} | {name:21s} -> {t:.6f} s")

    # CSV
    csv_path = Path(args.csv)
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        fieldnames = list(rows[0].keys())
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)

    # Winners per (file, pattern_type)
    by_key = {}
    key_field = fieldnames[-1]
    for r in rows:
        key = (r["file"], r["pattern_type"])
        if key not in by_key or r[key_field] < by_key[key][key_field]:
            by_key[key] = r

    print("\n=== Winners by file/pattern ===")
    for k, r in by_key.items:
        pass
    for k, r in by_key.items():
        print(f"{k[0]} | {k[1]} -> {r['algo']} ({r[key_field]:.6f} s)")

    # Fastest per file (avg of present+absent)
    per_file = {}
    for r in rows:
        k = (r["file"], r["algo"])
        per_file.setdefault(k, []).append(r[key_field])
    per_file_mean = {}
    for (file_lbl, algo), ts in per_file.items():
        per_file_mean.setdefault(file_lbl, []).append((algo, sum(ts)/len(ts)))

    print("\n=== Fastest per file (avg present+absent) ===")
    for file_lbl, pairs in per_file_mean.items():
        pairs.sort(key=lambda x: x[1])
        winner_algo, winner_time = pairs[0]
        print(f"{file_lbl}: {winner_algo} ({winner_time:.6f} s)")

    # Global means
    sums, cnts = {}, {}
    for r in rows:
        algo = r["algo"]
        sums[algo] = sums.get(algo, 0.0) + r[key_field]
        cnts[algo] = cnts.get(algo, 0) + 1
    means = sorted(((a, sums[a]/cnts[a]) for a in sums), key=lambda x: x[1])

    print("\n=== Algo means (lower = better) ===")
    for a, v in means:
        print(f"{a:21s} : {v:.6f} s")

    print(f"\nSaved CSV -> {csv_path.resolve()}")

if __name__ == "__main__":
    main()