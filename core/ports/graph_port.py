from abc import ABC, abstractmethod

from core.domain.entities.threat_graph import ThreatGraph


class IGraphBuilder(ABC):
    @abstractmethod
    def build(self, raw_data: dict) -> ThreatGraph:
        ...
