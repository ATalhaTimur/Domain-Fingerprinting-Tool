from dataclasses import dataclass


@dataclass(frozen=True)
class RiskScore:
    value: int

    def __post_init__(self) -> None:
        if not (0 <= self.value <= 100):
            raise ValueError(f"RiskScore must be 0–100, got {self.value}")

    @classmethod
    def zero(cls) -> "RiskScore":
        return cls(0)

    @property
    def level(self) -> str:
        if self.value >= 70:
            return "critical"
        if self.value >= 40:
            return "medium"
        return "low"
