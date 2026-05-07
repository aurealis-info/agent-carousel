"""Abstract base class for future auto-publish providers (Instagram, Buffer, etc.).

Empty in v2; reserved for v2.1 when auto-publish ships.
"""
from abc import ABC, abstractmethod
from pathlib import Path


class BasePublisher(ABC):
    @abstractmethod
    def publish(self, carousel_dir: Path, caption: str, hashtags: list[str]) -> dict:
        """Publish a finished carousel. Returns provider-specific result dict."""
