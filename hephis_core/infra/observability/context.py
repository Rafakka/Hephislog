from contextvars import ContextVar
from typing import Optional
from .run_context import RunContext

current_run: ContextVar[Optional[RunContext]]=ContextVar(
    "current_run",
    default=None
)