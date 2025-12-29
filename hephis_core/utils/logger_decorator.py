
import logging
import time
import traceback
import inspect
import asyncio
from functools import wraps
from typing import Iterable, Optional


# ---------------------------------------------------------
# DECORATOR FACTORY
# ---------------------------------------------------------

def log_action(action=None, *, meta_fields=None, logger_name="hephislog.action"):
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

    return decorator