"""O(1) insertion, deletion, and movement for known list nodes."""


class Node:
    """A node with links to both neighboring nodes."""

    def __init__(self, data):
        self.prev = None
        self.next = None
        self.data = data


class DoublyLinkedList:
    """A doubly linked list that keeps direct references to both ends."""

    def __init__(self):
        self.head = None
        self.tail = None
        self.length = 0

    def insert_front(self, data):
        node = Node(data)
        node.next = self.head
        if self.head is None:
            self.tail = node
        else:
            self.head.prev = node
        self.head = node
        self.length += 1
        return node

    def insert_back(self, data):
        node = Node(data)
        node.prev = self.tail
        if self.tail is None:
            self.head = node
        else:
            self.tail.next = node
        self.tail = node
        self.length += 1
        return node

    def remove_front(self):
        if self.head is None:
            return None
        return self.remove_node(self.head)

    def remove_back(self):
        if self.tail is None:
            return None
        return self.remove_node(self.tail)

    def remove_node(self, node):
        if node.prev is None:
            self.head = node.next
        else:
            node.prev.next = node.next

        if node.next is None:
            self.tail = node.prev
        else:
            node.next.prev = node.prev

        node.prev = None
        node.next = None
        self.length -= 1
        return node

    def move_to_front(self, node):
        if node is self.head:
            return node
        self.remove_node(node)
        node.prev = None
        node.next = self.head
        if self.head is None:
            self.tail = node
        else:
            self.head.prev = node
        self.head = node
        self.length += 1
        return node

