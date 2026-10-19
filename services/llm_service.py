"""Optional Local LLM Service for EduPilot AI.

Provides optional local Ollama integration for natural language synthesis
without requiring any paid API keys or cloud services.
Defaults gracefully to deterministic synthesis if Ollama is unavailable.
"""

from typing import Any, Dict, Optional
import httpx


class LLMService:
    """Optional local LLM client interfacing with local Ollama daemon."""

    def __init__(self, host: str = "http://localhost:11434", model: str = "llama3:latest"):
        self.host = host
        self.model = model
        self._available: Optional[bool] = None

    def is_available(self) -> bool:
        """Check whether local Ollama server is running and accessible."""
        if self._available is not None:
            return self._available
        try:
            r = httpx.get(f"{self.host}/api/tags", timeout=1.0)
            self._available = r.status_code == 200
        except Exception:
            self._available = False
        return self._available

    def generate_intervention_commentary(
        self, student_id: str, concerns: list, interventions: list
    ) -> str:
        """Generate optional natural language synthesis if Ollama is running."""
        if not self.is_available():
            return (
                "Operating in Deterministic Engine Mode. All calculations, rules, "
                "and recommendations were generated deterministically by the 4 specialized agents."
            )

        prompt = (
            f"You are EduPilot AI. Summarize the following academic findings for student {student_id}. "
            f"Concerns: {concerns}. Interventions: {interventions}. "
            f"Keep it objective, concise, and pedagogical."
        )

        try:
            r = httpx.post(
                f"{self.host}/api/generate",
                json={"model": self.model, "prompt": prompt, "stream": False},
                timeout=5.0,
            )
            if r.status_code == 200:
                return r.json().get("response", "").strip()
        except Exception:
            pass

        return "Operating in Deterministic Engine Mode."


llm_service = LLMService()
