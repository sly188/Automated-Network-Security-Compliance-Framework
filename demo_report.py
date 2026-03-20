#!/usr/bin/env python3
"""
renders the compliance report locally using mock audit results
no ansible or real devices needed — just run:
  python3 demo_report.py
then open reports/demo_report.html in your browser
"""

import json
import glob
from datetime import datetime
from jinja2 import Template

# load all audit result files
results = []
for f in sorted(glob.glob("reports/audit_results/*.json")):
    with open(f) as fh:
        results.append(json.load(fh))

# calc overall stats
scores = [r["score"] for r in results]
overall = round(sum(scores) / len(scores), 1)

critical_fails = sum(
    1 for r in results
    for c in r["checks"]
    if c["severity"] == "CRITICAL" and c["status"] == "FAIL"
)
high_fails = sum(
    1 for r in results
    for c in r["checks"]
    if c["severity"] == "HIGH" and c["status"] == "FAIL"
)

# read template
with open("roles/reporting/templates/report.html.j2") as fh:
    raw = fh.read()

# jinja2 render
t = Template(raw)
html = t.render(
    all_results=results,
    overall_score=overall,
    critical_fails=critical_fails,
    high_fails=high_fails,
    run_date=datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
    threshold=80
)

out = "reports/demo_report.html"
with open(out, "w") as fh:
    fh.write(html)

print(f"report saved to {out}")
print(f"overall score  : {overall}%")
print(f"devices audited: {len(results)}")
print(f"critical fails : {critical_fails}")
print(f"high fails     : {high_fails}")
