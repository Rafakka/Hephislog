
from hephis_core.events.bus import event_bus
from typing import List, Callable, Dict, Any

ReporterRule = Callable[[Dict[str, Any]], Dict[str,Any]| None]

class ReporterAgent:
    def __init__(self, rules:List[ReporterRule]):
        print("INIT:ReporterAgent")
        self.rules = rules
        event_bus.subscribe("system.run.completed",self.handle_run_completed)
    
    def handle_run_completed(self, event:Dict[str,Any]):
        print("REPORT CALLED")
        findings = []

        for rule in self.rules:
            try:
                result=rule(event)
                if result:
                    findings.append(result)
            except Exception as exc:
                findings.append({
                    "type":"reporter_error",
                    "rule":rule.__name__,
                    "error":str(exc),
                })

        report = self.build_report(event, findings) 

        self.output(report)

    def build_report(self, event, findings):
        return {
            "run_id":event["run_id"],
            "domain":event["domain"],
            "input_type":event["input_type"],
            "terminated_at":event["terminated_at"],
            "verdict":self.infer_verdict(findings),
            "findings":findings,
        }
    
    def infer_verdict(self, findings):
        if not findings:
            return "silent_success"
        if any(f["type"]== "error" for f in findings):
            return "error"
        return "no_action"
    
    def output(self, report):
        print("\n===REPORT===")
        print("Run:", report["run_id"])
        print("Verdict:", report["verdict"])

        if not report["findings"]:
            print("no findings")
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