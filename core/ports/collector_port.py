from abc import ABC, abstractmethod


class ICollector(ABC):
    @abstractmethod
    async def fetch(self, domain: str) -> dict:
        """Never raises — returns {'error': ...} on failure."""
        ...
