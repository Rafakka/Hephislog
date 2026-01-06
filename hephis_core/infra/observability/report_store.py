
_REPORTS = {}

def save_report(run_id:str, report:dict):
    _REPORTS[run_id] = report

def get_report(run_id:str):
    return _REPORTS.get(run_id)

def reset_report():
    _REPORTS.clear()
