# GOIT Algo HW-04

## Файли
- sort_files.py — Task 1 (CLI: `python3 sort_files.py SRC [DEST]`; авто-режим без аргументів).
- koch_snowflake.py — Task 2 (CLI: `--level`, `--outfile`; авто-режим без аргументів).
- sort_bench.py — Task 3 (CLI: `--sizes ... --repeats N`; авто-режим без аргументів).

## Висновки (Task 3)
- Insertion sort має `O(n²)` і різко програє на випадкових/обернених наборах.
- Merge sort стабільний `O(n log n)`, але має накладні витрати на злиття/пам’ять.
- **Timsort (`sorted`)** — гібрид злиття та вставок, адаптивний до вже відсортованих підпослідовностей; на практиці найшвидший або серед лідерів, особливо на «майже відсортованих» даних. Тому доцільно використовувати вбудовані `sorted()` / `.sort()`.

## Приклади запуску
```bash
# Task 1
python3 sort_files.py /path/to/src /path/to/dest
python3 sort_files.py /path/to/src

# Task 2
python3 koch_snowflake.py --level 4 --outfile snow4.png
python3 koch_snowflake.py

# Task 3
python3 sort_bench.py --sizes 2000 5000 10000 --repeats 3
python3 sort_bench.py