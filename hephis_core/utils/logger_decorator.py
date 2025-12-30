
import logging
import time
import traceback
import inspect
import asyncio
from functools import wraps
from typing import Iterable, Optional

from hephis_core.infra.observability.fact import Fact
from hephis_core.infra.observability.context import current_run


# ---------------------------------------------------------
# DECORATOR FACTORY
# ---------------------------------------------------------

def log_action(action:str, stage:str|None = None):

    def decorator(func):

        is_async = inspect.iscoroutinefunction(func)

        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start = time.start()
            meta = extract_metadata(func, args, kwargs, meta_fields)
            try:
                result = await func(*args,**kwargs)
                duration = time.time()-start
                logger.info(
                    f"{action} finished",
                    extra = build_log_payload(
                        action=action,
                        meta=meta,
                        duration=duration,
                        success=True,
                        result_summary=summarize_results(result),
                    ),
                )
                return result
            except Exception as exc:
                duration = time.time() - start
                logger.error(
                    f"{action} failed",
                    extra=build_log_payload(
                        action=action,
                        meta=meta,
                        duration=duration,
                        success=False,
                        error_info=capture_expetion(exc),
                    ),
                )
                raise

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start = time.time()
            meta = extract_metadata(func, args, kwargs, meta_fields)
            try:
                result = fun(*args, **kwargs)
                duration = time.time() - start
                logger_info(
                    extra=build_log_payload(
                        action=action,
                        meta=meta,
                        duration=duration,
                        success=True,
                        result_summary=summarize_results(result),
                    ),
                )
                return result
            except Exception as exc:
                    duration = time.time() - start
                    logger.error(
                        f"{action} failed",
                        extra=build_log_payload(
                            action=action,
                            meta=meta,
                            duration=duration,
                            success=False,
                            error_info=capture_expetion(exc),
                        ),
                    )
                    raise
            return async_wrapper if is_async else sync_wrapper

        @wraps(func)
        def wrapper(*args, **kwargs):

            ctx = current_run.get()
            component = func.__qualname__
            fact_stage = stage or action

            try:
                result = func(*args, **kwargs)

                if ctx is not None:
                    fact = Fact (
                        run_id=ctx.run_id,
                        stage=fact_stage,
                        component=component,
                        result="none" if result is None else "ok",
                        reason="returned none" if result is None else None,
                    ) 
                    ctx.add_fact(fact)
                return result
            except Exception as exc:
                if ctx is not None:
                    fact = Fact(
                    run_id=ctx.run_id,
                    stage=fact_stage, 
                    component=component,
                    result="error",
                    reason=exc.__class__.__name__,
                    )
                    ctx.add_fact(fact)
                raise

        return wrapper
        
    return decorator