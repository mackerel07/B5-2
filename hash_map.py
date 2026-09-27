"""A hash map implemented with a custom hash function and separate chaining."""

from doubly_linked_list import DoublyLinkedList


class HashMap:
    """Store key-value pairs in linked-list buckets."""

    def __init__(self, capacity=8):
        self.capacity = capacity
        self.buckets = [DoublyLinkedList() for _ in range(capacity)]
        self.count = 0

    def _hash(self, key):
        value = 0
        for byte in key.encode("utf-8"):
            value = (value * 31 + byte) & 0xFFFFFFFF
        return value % self.capacity

    def _find_node(self, key):
        node = self.buckets[self._hash(key)].head
        while node is not None:
            if node.data[0] == key:
                return node
            node = node.next
        return None

    def put(self, key, value):
        node = self._find_node(key)
        if node is not None:
            node.data = (key, value)
            return

        self.buckets[self._hash(key)].insert_back((key, value))
        self.count += 1
        if self.count / self.capacity > 0.75:
            self._resize()

    def get(self, key):
        node = self._find_node(key)
        return None if node is None else node.data[1]

    def remove(self, key):
        index = self._hash(key)
        node = self.buckets[index].head
        while node is not None:
            if node.data[0] == key:
                value = node.data[1]
                self.buckets[index].remove_node(node)
                self.count -= 1
                return value
            node = node.next
        return None

    def contains(self, key):
        return self._find_node(key) is not None

    def keys(self):
        result = []
        for bucket in self.buckets:
            node = bucket.head
            while node is not None:
                result.append(node.data[0])
                node = node.next
        return result

    def size(self):
        return self.count

    def _resize(self):
        old_buckets = self.buckets
        self.capacity *= 2
        self.buckets = [DoublyLinkedList() for _ in range(self.capacity)]
        self.count = 0

        for bucket in old_buckets:
            node = bucket.head
            while node is not None:
                key, value = node.data
                self.buckets[self._hash(key)].insert_back((key, value))
                self.count += 1
                node = node.next

