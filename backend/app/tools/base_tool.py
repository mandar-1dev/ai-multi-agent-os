import time
import logging
from abc import ABC, abstractmethod
from typing import Any

logger = logging.getLogger("agentos.tools")


class ToolResult:
    def __init__(self, success: bool, data: Any = None, error: str = None, duration_ms: float = 0.0):
        self.success = success
        self.data = data
        self.error = error
        self.duration_ms = duration_ms

    def to_dict(self) -> dict:
        return {
            "success": self.success,
            "data": self.data,
            "error": self.error,
            "duration_ms": round(self.duration_ms, 2),
        }


class BaseTool(ABC):
    name: str = "base_tool"
    description: str = "Base tool"

    @abstractmethod
    def validate(self, **kwargs) -> tuple[bool, str | None]:
        """Return (is_valid, error_message)."""
        raise NotImplementedError

    @abstractmethod
    def _run(self, **kwargs) -> Any:
        raise NotImplementedError

    def run(self, **kwargs) -> ToolResult:
        start = time.time()
        ok, err = self.validate(**kwargs)
        if not ok:
            return ToolResult(False, None, err, (time.time() - start) * 1000)
        try:
            data = self._run(**kwargs)
            return ToolResult(True, data, None, (time.time() - start) * 1000)
        except Exception as e:  # noqa: BLE001
            logger.exception("Tool %s failed", self.name)
            return ToolResult(False, None, str(e), (time.time() - start) * 1000)
