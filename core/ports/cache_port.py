from abc import ABC, abstractmethod


class ICache(ABC):
    @abstractmethod
    async def get(self, key: str) -> dict | None:
        ...

    @abstractmethod
    async def set(self, key: str, value: dict, ttl_seconds: int) -> None:
        ...
