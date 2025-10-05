#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#Завдання 4. Візуалізація бінарної купи.

#- Бере масив (array) і малює дерево купи (індекс i -> діти 2i+1, 2i+2)
#- Підтримує min-heap та max-heap режим
#- Виділяє порушення heap-властивості червоним (tomato)
#- Може зберегти у PNG (--outfile) і/або показати вікно (--show)

#Приклади:
#    python3 task4_heap_visualize.py --heap "10 14 20 28 18 25 32" --mode min --show
#    python3 task4_heap_visualize.py --heap "42 39 30 18 27 11" --mode max --outfile heap.png
#    python3 task4_heap_visualize.py --random 15 --mode min --heapify --show

from __future__ import annotations

import argparse
import math
import random
import uuid
from typing import List, Tuple, Optional

import matplotlib.pyplot as plt
import networkx as nx
from matplotlib import cm

#Базові класи/функції з ТЗ (адаптовано)

class Node:
    def __init__(self, key, color="skyblue", label=None):
        self.left: Optional["Node"] = None
        self.right: Optional["Node"] = None
        self.val = key
        self.color = color             # колір вузла
        self.id = str(uuid.uuid4())    # унікальний id
        self.label = label if label is not None else key  # що показувати на рисунку

def add_edges(graph, node, pos, x=0.0, y=0.0, layer=1):
    
    #Рекурсивно додає вузли/ребра у граф та координати для візуалізації.
    #Виставляє дітей ліворуч/праворуч на відстані ~ 1/(2^layer).
    
    if node is None:
        return graph

    graph.add_node(node.id, color=node.color, label=str(node.label))

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

def draw_tree(tree_root: Node, title: str = "Бінарна купа", figsize=(10, 6), outfile: str | None = None, show=False):
    #Малює дерево через networkx#
    tree = nx.DiGraph()
    pos = {tree_root.id: (0, 0)}
    add_edges(tree, tree_root, pos)

    colors = [node[1]['color'] for node in tree.nodes(data=True)]
    labels = {node[0]: node[1]['label'] for node in tree.nodes(data=True)}

    plt.figure(figsize=figsize)
    nx.draw(
        tree, pos=pos, labels=labels, arrows=False,
        node_size=2000, node_color=colors, linewidths=1.0, edgecolors="black"
    )
    plt.title(title)
    if outfile:
        plt.savefig(outfile, dpi=200, bbox_inches="tight")
    if show:
        plt.show()
    plt.close()

#Побудова дерева з масиву купи

def level_of(i: int) -> int:
    #Рівень вузла за індексом (root=0 -> рівень 0)
    return int(math.floor(math.log2(i + 1)))

def heap_property_ok(arr: List[float], i: int, mode: str) -> bool:
    
    #Перевіряє heap-властивість для вузла i:
    #  - min-heap: parent <= children
    #  - max-heap: parent >= children

    n = len(arr)
    left = 2 * i + 1
    right = 2 * i + 2

    if mode == "min":
        if left < n and arr[i] > arr[left]:
            return False
        if right < n and arr[i] > arr[right]:
            return False
    else:  # max
        if left < n and arr[i] < arr[left]:
            return False
        if right < n and arr[i] < arr[right]:
            return False
    return True

def build_heap_tree(arr: List[float], mode: str = "min", show_index=False, cmap_name="Blues") -> Optional[Node]:
    
    #Створює дерево Node з масиву купи.
    #Кольори за рівнями (градієнт), порушення heap-властивості — 'tomato'.
    
    if not arr:
        return None

    #Палітра за рівнем
    max_level = level_of(len(arr) - 1)
    cmap = cm.get_cmap(cmap_name)

    nodes: List[Optional[Node]] = [None] * len(arr)
    for i, val in enumerate(arr):
        lev = level_of(i)
        t = 0 if max_level == 0 else lev / max_level
        color = cmap(0.25 + 0.65 * (1 - t))  # верх темніший, низ світліший

        label = f"{i}:{val}" if show_index else f"{val}"
        if not heap_property_ok(arr, i, mode):
            color = "tomato"

        nodes[i] = Node(key=val, color=color, label=label)

    #Зв'язати дітей
    for i in range(len(arr)):
        left = 2 * i + 1
        right = 2 * i + 2
        if left < len(arr):
            nodes[i].left = nodes[left]
        if right < len(arr):
            nodes[i].right = nodes[right]

    return nodes[0]

#Допоміжне: heapify / генерація

def heapify_min(arr: List[int]) -> None:
    #Вбудований heapq — мін-купа
    import heapq
    heapq.heapify(arr)

def heapify_max(arr: List[int]) -> None:
    #Проста обгортка для max-heap через інверсію значень
    import heapq
    #Робимо max-heap: інвертуємо знаки, heapify, повертаємо назад
    neg = [-x for x in arr]
    heapq.heapify(neg)
    for i in range(len(arr)):
        arr[i] = -neg[i]

#CLI

def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Візуалізація бінарної купи")
    ap.add_argument("--heap", type=str, help="Список чисел, напр.: '10 14 20 28 18 25 32'")
    ap.add_argument("--mode", choices=["min", "max"], default="min", help="Тип купи (min/max)")
    ap.add_argument("--heapify", action="store_true", help="Попередньо перетворити масив у коректну купу")
    ap.add_argument("--random", type=int, help="Згенерувати випадковий масив із N елементів (ігнорує --heap)")
    ap.add_argument("--low", type=int, default=1, help="Нижня межа генерації випадкових чисел (для --random)")
    ap.add_argument("--high", type=int, default=99, help="Верхня межа генерації випадкових чисел (для --random)")
    ap.add_argument("--show-index", action="store_true", help="Показувати індекс вузла разом зі значенням")
    ap.add_argument("--outfile", type=str, help="PNG-файл для збереження (наприклад, heap.png)")
    ap.add_argument("--show", action="store_true", help="Показати вікно з візуалізацією")
    return ap.parse_args()

def parse_heap_string(s: str) -> List[float]:
    parts = s.replace(",", " ").split()
    out: List[float] = []
    for p in parts:
        try:
            #спробуємо int, інакше float
            v = int(p)
        except ValueError:
            v = float(p)
        out.append(v)
    return out

def main() -> None:
    args = parse_args()

    if args.random:
        arr = [random.randint(args.low, args.high) for _ in range(args.random)]
    elif args.heap:
        arr = parse_heap_string(args.heap)
    else:
        #дефолтний приклад
        arr = [10, 14, 20, 28, 18, 25, 32]

    #За потреби — привести до валідної купи
    if args.heapify:
        if args.mode == "min":
            heapify_min(arr)
        else:
            heapify_max(arr)

    #Побудувати дерево
    root = build_heap_tree(arr, mode=args.mode, show_index=args.show_index, cmap_name="Blues")
    if root is None:
        print("Порожній масив — нема що малювати.")
        return

    title = f"Бінарна купа ({args.mode}-heap) — {len(arr)} елементів"
    draw_tree(root, title=title, outfile=args.outfile, show=args.show)

if __name__ == "__main__":
    main()