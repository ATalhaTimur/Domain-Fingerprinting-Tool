from pydantic import BaseModel


class ScanRequestDTO(BaseModel):
    target: str
    mode: str = "technical"
