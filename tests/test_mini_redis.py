"""Required behavior checks for the Mini Redis assignment."""

import time
import unittest

from doubly_linked_list import DoublyLinkedList
from hash_map import HashMap
from min_heap import MinHeap
from mini_redis import MiniRedis, OOM_ERROR


class DataStructureTests(unittest.TestCase):
    def test_doubly_linked_list_operations(self):
        linked = DoublyLinkedList()
        middle = linked.insert_front("middle")
        linked.insert_front("front")
        linked.insert_back("back")
        linked.move_to_front(middle)
        self.assertEqual(linked.head.data, "middle")
        self.assertEqual(linked.remove_front().data, "middle")
        self.assertEqual(linked.remove_back().data, "back")

    def test_hash_map_collision_and_resize(self):
        mapping = HashMap(2)
        mapping.put("a", "1")
        mapping.put("c", "2")
        self.assertEqual(mapping.capacity, 4)
        self.assertEqual(mapping.get("a"), "1")
        self.assertEqual(mapping.remove("c"), "2")

    def test_min_heap(self):
        heap = MinHeap()
        heap.push((3, "c"))
        heap.push((1, "a"))
        heap.push((2, "b"))
        self.assertEqual(heap.peek(), (1, "a"))
        self.assertEqual([heap.pop(), heap.pop(), heap.pop()], [(1, "a"), (2, "b"), (3, "c")])


class CommandTests(unittest.TestCase):
    def setUp(self):
        self.store = MiniRedis()

    def test_string_commands(self):
        self.assertEqual(self.store.set("name", "Alice"), "OK")
        self.assertEqual(self.store.get("name"), '"Alice"')
        self.assertEqual(self.store.exists("name"), "(integer) 1")
        self.assertEqual(self.store.dbsize(), "(integer) 1")
        self.assertIn('"name"', self.store.keys())
        self.assertEqual(self.store.delete("name"), "(integer) 1")
        self.assertEqual(self.store.get("name"), "(nil)")

    def test_lru_eviction_and_memory(self):
        self.store.config_set_maxmemory("6")
        self.store.set("a", "11")
        self.store.set("b", "22")
        self.store.get("a")
        self.store.set("c", "33")
        self.assertEqual(self.store.exists("a"), "(integer) 1")
        self.assertEqual(self.store.exists("b"), "(integer) 0")
        self.assertEqual(self.store.used_memory, 6)
        self.assertEqual(self.store.evicted_keys, 1)

    def test_oversized_entry_is_rejected_without_changing_old_value(self):
        self.store.set("a", "old")
        self.store.config_set_maxmemory("3")
        self.assertEqual(self.store.set("a", "large"), OOM_ERROR)
        self.assertEqual(self.store.get("a"), '"old"')

    def test_ttl_and_overwrite_reset(self):
        self.store.set("key", "value")
        self.assertEqual(self.store.ttl("key"), "(integer) -1")
        self.assertEqual(self.store.expire("key", "1"), "(integer) 1")
        self.assertIn(self.store.ttl("key"), ("(integer) 0", "(integer) 1"))
        self.store.set("key", "new")
        self.assertEqual(self.store.ttl("key"), "(integer) -1")
        self.store.expire("key", "0")
        self.assertEqual(self.store.ttl("key"), "(integer) -2")

    def test_expired_key_is_removed_without_lru_update(self):
        self.store.set("old", "value")
        node = self.store.lru_nodes.get("old")
        self.store.expirations.put("old", time.time() - 1)
        self.assertEqual(self.store.get("old"), "(nil)")
        self.assertIsNone(node.prev)
        self.assertIsNone(node.next)

    def test_errors(self):
        self.assertTrue(self.store.execute(["HELLO"]).startswith("(error) ERR unknown command"))
        self.assertTrue(self.store.execute(["GET"]).startswith("(error) ERR wrong number"))
        self.assertEqual(self.store.config_set_maxmemory("abc"), "(error) ERR value is not an integer or out of range")


if __name__ == "__main__":
    unittest.main()

