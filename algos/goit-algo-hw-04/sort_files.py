#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Task 1. Рекурсивне сортування файлів за розширенням.

Режими запуску:
1) Режим перевірки (критерії ДЗ) — з аргументами:
   python3 sort_files.py SRC [DEST]
   де SRC — обов'язково; DEST — опційно (default=./dist)

2) Авто-режим (без твоєї участі) — без аргументів:
   python3 sort_files.py
   → SRC = ~/Downloads/test_src (буде створено демо-файли, якщо немає)
     DEST = ./dist (поруч зі скриптом)
"""

from __future__ import annotations
import argparse
import shutil
from pathlib import Path
from collections import Counter
import sys

AUTO_SRC  = Path("~/Downloads/test_src").expanduser()
AUTO_DEST = Path(__file__).parent / "dist"

def is_subpath(child: Path, parent: Path) -> bool:
    try:
        cr, pr = child.resolve(), parent.resolve()
        return pr in cr.parents
    except Exception:
        return False

def safe_copy(src_file: Path, dst_dir: Path):
    dst_dir.mkdir(parents=True, exist_ok=True)
    target = dst_dir / src_file.name
    if target.exists():
        stem, suffix = target.stem, target.suffix
        i = 1
        while True:
            candidate = dst_dir / f"{stem}__copy{i}{suffix}"
            if not candidate.exists():
                target = candidate
                break
            i += 1
    shutil.copy2(src_file, target)
    print(f"[copy] {src_file} -> {target}")

def process_dir(src: Path, dest_root: Path) -> Counter:
    stats = Counter()
    for entry in src.iterdir():
        try:
            if entry.is_symlink():
                print(f"[skip] symlink: {entry}")
                continue
            if entry.is_dir():
                stats.update(process_dir(entry, dest_root))
            elif entry.is_file():
                ext = entry.suffix.lower().lstrip(".") or "no_ext"
                safe_copy(entry, dest_root / ext)
                stats[ext] += 1
            else:
                print(f"[skip] невідомий тип: {entry}")
        except Exception as e:
            print(f"[err] {entry}: {e}")
    return stats

def ensure_demo_src(src: Path) -> Path:
    if not src.exists():
        print(f"[init] Створю демо-набір у: {src}")
        src.mkdir(parents=True, exist_ok=True)
        (src / "file1.txt").write_text("Hello text\n", encoding="utf-8")
        (src / "script.py").write_text("print('hi')\n", encoding="utf-8")
        (src / "doc.pdf").write_text("%PDF-1.4\n", encoding="utf-8")
        (src / "image.jpg").touch()
        (src / "README").write_text("no extension\n", encoding="utf-8")
    return src

def parse_args_or_none():
    """Пробуємо розпарсити CLI. Якщо аргументів немає — повертаємо None, None (авто-режим)."""
    # якщо немає додаткових аргументів, окрім самого скрипта — авто-режим
    if len(sys.argv) == 1:
        return None, None
    p = argparse.ArgumentParser(description="Recursive file sorter by extension")
    p.add_argument("src", type=Path, help="Шлях до вихідної директорії")
    p.add_argument("dest", type=Path, nargs="?", default=Path("dist"),
                   help="Шлях до директорії призначення (default=./dist)")
    args = p.parse_args()
    return args.src, args.dest

def main():
    src, dest = parse_args_or_none()

    if src is None and dest is None:
        # Авто-режим для зручного запуску без твоєї участі
        src, dest = ensure_demo_src(AUTO_SRC), AUTO_DEST
        print("[mode] auto")
    else:
        print("[mode] cli")

    if not src.is_dir():
        print("❌ Вихідний шлях не існує або це не директорія")
        return

    # Захист від самокопіювання
    if src == dest or is_subpath(dest, src) or is_subpath(src, dest):
        print("❌ Шляхи src та dest перетинаються. Обери іншу директорію призначення.")
        return

    dest.mkdir(parents=True, exist_ok=True)
    print(f"[src]  {src.resolve()}")
    print(f"[dest] {dest.resolve()}")
    print("[run] Починаю рекурсивне копіювання...\n")

    stats = process_dir(src, dest)

    print("\n=== Підсумок ===")
    total = sum(stats.values())
    if total == 0:
        print("⚠️ Файлів не знайдено")
    else:
        for ext, cnt in sorted(stats.items()):
            print(f"{ext:>8}: {cnt}")
        print(f"Σ Разом: {total}")
    print(f"\n[done] Перевір папку: {dest.resolve()}")

if __name__ == "__main__":
    main()