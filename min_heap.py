"""A minimum heap for (expire_at, key) pairs."""


class MinHeap:
    """Keep the element with the earliest expiration at index zero."""

    def __init__(self):
        self.items = []

    def push(self, item):
        self.items.append(item)
        self._heapify_up(len(self.items) - 1)

    def pop(self):
        if not self.items:
            return None
        root = self.items[0]
        last = self.items.pop()
        if self.items:
            self.items[0] = last
            self._heapify_down(0)
        return root

    def peek(self):
        return None if not self.items else self.items[0]

    def size(self):
        return len(self.items)

    def _heapify_up(self, index):
        while index > 0:
            parent = (index - 1) // 2
            if self.items[parent] <= self.items[index]:
                break
            self.items[parent], self.items[index] = self.items[index], self.items[parent]
            index = parent

    def _heapify_down(self, index):
        length = len(self.items)
        while True:
            left = index * 2 + 1
            right = left + 1
            smallest = index

            if left < length and self.items[left] < self.items[smallest]:
                smallest = left
            if right < length and self.items[right] < self.items[smallest]:
                smallest = right
            if smallest == index:
                return

            self.items[index], self.items[smallest] = self.items[smallest], self.items[index]
            index = smallest

