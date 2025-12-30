from hephis_core.infra.observability.run_context import RunContext
from hephis_core.infra.observability.context import current_run
from hephis_core.utils.logger_decorator import log_action

@log_action(action="test_ok",stage="test")
def returns_value():
    return 42

@log_action(action="test_none", stage="test")
def returns_none():
    return None

@log_action(action="test_error",stage="test")
def return_error():
    return RuntimeError("boom")

def run_test():
    ctx=RunContext(
        run_id="test_run-1",
        domain="test",
        input_type="manual"
    )

    token = current_run.set(ctx)

    try:
        returns_value()
        returns_none()

        try:
            raises_error()
        except RuntimeError:
            pass

    finally:
        current_run.reset(token)
    
    for fact in ctx.facts:
        print(fact)
