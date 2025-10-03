#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Task 1. Рекурсивне сортування файлів за розширенням.

Режими запуску:
1) CLI-режим (відповідає критеріям ДЗ):
   python3 sort_files.py SRC [DEST]
   де:
     SRC  – шлях до вихідної директорії (обов'язково)
     DEST – шлях до директорії призначення (опційно, default=./dist)

2) Авто-режим (без твоєї участі — зручно для швидкого запуску):
   python3 sort_files.py
   → SRC  = ~/Downloads/test_src  (створить демо-файли, якщо теки немає)
     DEST = ./dist (поруч зі скриптом)
"""

from __future__ import annotations
import argparse
import shutil
from pathlib import Path
from collections import Counter
import sys

# Шляхи для авто-режиму
AUTO_SRC  = Path("~/Downloads/test_src").expanduser()
AUTO_DEST = Path(__file__).parent / "dist"


def is_subpath(child: Path, parent: Path) -> bool:
    """True, якщо child знаходиться всередині parent (з урахуванням resolve())."""
    try:
        cr, pr = child.resolve(), parent.resolve()
        return pr in cr.parents
    except Exception:
        return False


def safe_copy(src_file: Path, dst_dir: Path) -> None:
    """Копіює файл у підпапку, уникаючи перезапису (file__copyN.ext)."""
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
    print(f"[copy] {src_file} -> {target}", flush=True)


def process_dir(src: Path, dest_root: Path) -> Counter:
    """Рекурсивно обходить SRC і копіює файли до DEST/<ext>/..."""
    stats = Counter()
    for entry in src.iterdir():
        try:
            if entry.is_symlink():
                print(f"[skip] symlink: {entry}", flush=True)
                continue
            if entry.is_dir():
                stats.update(process_dir(entry, dest_root))  # рекурсія
            elif entry.is_file():
                ext = entry.suffix.lower().lstrip(".") or "no_ext"
                safe_copy(entry, dest_root / ext)
                stats[ext] += 1
            else:
                print(f"[skip] невідомий тип: {entry}", flush=True)
        except PermissionError as e:
            print(f"[err] Permission denied: {entry} ({e})", flush=True)
        except OSError as e:
            print(f"[err] OS error: {entry} ({e})", flush=True)
        except Exception as e:
            print(f"[err] Unexpected: {entry} ({e})", flush=True)
    return stats


def ensure_demo_src(src: Path) -> Path:
    """Створює демо-набір файлів у SRC, якщо теки не існує."""
    if not src.exists():
        print(f"[init] Створю демо-набір у: {src}", flush=True)
        src.mkdir(parents=True, exist_ok=True)
        (src / "file1.txt").write_text("Hello text\n", encoding="utf-8")
        (src / "script.py").write_text("print('hi')\n", encoding="utf-8")
        (src / "doc.pdf").write_text("%PDF-1.4\n", encoding="utf-8")
        (src / "image.jpg").touch()
        (src / "README").write_text("no extension\n", encoding="utf-8")
    return src


def parse_args_or_none() -> tuple[Path | None, Path | None]:
    """
    Повертає (src, dest), якщо передані CLI-аргументи.
    Якщо скрипт запущено без аргументів — (None, None) → авто-режим.
    """
    if len(sys.argv) == 1:
        return None, None
    p = argparse.ArgumentParser(description="Recursive file sorter by extension")
    p.add_argument("src", type=Path, help="Шлях до вихідної директорії")
    p.add_argument(
        "dest",
        type=Path,
        nargs="?",
        default=Path("dist"),
        help="Шлях до директорії призначення (default=./dist)",
    )
    a = p.parse_args()
    return a.src, a.dest


def main() -> None:
    src, dest = parse_args_or_none()

    if src is None and dest is None:
        # Авто-режим (зручно для швидкого запуску)
        src, dest = ensure_demo_src(AUTO_SRC), AUTO_DEST
        print("[mode] auto", flush=True)
    else:
        print("[mode] cli", flush=True)

    if not src.is_dir():
        print("❌ Вихідний шлях не існує або це не директорія", flush=True)
        return

    # Захист від самокопіювання / перетину шляхів
    if src == dest or is_subpath(dest, src) or is_subpath(src, dest):
        print("❌ Шляхи src та dest перетинаються. Обери іншу директорію призначення.", flush=True)
        return

    dest.mkdir(parents=True, exist_ok=True)
    print(f"[src]  {src.resolve()}", flush=True)
    print(f"[dest] {dest.resolve()}", flush=True)
    print("[run] Починаю рекурсивне копіювання...\n", flush=True)

    stats = process_dir(src, dest)

    print("\n=== Підсумок ===", flush=True)
    total = sum(stats.values())
    if total == 0:
        print("⚠️ Файлів не знайдено", flush=True)
    else:
        for ext, cnt in sorted(stats.items()):
            print(f"{ext:>8}: {cnt}", flush=True)
        print(f"Σ Разом: {total}", flush=True)
    print(f"\n[done] Перевір папку: {dest.resolve()}", flush=True)


if __name__ == "__main__":
    main()