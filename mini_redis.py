"""The required in-memory Mini Redis commands, LRU eviction, and TTL handling."""

import time

from doubly_linked_list import DoublyLinkedList
from hash_map import HashMap
from min_heap import MinHeap


INTEGER_ERROR = "(error) ERR value is not an integer or out of range"
OOM_ERROR = "(error) OOM command not allowed when used_memory > 'maxmemory'"


class MiniRedis:
    """A small Redis-like string store backed by custom data structures."""

    def __init__(self):
        self.data = HashMap()
        self.lru = DoublyLinkedList()
        self.lru_nodes = HashMap()
        self.expirations = HashMap()
        self.expiration_heap = MinHeap()
        self.used_memory = 0
        self.maxmemory = 0
        self.evicted_keys = 0

    @staticmethod
    def _entry_size(key, value):
        return len(key.encode("utf-8")) + len(value.encode("utf-8"))

    @staticmethod
    def _quote(value):
        escaped = value.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{escaped}"'

    def _touch(self, key):
        node = self.lru_nodes.get(key)
        if node is None:
            node = self.lru.insert_front(key)
            self.lru_nodes.put(key, node)
        else:
            self.lru.move_to_front(node)

    def _delete_key(self, key):
        if not self.data.contains(key):
            return False

        value = self.data.remove(key)
        self.used_memory -= self._entry_size(key, value)
        node = self.lru_nodes.remove(key)
        if node is not None:
            self.lru.remove_node(node)
        self.expirations.remove(key)
        return True

    def _delete_if_expired(self, key):
        expire_at = self.expirations.get(key)
        if expire_at is not None and expire_at <= time.time():
            self._delete_key(key)
            return True
        return False

    def _purge_expired(self):
        now = time.time()
        while self.expiration_heap.peek() is not None:
            expire_at, key = self.expiration_heap.peek()
            if expire_at > now:
                return
            self.expiration_heap.pop()
            current = self.expirations.get(key)
            if current == expire_at:
                self._delete_key(key)

    def set(self, key, value):
        self._purge_expired()
        entry_size = self._entry_size(key, value)
        if self.maxmemory > 0 and entry_size > self.maxmemory:
            return OOM_ERROR

        if self.data.contains(key):
            self.used_memory -= self._entry_size(key, self.data.get(key))

        self.data.put(key, value)
        self.used_memory += entry_size
        self.expirations.remove(key)
        self._touch(key)

        while self.maxmemory > 0 and self.used_memory > self.maxmemory:
            oldest_key = self.lru.tail.data
            self._delete_key(oldest_key)
            self.evicted_keys += 1
        return "OK"

    def get(self, key):
        if self._delete_if_expired(key) or not self.data.contains(key):
            return "(nil)"
        value = self.data.get(key)
        self._touch(key)
        return self._quote(value)

    def delete(self, key):
        self._delete_if_expired(key)
        return "(integer) 1" if self._delete_key(key) else "(integer) 0"

    def exists(self, key):
        self._delete_if_expired(key)
        return "(integer) 1" if self.data.contains(key) else "(integer) 0"

    def dbsize(self):
        self._purge_expired()
        return f"(integer) {self.data.size()}"

    def keys(self):
        self._purge_expired()
        keys = self.data.keys()
        if not keys:
            return "(empty array)"
        return "\n".join(f"{index}. {self._quote(key)}" for index, key in enumerate(keys, 1))

    def config_set_maxmemory(self, value):
        try:
            number = int(value)
        except ValueError:
            return INTEGER_ERROR
        if number < 0:
            return INTEGER_ERROR
        self.maxmemory = number
        return "OK"

    def info_memory(self):
        self._purge_expired()
        return (
            f"used_memory:{self.used_memory}\n"
            f"maxmemory:{self.maxmemory}\n"
            f"evicted_keys:{self.evicted_keys}"
        )

    def expire(self, key, seconds_text):
        try:
            seconds = int(seconds_text)
        except ValueError:
            return INTEGER_ERROR

        if self._delete_if_expired(key) or not self.data.contains(key):
            return "(integer) 0"
        if seconds <= 0:
            self._delete_key(key)
            return "(integer) 1"

        expire_at = time.time() + seconds
        self.expirations.put(key, expire_at)
        self.expiration_heap.push((expire_at, key))
        return "(integer) 1"

    def ttl(self, key):
        if self._delete_if_expired(key) or not self.data.contains(key):
            return "(integer) -2"
        expire_at = self.expirations.get(key)
        if expire_at is None:
            return "(integer) -1"
        return f"(integer) {max(0, int(expire_at - time.time()))}"

    def execute(self, parts):
        """Validate and execute one already-tokenized CLI command."""
        command = parts[0].upper()
        arguments = parts[1:]

        if command == "SET" and len(arguments) == 2:
            return self.set(arguments[0], arguments[1])
        if command == "GET" and len(arguments) == 1:
            return self.get(arguments[0])
        if command == "DEL" and len(arguments) == 1:
            return self.delete(arguments[0])
        if command == "EXISTS" and len(arguments) == 1:
            return self.exists(arguments[0])
        if command == "DBSIZE" and not arguments:
            return self.dbsize()
        if command == "KEYS" and not arguments:
            return self.keys()
        if command == "CONFIG" and len(arguments) == 3:
            if arguments[0].upper() == "SET" and arguments[1].lower() == "maxmemory":
                return self.config_set_maxmemory(arguments[2])
        if command == "INFO" and len(arguments) == 1:
            if arguments[0].lower() == "memory":
                return self.info_memory()
        if command == "EXPIRE" and len(arguments) == 2:
            return self.expire(arguments[0], arguments[1])
        if command == "TTL" and len(arguments) == 1:
            return self.ttl(arguments[0])

        known = ("SET", "GET", "DEL", "EXISTS", "DBSIZE", "KEYS", "CONFIG", "INFO", "EXPIRE", "TTL")
        if command in known:
            return f"(error) ERR wrong number of arguments for '{command}' command"
        return f"(error) ERR unknown command '{parts[0]}'"

