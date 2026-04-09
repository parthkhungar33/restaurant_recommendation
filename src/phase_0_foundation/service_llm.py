from abc import ABC, abstractmethod
from typing import Any


class LLMProvider(ABC):
    """Provider interface for future LLM integrations."""

    @abstractmethod
    def complete(self, prompt: str, **kwargs: Any) -> str:
        raise NotImplementedError
