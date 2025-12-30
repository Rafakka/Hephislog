from hephis_core.events.bus import event_bus
from hephis_core.infra.observability.run_context import RunContext

def close_run(ctx:RunContext, stage:str):
    ctx.terminate(stage)

    event_bus.emit(
        "system.run.completed",{
            "run_id":ctx.run_id,
            "domain":ctx.domain,
            "input_type":ctx.input_type,
            "terminated_at":ctx.terminated_at_stage,
            "facts":ctx.facts,
        }
    )