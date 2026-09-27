"""Command-line REPL for Mini Redis."""

import shlex

from mini_redis import MiniRedis


def main():
    store = MiniRedis()
    while True:
        try:
            line = input("mini-redis> ")
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if line.strip().lower() in ("exit", "quit"):
            break
        try:
            parts = shlex.split(line)
        except ValueError as error:
            print(f"(error) ERR {error}")
            continue
        if parts:
            print(store.execute(parts))


if __name__ == "__main__":
    main()

