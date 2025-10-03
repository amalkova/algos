#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Завдання 1 (наднадійний режим):
- Без GUI, без input.
- SRC = ~/Downloads/test_src (створюється з демо-файлами, якщо нема).
- DEST = ./dist поруч зі скриптом.
- Докладний консольний лог, щоб було видно, що саме відбувається.
"""
from __future__ import annotations
from pathlib import Path
from collections import Counter
import shutil
import sys

SRC = Path("~/Downloads/test_src").expanduser()
DEST = Path(__file__).parent / "dist"

def log(msg: str):
    print(msg, flush=True)

def ensure_demo_src(src: Path) -> Path:
    if not src.exists():
        log(f"[init] Створю демо-набір у: {src}")
        src.mkdir(parents=True, exist_ok=True)
        (src / "file1.txt").write_text("Hello text\n", encoding="utf-8")
        (src / "script.py").write_text("print('hi')\n", encoding="utf-8")
        (src / "doc.pdf").write_text("%PDF-1.4\n", encoding="utf-8")
        (src / "image.jpg").touch()
        (src / "README").write_text("no extension\n", encoding="utf-8")
    else:
        log(f"[ok] Знайшов SRC: {src}")
    return src

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
    log(f"[copy] {src_file}  ->  {target}")

def process_dir(src: Path, dest_root: Path) -> Counter:
    stats = Counter()
    for entry in src.iterdir():
        if entry.is_symlink():
            log(f"[skip] symlink: {entry}")
            continue
        if entry.is_dir():
            stats.update(process_dir(entry, dest_root))
        elif entry.is_file():
            ext = entry.suffix.lower().lstrip(".") or "no_ext"
            safe_copy(entry, dest_root / ext)
            stats[ext] += 1
        else:
            log(f"[skip] невідомий тип: {entry}")
    return stats

def main():
    print("=== GOIT HW-04 | Task 1 | auto-mode ===", flush=True)
    try:
        src = ensure_demo_src(SRC)
        dest = DEST
        if src == dest or str(dest).startswith(str(src)) or str(src).startswith(str(dest)):
            print("❌ SRC і DEST перетинаються. Зміни DEST у коді.", flush=True)
            sys.exit(1)
        dest.mkdir(parents=True, exist_ok=True)
        print(f"[paths] SRC:  {src.resolve()}", flush=True)
        print(f"[paths] DEST: {dest.resolve()}", flush=True)
        print("[run] Починаю рекурсивне копіювання...\n", flush=True)
        stats = process_dir(src, dest)
        total = sum(stats.values())
        print("\n=== Результат ===", flush=True)
        if total == 0:
            print("⚠️  У вихідній директорії файлів не знайдено.", flush=True)
        else:
            for ext, cnt in sorted(stats.items()):
                print(f"  {ext:>8}: {cnt}", flush=True)
            print(f"Σ Разом: {total}", flush=True)
        print(f"\n[done] Перевір папку: {dest.resolve()}", flush=True)
    except Exception as e:
        print(f"❌ Помилка: {e}", flush=True)
        raise

if __name__ == "__main__":
    main()