#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#Завдання 3. Алгоритм Дейкстри з використанням бінарної купи (heapq).

#Особливості:
#- Невід’ємні ваги ребер (вимога Дейкстри).
#- Підтримка неорієнтованого та орієнтованого графа.
#- Відновлення шляху prev-списком.
#- CLI: можна запускати на вбудованому демо-графі або передати CSV з ребрами.

#Формат CSV (без заголовка): u,v,w
#Приклад:
#A,B,4
#A,C,2
#C,E,3
#...

#Складність: O((V + E) log V) завдяки бінарній купі.

from __future__ import annotations
from typing import Dict, List, Tuple, Iterable, Optional
import heapq
import argparse
import csv
import math
from collections import defaultdict

#Типи
Node = str
Weight = float
AdjList = Dict[Node, List[Tuple[Node, Weight]]]

#Побудова графа
def make_graph(edges: Iterable[Tuple[Node, Node, Weight]], directed: bool = False) -> AdjList:
    #Створює список суміжності з набору ребер (u, v, w)
    g: AdjList = defaultdict(list)
    for u, v, w in edges:
        if w < 0:
            raise ValueError("Dijkstra потребує невід’ємних ваг ребер")
        g[u].append((v, float(w)))
        if not directed:
            g[v].append((u, float(w)))
        #гарантуємо наявність ключів у словнику
        _ = g[u]; _ = g[v]
    return g

def load_edges_csv(path: str) -> List[Tuple[Node, Node, Weight]]:
    #Завантажити ребра з CSV формату u,v,w (без заголовка)
    edges: List[Tuple[Node, Node, Weight]] = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            if not row or row[0].startswith("#"):
                continue
            if len(row) != 3:
                raise ValueError(f"Невірний рядок CSV: {row!r}")
            u, v, w = row
            edges.append((u.strip(), v.strip(), float(w)))
    return edges

#Дейкстра з купою
def dijkstra_heap(graph: AdjList, start: Node) -> Tuple[Dict[Node, float], Dict[Node, Optional[Node]]]:
    
    #Обчислює найкоротші відстані від start до всіх вершин.
    #Повертає (dist, prev), де:
    #  dist[v] — найкоротша відстань,
    #  prev[v] — попередник у найкоротшому шляху (або None для start/недосяжних).
    
    dist: Dict[Node, float] = {v: math.inf for v in graph.keys()}
    prev: Dict[Node, Optional[Node]] = {v: None for v in graph.keys()}
    if start not in graph:
        raise KeyError(f"Початкова вершина {start!r} відсутня у графі")

    dist[start] = 0.0
    heap: List[Tuple[float, Node]] = [(0.0, start)]  # (динамічна оцінка, вершина)

    while heap:
        d_u, u = heapq.heappop(heap)
        if d_u != dist[u]:
            # пропускаємо "застарілий" запис
            continue

        for v, w in graph[u]:
            nd = d_u + w
            if nd < dist[v]:
                dist[v] = nd
                prev[v] = u
                heapq.heappush(heap, (nd, v))

    return dist, prev

def reconstruct_path(prev: Dict[Node, Optional[Node]], start: Node, goal: Node) -> List[Node]:
    #Відновлює шлях start→goal за prev. Якщо недосяжно — повертає порожній список
    path: List[Node] = []
    cur: Optional[Node] = goal
    while cur is not None:
        path.append(cur)
        if cur == start:
            break
        cur = prev.get(cur)
    path.reverse()
    if not path or path[0] != start:
        return []  # недосяжно
    return path

#Демо-граф
DEMO_EDGES: List[Tuple[Node, Node, Weight]] = [
    ("A", "B", 4),
    ("A", "C", 2),
    ("B", "C", 5),
    ("B", "D", 10),
    ("C", "E", 3),
    ("E", "D", 4),
    ("D", "F", 11),
    ("E", "F", 5),
]

#CLI
def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Алгоритм Дейкстри з бінарною купою")
    ap.add_argument("--csv", type=str, help="Шлях до CSV з ребрами (u,v,w). Якщо не задано — використовуємо демо-граф.")
    ap.add_argument("--directed", action="store_true", help="Вважати граф орієнтованим (за замовчуванням — ні).")
    ap.add_argument("--start", type=str, default="A", help="Початкова вершина (за замовчуванням A).")
    ap.add_argument("--goal", type=str, help="Опційно: вивести шлях до цієї вершини.")
    return ap.parse_args()

def main() -> None:
    args = parse_args()

    if args.csv:
        edges = load_edges_csv(args.csv)
    else:
        edges = DEMO_EDGES

    g = make_graph(edges, directed=args.directed)
    dist, prev = dijkstra_heap(g, args.start)

    #Друк відстаней
    print("=== Найкоротші відстані від", args.start, "===")
    for v in sorted(g.keys()):
        d = dist.get(v, math.inf)
        print(f"{v}: {'∞' if math.isinf(d) else round(d, 6)}")

    #Якщо задано goal — вивести шлях
    if args.goal:
        path = reconstruct_path(prev, args.start, args.goal)
        if not path:
            print(f"\nШлях {args.start}→{args.goal}: недосяжно")
        else:
            L = dist[args.goal]
            print(f"\nШлях {args.start}→{args.goal}: {' -> '.join(path)} (довжина = {round(L,6)})")

if __name__ == "__main__":
    main()