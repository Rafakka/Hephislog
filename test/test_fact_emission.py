from hephis_core.infra.observability.run_closer import close_run
from hephis_core.infra.observability.run_context import RunContext
from hephis_core.infra.observability.context import current_run
from hephis_core.utils.logger_decorator import log_action
from hephis_core.events.bus import event_bus

def debug_run_completed(event):
    print("\nRUN COMPLETED.")
    print(event["run_id"])
    print("Terminated at:",event["terminated_at"])
    print("Facts:")
    for f in event["facts"]:
        print(" ",f)

event_bus.subscribe("system.run.completed",
debug_run_completed)

@log_action(action="test_ok",stage="test")
def returns_value():
    return 42

@log_action(action="test_none", stage="test")
def returns_none():
    return None

@log_action(action="test_error",stage="test")
def raises_error():
    raise RuntimeError("boom")


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
        close_run(ctx, stage="test_runner")
        current_run.reset(token)

if __name__ == "__main__":
    run_test()