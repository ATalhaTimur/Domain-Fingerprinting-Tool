import re
from dataclasses import dataclass


_DOMAIN_RE = re.compile(
    r'^([a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$'
)


@dataclass(frozen=True)
class DomainTarget:
    value: str

    def __post_init__(self) -> None:
        if not _DOMAIN_RE.match(self.value):
            raise ValueError(f"Invalid domain: {self.value}")

    @classmethod
    def from_url(cls, raw: str) -> "DomainTarget":
        domain = re.sub(r'^https?://', '', raw).split('/')[0].split('?')[0]
        return cls(domain)
