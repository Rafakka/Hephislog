import pytest
from hephis_core.agents.reporter_agent import ReporterAgent
from hephis_core.agents.reporter_rules import REPORTER_RULES
from hephis_core.utils.utils import FakeFact

@pytest.fixture
def reporter():
    return ReporterAgent(rules=REPORTER_RULES)

def run_report(reporter, event):
    reporter.handle_run_completed(event)
    return reporter.last_report

def test_silent_success(reporter):
    report = run_report(reporter,{
        "run_id":"test_silent",
        "domain":"test",
        "input_type":"manual",
        "terminated_at":"now",
        "facts":[],
        }
    )

    assert report["veredict"] == "no_action"
    types = {f["type"] for f in report["findings"]}
    assert "silent_success" in types

def test_no_detector_signal(reporter):
    report = run_report(reporter,{
        "run_id":"test_no_detector",
        "domain":"test",
        "input_type":"manual",
        "terminated_at":"now",
        "facts":[
            FakeFact("detector","d1","none"),
            FakeFact("detector","d2","none"),
        ],
    })

    types = {f["type"] for f in report["findings"]}
    assert "no_detector_signal" in types

def test_agent_declined(reporter):
    report = run_report(reporter,{
        "run_id":"test_declined",
        "domain":"test",
        "input_type":"manual",
        "terminated_at":"now",
        "facts":[
            FakeFact(stage="decision",component="agent",result="declined"),
        ],
    })

    types = {f["type"] for f in report["findings"]}
    assert "agent_declined" in types
    assert report["veredict"] == "no_action"

def test_mixed_results(reporter):
    report = run_report(reporter, {
        "run_id":"test_mixed",
        "domain":"test",
        "input_type":"manual",
        "terminated_at":"now",
        "facts":[
            FakeFact("detector","d1","ok"),
            FakeFact("decision","agent","none"),
        ],
    })

    assert report["veredict"] in {"no_action","silent_success"}

def test_reporter_survives_broke_rule():
    def broken_rule(event):
        return event["this"]["will"]["explode"]

    reporter = ReporterAgent(rules=[broken_rule])

    reporter.handle_run_completed({
        "run_id":"test_broken",
        "domain":"test",
        "input_type":"manual",
        "terminated_at":"now",
        "facts":[],
    })

    report = reporter.last_report
    assert any(f["type"] == "reporter_error" for f in report["findings"])
