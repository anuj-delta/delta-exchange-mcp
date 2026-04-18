from __future__ import annotations

from typing import Any


class DeltaApiError(Exception):
    def __init__(self, code: str, context: Any = None, status: int | None = None):
        self.code = code
        self.context = context
        self.status = status
        msg = f"delta api error: {code}"
        if context:
            msg += f" (context={context})"
        if status:
            msg += f" [http {status}]"
        super().__init__(msg)


class ConfigError(Exception):
    pass
