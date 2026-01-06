
from hephis_core.events.bus import event_bus
from hephis_core.infra.observability.report_store import save_report
from hephis_core.swarm.run_context import run_context
from hephis_core.agents.reporter_rules import REPORTER_RULES
from typing import List, Callable, Dict, Any

ReporterRule = Callable[[Dict[str, Any]], Dict[str,Any]| None]

class ReporterAgent:
    def __init__(self, rules:List[ReporterRule], renderer=None):
        print("INIT: ReporterAgent")
        self.rules = rules
        self.renderer = renderer or self.output
        event_bus.subscribe("system.run.completed",self.handle_run_completed)
    
    def handle_run_completed(self, event):
        print("REPORT CALLED")
        run_id = event["run_id"]
        context = run_context.get(run_id)

        findings = []

        for rule in REPORTER_RULES:
            try:
                result = rule(context)
                if result:
                    findings.append(result)
            except Exception as exc:
                findings.append({
                    "type":"reporter_error",
                    "rule":rule.__name__,
                    "error":str(exc),
                })

        report = self.build_report(run_id, context, findings)
        save_report(run_id, report)
        self.output(report)

    def build_report(self, run_id, context, findings):
        return {
            "run_id":run_id,
            "domain":context.get("decision",{}).get("domain"),
            "input_type":context.get("source"),
            "terminated_at":context.get("terminated_at"),
            "veredict":self.infer_veredict(findings),
            "findings":findings,
            "context":context,
        }
    
    def infer_veredict(self, findings):
        if not findings:
            return "silent_success"
        if any(f["type"]== "error" for f in findings):
            return "error"
        return "no_action"
    
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