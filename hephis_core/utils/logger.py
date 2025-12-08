import logging

def log_deletion(event: str, **details):
    """
    Unified deletion logger for all delete actions.
    Uses the Django logging config ('hephislog.deletion').
    """
    logger = logging.getLogger("hephislog.deletion")
    logger.info(event, extra=details)