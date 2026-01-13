
from hephis_core.events.bus import event_bus
from hephis_core.infra.observability.report_store import save_report
from hephis_core.swarm.run_context import run_context
from hephis_core.agents.reporter_rules.base import run_completed, should_run_diagnostics, logger
from hephis_core.agents.reporter_rules import REPORTER_RULES
from hephis_core.agents.reporter_rules.base import iter_facts
from typing import List, Callable, Dict, Any


ReporterRule = Callable[[list[dict]], dict | None]

class ReporterAgent:
    def __init__(self, rules:List[ReporterRule], renderer=None):
        print("10 - INIT: ReporterAgent")
        self.rules = rules
        self.renderer = renderer or self.output
        event_bus.subscribe("system.run.completed",self.handle_run_completed)
    
    def run_completed(context:list[dict]) -> bool:
        for f in context:
            if f.get("event") == "run_completed":
                return True
        return False
    
    def handle_run_completed(self, event):
        print("REPORT CALLED")

        run_id = event["run_id"]
        context = run_context.get(run_id)

        for f in context.get("facts",[]):
            assert isinstance(f,dict),f"invalid fact detected: {f!r}"

        if not should_run_diagnostics(context):
            report = {
                "run_id":run_id,
                "veredict":"silent_success",
                "findings":[],
                "context":context,
            }
            save_report(run_id, report)
            self.output(report)
            return

        findings = []

        for rule in REPORTER_RULES:
            try:
                facts = iter_facts(context)
                result = rule(facts)
                if result:
                    findings.append(result)
            except Exception as exc:
                logger.exception(
                    "Reporter rule failed",
                    rule=rule.__name__
                )

        report = {
            "run_id":run_id,
            "veredict":self.infer_veredict(findings, context),
            "findings":findings,
            "context":context,
        }
        save_report(run_id, report)
        self.output(report)
    
    def infer_veredict(self, findings, context):

        if run_completed(context):
            return "silent_success"

        if any(f.get("type")=="error" for f in findings):
            return "error"

        if findings:
            return "Flow Completed"

        return "silent_success"
    
    def output(self, report):
        self.last_report = report
        print("\n===REPORT===")
        print("Run:", report["run_id"])
        print("Veredict:", report["veredict"])

        findings = report.get("findings",[])

        if not findings:
            print("No rule produced findings")
            return

        if not report["findings"]:
            print("Explanation:No rule produced findings.")
            print("Meaning: The pipiline completed successfully without requiring action.")
            return
        
        print("\nDetails:")
        for f in report["findings"]:
            print(f"- Type:{f.get('type')}")

            if "reason" in f:
                print(f" Reason:{f['reason']}")
            
            if "message" in f:
                print(f" Message:{f['message']}")
            
            if "summary" in f:
                print(" Summary:")
                for k, v in f["summary"].items():
                    print(f" {k}:{v}")
            if None in f:
                print("None")