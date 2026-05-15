import os

import httpx

from core.ports.ai_port import IAIAnalyzer
from infrastructure.ai.prompts import PROMPTS


class ClaudeAnalyzer(IAIAnalyzer):
    MODEL = "claude-sonnet-4-20250514"

    async def analyze(self, relations_text: str, mode: str = "technical") -> str:
        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key":         os.getenv("ANTHROPIC_API_KEY"),
                    "anthropic-version": "2023-06-01",
                    "content-type":      "application/json",
                },
                json={
                    "model":      self.MODEL,
                    "max_tokens": 512,
                    "system":     PROMPTS.get(mode, PROMPTS["technical"]),
                    "messages": [{
                        "role":    "user",
                        "content": f"Analyze the following infrastructure relationships:\n\n{relations_text}",
                    }],
                },
            )
        return r.json()["content"][0]["text"]
