#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#BST: просте двійкове дерево пошуку для цілих чисел.
#Завдання 1: знайти мінімальне значення (ліва «гілка» до кінця).
#Завдання 2: знайти суму всіх значень (DFS).

#Функції готові до прямого використання:
#- insert_bst(root, value) -> BSTNode : вставка
#- find_min_value(root) -> int        : мінімум у дереві
#- sum_values(root) -> int            : сума всіх значень

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Iterable

@dataclass
class BSTNode:
    value: int
    left: Optional["BSTNode"] = None
    right: Optional["BSTNode"] = None


def insert_bst(root: Optional[BSTNode], value: int) -> BSTNode:
    #Вставка значення у BST. Повертає корінь (може змінитись, якщо root=None)
    if root is None:
        return BSTNode(value)
    cur = root
    while True:
        if value < cur.value:
            if cur.left is None:
                cur.left = BSTNode(value)
                break
            cur = cur.left
        else:
            # для простоти: рівні значення кладемо вправо
            if cur.right is None:
                cur.right = BSTNode(value)
                break
            cur = cur.right
    return root


def build_bst(values: Iterable[int]) -> Optional[BSTNode]:
    #Зручний конструктор дерева зі списку чисел
    root: Optional[BSTNode] = None
    for v in values:
        root = insert_bst(root, int(v))
    return root


# Завдання 1: мінімальне значення у BST/AVL

def find_min_value(root: Optional[BSTNode]) -> int:
    #Повертає мінімальне значення у дереві.
    #Ідеї: у BST найменший елемент — крайній лівий вузол
  
    if root is None:
        raise ValueError("Дерево порожнє — немає мінімального значення.")
    node = root
    while node.left is not None:
        node = node.left
    return node.value


# Завдання 2: сума всіх значень

def sum_values(root: Optional[BSTNode]) -> int:
    #Повертає суму всіх значень у дерево (рекурсивний DFS)
    if root is None:
        return 0
    return root.value + sum_values(root.left) + sum_values(root.right)