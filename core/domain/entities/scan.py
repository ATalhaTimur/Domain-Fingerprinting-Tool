from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from core.domain.entities.domain_target import DomainTarget
from core.domain.entities.risk_score import RiskScore


class ScanStatus(Enum):
    PENDING   = "pending"
    RUNNING   = "running"
    COMPLETED = "completed"
    FAILED    = "failed"


@dataclass
class Scan:
    id:           str
    target:       DomainTarget
    status:       ScanStatus       = ScanStatus.PENDING
    risk_score:   RiskScore        = field(default_factory=RiskScore.zero)
    raw_data:     dict             = field(default_factory=dict)
    created_at:   datetime         = field(default_factory=datetime.utcnow)
    completed_at: datetime | None  = None

    def complete(self, raw_data: dict, risk_score: RiskScore) -> None:
        self.raw_data     = raw_data
        self.risk_score   = risk_score
        self.status       = ScanStatus.COMPLETED
        self.completed_at = datetime.utcnow()

    def fail(self, reason: str) -> None:
        self.status = ScanStatus.FAILED
        self.raw_data["failure_reason"] = reason
