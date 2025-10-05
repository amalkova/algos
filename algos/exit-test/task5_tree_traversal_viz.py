#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#Завдання 5. Візуалізація обходу бінарного дерева (BFS/DFS) БЕЗ рекурсії.

#- Будуємо дерево з масиву (i -> діти 2i+1, 2i+2), як у завданні 4.
#- Обхід у ширину (BFS) через чергу та у глибину (DFS) через стек.
#- Кожен вузол отримує унікальний колір у 16-ковому RGB (#RRGGBB) за порядком відвідування:
#  темний -> світлий (градієнт).
#- За бажанням додаємо до підпису порядковий номер відвідування.

#Приклади:
#    python3 task5_tree_traversal_viz.py --tree "0 4 1 5 10 3" --mode bfs --annotate --show
#    python3 task5_tree_traversal_viz.py --random 15 --mode dfs --outfile dfs.png

from __future__ import annotations
from collections import deque
from dataclasses import dataclass
from typing import Optional, List, Tuple, Iterable

import argparse
import math
import random
import uuid

import matplotlib.pyplot as plt
import networkx as nx

#Модель вузла і малювання

@dataclass
class Node:
    val: str
    left: Optional["Node"] = None
    right: Optional["Node"] = None
    color: str = "#87CEEB"                # skyblue за замовчуванням
    label: str = ""                        # що малювати всередині
    id: str = ""

    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())
        if not self.label:
            self.label = str(self.val)

def add_edges(graph, node, pos, x=0.0, y=0.0, layer=1):
    #Рекурсивно формує структуру для networkx (тільки для малювання)
    if node is None:
        return graph
    graph.add_node(node.id, color=node.color, label=node.label)
    if node.left:
        graph.add_edge(node.id, node.left.id)
        xl = x - 1 / (2 ** layer)
        pos[node.left.id] = (xl, y - 1)
        add_edges(graph, node.left, pos, x=xl, y=y - 1, layer=layer + 1)
    if node.right:
        graph.add_edge(node.id, node.right.id)
        xr = x + 1 / (2 ** layer)
        pos[node.right.id] = (xr, y - 1)
        add_edges(graph, node.right, pos, x=xr, y=y - 1, layer=layer + 1)
    return graph

def draw_tree(tree_root: Node, title: str, figsize=(10, 6), outfile: str | None = None, show=False):
    #Малює дерево із кольорами та підписами
    tree = nx.DiGraph()
    pos = {tree_root.id: (0, 0)}
    add_edges(tree, tree_root, pos)

    colors = [d["color"] for _, d in tree.nodes(data=True)]
    labels = {n: d["label"] for n, d in tree.nodes(data=True)}

    plt.figure(figsize=figsize)
    nx.draw(
        tree, pos=pos, labels=labels, arrows=False,
        node_size=2000, node_color=colors, edgecolors="black", linewidths=1.0
    )
    plt.title(title)
    if outfile:
        plt.savefig(outfile, dpi=200, bbox_inches="tight")
    if show:
        plt.show()
    plt.close()

#Побудова дерева з масиву

def level_of(i: int) -> int:
    return int(math.floor(math.log2(i + 1)))

def parse_tree_string(s: str) -> List[Optional[str]]:
    
    #Розбір рядка виду "0 4 1 5 10 3 None" → список значень;
    #'None', 'null', '_' трактуються як відсутній вузол.
    
    parts = s.replace(",", " ").split()
    out: List[Optional[str]] = []
    for p in parts:
        if p.lower() in ("none", "null", "_"):
            out.append(None)
        else:
            out.append(p)
    return out

def build_tree_from_array(arr: List[Optional[str]], show_index=False) -> Optional[Node]:
    
    #Створює COMPLETE-дерево з масиву arr (можливі None для «дір»).
    
    if not arr:
        return None
    nodes: List[Optional[Node]] = [None] * len(arr)
    for i, val in enumerate(arr):
        if val is None:
            continue
        label = f"{i}:{val}" if show_index else str(val)
        nodes[i] = Node(val=str(val), label=label)

    for i in range(len(arr)):
        if nodes[i] is None:
            continue
        li, ri = 2 * i + 1, 2 * i + 2
        if li < len(arr):
            nodes[i].left = nodes[li]
        if ri < len(arr):
            nodes[i].right = nodes[ri]
    return nodes[0]

