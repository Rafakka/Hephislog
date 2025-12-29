from collections import defaultdict
from hephis_core.events.decorators import on_event
from hephis_core.utils.logger_decorator import log_action
from hephis_core.events.event_bus import event_bus

class ConfidenceAgent:

    def __init__(self):
        print("INIT:",self.__class__.__name__)
        self.trust = defaultdict(lambda: defaultdict(lambda:{"success":0,"failure":0,}))
        self.pending = {}
        self._register_handlers()


    def _register_handlers(self):
        for attr_name in dir (self):
            attr = getattr(self,attr_name)
            
            fn = getattr(attr,"__func__",None)

            if fn and hasattr(fn, "_event_name"):
                event_name = fn._event_name
                print(f"REGISTER{self.__class__.__name__}->{event_name}")
                print("SUBSCRIBE BUS ID:", id(event_bus))
                event_bus.subscribe(event_name, attr)

    @log_action(action="agt-recording-decisions")
    @on_event("intent.*")
    def record_decisions(self, payload):
        run_id = payload.get("run_id")
        domain = payload.get("domain")

        if not run_id or not domain:
            return
        smell = domain
        intent = f"organize.{domain}"

        self.pending[run_id] = {
            "smell":smell,
            "intent":intent,
        }

    @log_action(action="agt-learning-from-outcomes")
    @on_event("*.pipeline_finished")
    def learn_from_outcomes(self, payload):
        run_id = payload.get("run_id")
        success = payload.get("success", True)
        decision = self.pending.pop(run_id, None)

        if not decision:
            return
                
        smell = decision.get("smell")
        intent = decision.get("intent")
        if not smell or not intent:
            return
                
        stats = self.trust[smell][intent]
        if success:
            stats["success"] +=1
        else:
            stats["failure"] +=1
            
        total = stats["success"] + stats["failure"]
        trust_value = stats["success"] / total if total else 1.0

        print("EMIT BUS ID:", id(event_bus))
        event_bus.emit("confidence.updated",{
                "smell":smell,
                "intent":intent,
                "trust":trust_value,
            })

        
    def get_trust(self, smell:str, intent:str) -> float:

        stats = self.trust.get(smell,{}).get(intent)

        if not stats:
            return 1.0
            
        total = stats["success"] + stats["failure"]
        if total == 0:
            return 1.0
            
        return stats["success"] / total