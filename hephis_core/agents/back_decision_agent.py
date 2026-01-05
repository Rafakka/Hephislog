class DecisionAgent:

    DOMAIN_THRESHOLDS = {
        "recipe":0.6,
        "music":0.7,
        "text":0.6,
    }
    
    DEFAULT_THRESHOLD = 0.5

    def __init__(self):
        print("INIT:", self.__class__.__name__)
        self.confidence = {}
        for attr_name in dir(self):
            attr = getattr(self, attr_name)
            fn = getattr(attr, "__func__", None)
            if fn and hasattr(fn, "__event_name__"):
                event_bus.subscribe(fn.__event_name__, attr)

    @log_action(action="agt-deciding-by-smell")
    @on_event("system.smells.post.extraction")
    def decide(self, payload):
        smells = payload.get("smells",{})
        source = payload.get("source")
        run_id = payload.get("run_id")
        raw = payload.get("raw")

        if not run_id or not smells:
            event_bus.emit(
                "facts.emit",{
                    "stage":"decision",
                    "component":"DecisionAgent",
                    "result":"declined",
                    "reason":"missing_run_id_or_smells",
                    "details":{"smells":smells}
                }
            )

        candidates = {
            domain:score
            for domain, score in smells.items()
            if score >= self.DOMAIN_THRESHOLDS.get(domain, self.DEFAULT_THRESHOLD)
        }

        if not candidates:
            event_bus.emit(
                "facts.emit",{
                    "stage":"decision",
                    "component":"DecisionAgent",
                    "result":"declined",
                    "reason":"no_domain_above_threshold",
                    "details":{
                        "thresholds":self.DOMAIN_THRESHOLDS,
                        "smells":smells,
                    }
                }
            )
        
        weighted = {}

        for domain, score in candidates.items():
            intent = f"organize.{domain}"
            trust = self.confidence.get((domain,intent),1.0)

        threshold = self.DOMAIN_THRESHOLDS.get(domain, self.DEFAULT_THRESHOLD)

        if trust < threshold:
            continue
            weighted[domain] = score*trust

        if not weighted:
            event_bus.emit(
                "facts.emit",{
                    "stage":"decision",
                    "component":"DecisionAgent",
                    "result":"declined",
                    "reason":"trust_filtered_all_candidates",
                    "details":{"candidates":candidates}
                }
            )

        chosen_domain, confidence = max(weighted.items(), key=lambda i:i[1])

        decision = {
                "domain":chosen_domain,
                "confidence":confidence,
                "smells":smells,
                "source":source,
                "run_id":run_id,
            }

        if raw is None:
                event_bus.emit(
                    "facts.emit",{
                        "stage":"decision",
                        "component":"DecisionAgent",
                        "result":"accepted",
                        "reason":"no_raw_payload_no_intent",
                    }
                )

        event_bus.emit(
                    f"intent.organize.{chosen_domain}",{
                    "domain":chosen_domain,
                    "confidence":confidence,
                    "run_id":run_id,
                    "raw":raw,
                    "source":source,
                    
                    }
                )

    @log_action(action="agt-updating-confidence")
    @on_event("confidence.updated")
    def update_confidence(self, payload):
        key = (payload["smell"], payload["intent"])
        self.confidence[key] = payload["trust"]
