"""An advanced-level Python file for testing concept extraction."""

from __future__ import annotations

import asyncio
from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from dataclasses import dataclass
from functools import lru_cache


@dataclass(frozen=True)
class Config:
    host: str = "localhost"
    port: int = 8080
    timeout: float = 30.0


class Repository(ABC):
    @abstractmethod
    async def get(self, key: str) -> dict | None:
        ...

    @abstractmethod
    async def store(self, key: str, value: dict) -> None:
        ...


class InMemoryRepo(Repository):
    def __init__(self):
        self._store: dict[str, dict] = {}

    async def get(self, key: str) -> dict | None:
        return self._store.get(key)

    async def store(self, key: str, value: dict) -> None:
        self._store[key] = value


async def stream_data(urls: list[str]) -> AsyncIterator[dict]:
    for url in urls:
        try:
            data = {"url": url, "status": 200}
            yield data
        except Exception as e:
            raise RuntimeError(f"Failed to fetch {url}") from e


@lru_cache(maxsize=128)
def compute_hash(data: str) -> int:
    return hash(data)


def dispatch_command(cmd: str, **kwargs):
    match cmd.split():
        case ["read", path]:
            print(f"Reading {path}")
        case ["write", path, *content]:
            print(f"Writing {', '.join(content)} to {path}")
        case ["delete", path]:
            print(f"Deleting {path}")
        case _:
            print(f"Unknown command: {cmd}")


class ValidatedDescriptor:
    def __init__(self, validator):
        self.validator = validator
        self._name = ""

    def __set_name__(self, owner, name):
        self._name = name

    def __get__(self, obj, objtype=None):
        return obj.__dict__.get(self._name)

    def __set__(self, obj, value):
        if not self.validator(value):
            raise ValueError(f"Invalid value for {self._name}: {value}")
        obj.__dict__[self._name] = value


async def main():
    repo = InMemoryRepo()
    await repo.store("key1", {"value": 42})
    result = await repo.get("key1")
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
