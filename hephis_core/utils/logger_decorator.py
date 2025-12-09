# hephis_core/utils/logger_decorators.py
import logging
import time
import traceback
import inspect
from functools import wraps
from typing import Iterable, Optional

DEFAULT_LOGGER = "hephislog.deletion"

def determine_success(result):
    if isinstance(result, dict) and "success" in result:
        return bool(result.get("success"))
    return True

def summarize_result(result):
    if not isinstance(result, (str, int, float, dict, list)):
        return {"type": type(result).__name__}
    elif isinstance(result, dict):
        return result
    else:
        return {"value": str(result)}

def capture_exception(exc):
    error = str(exc)
    tb = traceback.format_exc()
    return {
        "error": error,
        "traceback": tb
    }

def _extract_metadata_from_call(func, args, kwargs, keys: Optional[Iterable[str]]):
    """
    Use inspect.signature to bind args+kwargs to parameter names,
    then return a dict with only requested keys (if present).
    """
    if not keys:
        return {}

    sig = inspect.signature(func)
    try:
        bound = sig.bind_partial(*args, **kwargs)
    except Exception:
        # if binding fails, return whatever we can from kwargs
        return {k: kwargs.get(k) for k in keys if k in kwargs}

    bound.apply_defaults()
    meta = {}
    for k in keys:
        if k in bound.arguments:
            meta[k] = bound.arguments[k]
        elif k in kwargs:
            meta[k] = kwargs[k]
        else:
            meta[k] = None
    return meta


def log_action(
    action: Optional[str] = None,
    *,
    meta_fields: Optional[Iterable[str]] = None,
    logger_name: str = DEFAULT_LOGGER,
    level_on_success: str = "info",
    level_on_error: str = "error",
):
    """
    Decorator factory that logs calls to a function.

    Parameters:
      - action: friendly action name (string). If None, decorator uses func.__name__.
      - meta_fields: list/iterable of parameter names to extract from call (e.g. ["domain","title","url"])
      - logger_name: logging.getLogger(...) name to use
      - level_on_success / level_on_error: "info"/"warning"/"error" etc.

    Behaviour:
      - Works for both sync and async functions.
      - If the wrapped function returns a dict with a 'success' key, that value is used to decide success.
      - Exceptions are logged and re-raised (preserve original behaviour).
      - Logs include timing and the result (or error).
    """

    def decorator(func):
        is_coroutine = inspect.iscoroutinefunction(func)
        act_name = action or func.__name__
        logger = logging.getLogger(logger_name)

        def _log(level, event, extra):
            # pick level method dynamically
            fn = getattr(logger, level, logger.info)
            try:
                fn(event, extra=extra)
            except Exception:
                # logging must not crash the app
                logger.exception("Failed to emit structured log")

        if is_coroutine:
            async def async_wrapper(*args, **kwargs):
                start = time.time()
                meta = _extract_metadata_from_call(func, args, kwargs, meta_fields)
                try:
                    result = await func(*args, **kwargs)
                    duration = time.time() - start

                    # determine success
                    success = determine_success(result)

                    result_summary = summarize_result(result)

                    extra = {
                        "action": act_name,
                        "meta": meta,
                        "duration_s": duration,
                        "success": success,
                        "result_summary": result_summary
                    }
                    _log(level_on_success, f"{act_name} finished", extra)
                    return result

                except Exception as exc:
                    error_info = capture_exception(exc)
                    duration = time.time() - start

                    extra = {
                        "action": act_name,
                        "meta": meta,
                        "duration_s": duration,
                        "success": False,
                        "error": error_info["error"],
                        "traceback": error_info["tb"]
                    }
                    _log(level_on_error, f"{act_name} failed", extra)
                    raise

            wrapped = wraps(func)(async_wrapper)
            return wrapped

        else:
            def sync_wrapper(*args, **kwargs):
                start = time.time()
                meta = _extract_metadata_from_call(func, args, kwargs, meta_fields)
                try:
                    result = func(*args, **kwargs)
                    duration = time.time() - start
                    
                    success = determine_success(result)
                    result_summary = summarize_result(result)

                    extra = {
                        "action": act_name,
                        "meta": meta,
                        "duration_s": duration,
                        "success": success,
                        "result_summary":result_summary,
                    }
                    _log(level_on_success, f"{act_name} finished", extra)
                    return result

                except Exception as exc:
                    error_info = capture_exception(exc)
                    duration = time.time() - start
                    extra = {
                        "action": act_name,
                        "meta": meta,
                        "duration_s": duration,
                        "success": False,
                        "error": error_info["error"],
                        "traceback":error_info["tb"],
                    }
                    _log(level_on_error, f"{act_name} failed", extra)
                    raise

            wrapped = wraps(func)(sync_wrapper)
            return wrapped

    return decorator