#Градієнт кольорів (hex)

def _hex_to_rgb(h: str) -> Tuple[int, int, int]:
    h = h.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)

def _rgb_to_hex(rgb: Tuple[int, int, int]) -> str:
    r, g, b = rgb
    return f"#{r:02X}{g:02X}{b:02X}"

def hex_gradient(start: str, end: str, n: int) -> List[str]:

    #Лінійний градієнт з start → end, повертає список hex-кольорів довжини n
    
    if n <= 0:
        return []
    if n == 1:
        return [start]
    r1, g1, b1 = _hex_to_rgb(start)
    r2, g2, b2 = _hex_to_rgb(end)
    out = []
    for i in range(n):
        t = i / (n - 1)
        r = int(round(r1 + (r2 - r1) * t))
        g = int(round(g1 + (g2 - g1) * t))
        b = int(round(b1 + (b2 - b1) * t))
        out.append(_rgb_to_hex((r, g, b)))
    return out

#Обходи без рекурсії

def traverse_bfs(root: Optional[Node]) -> List[Node]:
    #Обхід у ширину (черга)
    order: List[Node] = []
    if root is None:
        return order
    q: deque[Node] = deque([root])
    while q:
        u = q.popleft()
        order.append(u)
        if u.left:
            q.append(u.left)
        if u.right:
            q.append(u.right)
    return order

def traverse_dfs(root: Optional[Node]) -> List[Node]:
    #Обхід у глибину (стек) — префіксний: root, left, right
    order: List[Node] = []
    if root is None:
        return order
    stack: List[Node] = [root]
    while stack:
        u = stack.pop()
        order.append(u)
        #Спочатку кладемо right, потім left — щоб першим дістати left
        if u.right:
            stack.append(u.right)
        if u.left:
            stack.append(u.left)
    return order

def colorize_by_order(root: Optional[Node], order: List[Node], annotate=False) -> None:
    
    #Присвоює кольори вузлам згідно порядку відвідування:
    #темний -> світлий (від #08306B до #BDD7E7).
    
    if not order:
        return
    colors = hex_gradient("#08306B", "#BDD7E7", len(order))
    for i, node in enumerate(order):
        node.color = colors[i]
        if annotate:
            node.label = f"{node.label}\n#{i+1}"  # додаємо порядковий номер

#CLI / MAIN

def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Візуалізація BFS/DFS без рекурсії")
    ap.add_argument("--tree", type=str, help="Список значень (можна 'None'): напр. '0 4 1 5 10 3'")
    ap.add_argument("--random", type=int, help="Згенерувати випадкове дерево з N вузлів")
    ap.add_argument("--low", type=int, default=0, help="Нижня межа випадкових значень (для --random)")
    ap.add_argument("--high", type=int, default=99, help="Верхня межа випадкових значень (для --random)")
    ap.add_argument("--mode", choices=["bfs", "dfs"], default="bfs", help="Тип обходу")
    ap.add_argument("--annotate", action="store_true", help="Додати до мітки порядковий номер відвідування")
    ap.add_argument("--show-index", action="store_true", help="Показувати індекс у мітці (формат i:val)")
    ap.add_argument("--outfile", type=str, help="PNG-файл для збереження рисунку")
    ap.add_argument("--show", action="store_true", help="Показати вікно з рисунком")
    return ap.parse_args()

def main() -> None:
    args = parse_args()

    #Джерело дерева
    if args.random:
        arr = [str(random.randint(args.low, args.high)) for _ in range(args.random)]
    elif args.tree:
        arr = parse_tree_string(args.tree)
    else:
        #дефолтний приклад з ТЗ
        arr = ["0", "4", "1", "5", "10", "3"]

    root = build_tree_from_array(arr, show_index=args.show_index)
    if root is None:
        print("Порожнє дерево — нема що обходити.")
        return

    # Обхід (без рекурсії)
    if args.mode == "bfs":
        order = traverse_bfs(root)
        title = "Обхід у ширину (BFS)"
    else:
        order = traverse_dfs(root)
        title = "Обхід у глибину (DFS)"

    # Розфарбувати й (опційно) підписати порядковий номер
    colorize_by_order(root, order, annotate=args.annotate)

    # Візуалізація
    draw_tree(root, title=title, outfile=args.outfile, show=args.show)

if __name__ == "__main__":
    main()