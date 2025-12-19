# hephis_core/utils/logger_decorators.py
import logging
import time
import traceback
import inspect
import asyncio
from functools import wraps
from typing import Iterable, Optional

# ---------------------------------------------------------
# Helper: determine success from returned dicts
# ---------------------------------------------------------
def determine_success(result):
    if isinstance(result, dict) and "success" in result:
        return bool(result["success"])
    return True


# ---------------------------------------------------------
# Helper: summarize complex results
# ---------------------------------------------------------
def summarize_result(result):
    if isinstance(result, dict):
        return result
    if isinstance(result, (str, int, float, list)):
        return {"value": str(result)}
    return {"type": type(result).__name__}


# ---------------------------------------------------------
# Helper: capture exception info
# ---------------------------------------------------------
def capture_exception(exc):
    return {
        "error": str(exc),
        "traceback": traceback.format_exc()
    }


# ---------------------------------------------------------
# Helper: build unified log payload
# ---------------------------------------------------------
def build_log_payload(action, meta, duration, success, result_summary=None, error_info=None):
    payload = {
        "action": action,
        "meta": meta,
        "duration_s": duration,
        "success": success
    }

    if success:
        payload["result_summary"] = result_summary
    else:
        payload["error"] = error_info["error"]
        payload["traceback"] = error_info["traceback"]

    return payload


# ---------------------------------------------------------
# Helper: extract named parameters from the call
# ---------------------------------------------------------

def extract_metadata(func, args, kwargs, fields):
    if not fields:
        return {}

    sig = inspect.signature(func)

    try:
        bound = sig.bind_partial(*args, **kwargs)
        bound.apply_defaults()
    except Exception:
        # Fallback: get metadata from kwargs only
        return {key: kwargs.get(key) for key in fields}

    meta = {}
    for key in fields:
        meta[key] = bound.arguments.get(key)
    return meta


# ---------------------------------------------------------
# DECORATOR FACTORY
# ---------------------------------------------------------

def log_action(action=None, *, meta_fields=None, logger_name="hephislog.action"):
    def decorator(func):
        logger = logging.getLogger(logger_name)
        act_name = action or func.__name__

        @wraps(func)
        async def unified_wrapper(*args, **kwargs):

            start = time.time()

            # Extract metadata
            meta = extract_metadata(func, args, kwargs, meta_fields)

            try:
                result = func(*args, **kwargs)

                if inspect.isawaitable(result):
                    result = await result

                duration = time.time() - start
                success = determine_success(result)

                payload = build_log_payload(
                    action=act_name,
                    meta=meta,
                    duration=duration,
                    success=success,
                    result_summary=summarize_result(result)
                )

                logger.info(f"{act_name} finished", extra=payload)
                return result

            except Exception as exc:
                # Build log on error
                duration = time.time() - start

                payload = build_log_payload(
                    action=act_name,
                    meta=meta,
                    duration=duration,
                    success=False,
                    error_info=capture_exception(exc)
                )

                logger.error(f"{act_name} failed", extra=payload)
                raise

        def sync_adapter(*args, **kwargs):
            return asyncio.run(unified_wrapper(*args, **kwargs))

        if inspect.iscoroutinefunction(func):
            return unified_wrapper
        else:
            return sync_adapter

    return decorator