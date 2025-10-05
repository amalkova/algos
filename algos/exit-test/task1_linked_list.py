#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#Завдання 1.
#Однозв’язний список:
#- reverse_inplace(head)
#- merge_two_sorted(a, b)
#- merge_sort(head)

#Демо запуск:
#    python3 task1_linked_list.py

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Iterable, Tuple

@dataclass
class Node:
    value: int
    next: Optional["Node"] = None

#helpers

def build_list(items: Iterable[int]) -> Optional[Node]:
    #Створити список з python-ітерабельного
    head: Optional[Node] = None
    tail: Optional[Node] = None
    for x in items:
        n = Node(int(x))
        if head is None:
            head = tail = n
        else:
            assert tail is not None
            tail.next = n
            tail = n
    return head

def to_pylist(head: Optional[Node]) -> list[int]:
    out: list[int] = []
    cur = head
    while cur:
        out.append(cur.value)
        cur = cur.next
    return out

#tasks

def reverse_inplace(head: Optional[Node]) -> Optional[Node]:
    #Реверсування однозв’язного списку in-place (O(n) час, O(1) пам'ять)#
    prev: Optional[Node] = None
    cur = head
    while cur:
        nxt = cur.next
        cur.next = prev
        prev = cur
        cur = nxt
    return prev

def split_middle(head: Node) -> Tuple[Node, Optional[Node]]:
    
    #Розбити список на дві половини (slow/fast). Повертає (ліва_голова, права_голова).
    #Якщо довжина непарна — ліва на 1 елемент довша.
    
    slow = head
    fast = head
    prev: Optional[Node] = None
    while fast and fast.next:
        prev = slow
        slow = slow.next  # type: ignore
        fast = fast.next.next
    #тепер slow — початок правої половини; prev — кінець лівої
    if prev:
        prev.next = None
    return head, slow

def merge_two_sorted(a: Optional[Node], b: Optional[Node]) -> Optional[Node]:
    #Злиття двох ВІДСОРТОВАНИХ списків у один відсортований (O(n+m))
    dummy = Node(0)
    tail = dummy
    pa, pb = a, b
    while pa and pb:
        if pa.value <= pb.value:
            tail.next = pa
            pa = pa.next
        else:
            tail.next = pb
            pb = pb.next
        tail = tail.next
    tail.next = pa if pa else pb
    return dummy.next

def merge_sort(head: Optional[Node]) -> Optional[Node]:
    #Сортування злиттям для однозв’язного списку (O(n log n))
    if head is None or head.next is None:
        return head
    left_head, right_head = split_middle(head)
    left_sorted = merge_sort(left_head)
    right_sorted = merge_sort(right_head)
    return merge_two_sorted(left_sorted, right_sorted)

#demo

def _demo():
    print("=== Демонстрація Завдання 1 (однозв’язний список) ===")

    data = [7, 3, 9, 1, 5, 8, 10]
    head = build_list(data)
    print("Початковий:", to_pylist(head))

    #1) reverse
    rev = reverse_inplace(head)
    print("Реверс:", to_pylist(rev))

    #Щоб показати сортування — повернемо назад у початковому порядку
    head = reverse_inplace(rev)

    #2) merge sort
    sorted_head = merge_sort(head)
    print("Після merge-sort:", to_pylist(sorted_head))

    #3) merge two sorted
    a = build_list([1, 4, 6, 9])
    b = build_list([0, 2, 3, 7, 10])
    merged = merge_two_sorted(a, b)
    print("Злиття двох відсортованих:", to_pylist(merged))

if __name__ == "__main__":
    _demo()