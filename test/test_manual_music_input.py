from hephis_core.events.bus import event_bus
from hephis_core.swarm.decision_store import decision_store
from hephis_core.infra.observability.report_store import reset_report
from hephis_core.bootstrap import bootstrap_agents

def run_manual_explained_silence():
    print("\n===EMIT INPUT EVENT ===")

    event_bus.reset()
    decision_store.reset()
    reset_report()
    bootstrap_agents()

    run_id = "music-clear-1"
    
    print("\n===EMIT INPUT EVENT===")
    event_bus.emit(
        "system.smells.post.extraction",
        {
            "run_id":run_id,
            "source":"test",
            "raw":{
                "domain":"music",
                "lyrics":["taking away..."],
                "chords":["C","G","Am","F"],
                "text":"taking away...",
            },
            "smells":{
                "music":0.9,
                "text":0.1,
            }
        }   
    )

    print("Event emitted successfully.")

    print("\n===CHECK DECISION===")
    decision = decision_store.get(run_id)
    print("Decision:", decision)

    if decision is None:
        print("no agent acted", decision)
    else:
        print("agent acted:", decision)


if __name__ == "__main__":
    run_manual_explained_silence()
