from abc import ABC, abstractmethod


class IAIAnalyzer(ABC):
    @abstractmethod
    async def analyze(self, relations_text: str, mode: str) -> str:
        ...
