# Before / After — Cascade Cross-Warehouse Inventory Reporting

A one-page business case for replacing a manual cross-warehouse reporting process with a
multi-agent system, while keeping human sign-off on every report.

---

## The process

Cascade Retail's ops analyst compiles a network inventory report by checking stock across 6
separate warehouse systems, reconciling them by hand, and writing up shortages and
imbalances. The output is accurate and trusted. The constraint is speed and capacity: one
report takes about half a day, and it runs roughly 3 times a week.

---

## Before (manual)

Assumptions are defensible estimates, stated so the math can be checked.

| Measure | Value |
|---|---|
| Time per report | ~4 hours |
| Frequency | 3 reports / week |
| Analyst cost (fully loaded) | ~$70k base × 1.3 overhead ÷ 2,080 hrs ≈ **$45/hr** |
| Cost per report | 4 hrs × $45 = **$180** |
| Annual cost (156 reports) | **~$28,000/year** of analyst time on this one task |

Plus a softer, unpriced cost: the manual process occasionally misses cross-warehouse
signals — stock stranded in one warehouse while another runs dry — which means lost sales
or avoidable transfers.

---

## After (multi-agent system)

| Measure | Value |
|---|---|
| Processing time | **~1–4 minutes**, depending on how many self-correction retries the critic triggers |
| Human review | A short sign-off on a finished report (minutes, not hours) |
| Cost per run | A few cents in API tokens (**under $0.15** even with retries) |
| Consistency | The same validation checks run on every report, identically |

---

## Side by side

| | Manual | Multi-agent |
|---|---|---|
| Time to a report | ~4 hours | ~1–4 min processing + short review |
| Cost per report | $180 | under $0.15 |
| Checks applied | Vary with the analyst's day | Identical every run |
| Human role | Builds the report | Reviews and approves a finished report |

---

## The honest claim

This is **not** a headcount-reduction case. The analyst is not removed — their hours are
redirected, and they stay in the loop as the approver. Pitched as "saves $28k," a
stakeholder disproves it in one question. The real, defensible value is:

1. **Faster turnaround** — a report on demand in minutes instead of waiting half a day for
   someone to compile it.
2. **Redeployed capacity** — ~12 analyst-hours/week returned from data-gathering to
   judgment work.
3. **Fewer misses** — the same shortage, imbalance, and data-quality checks run on every
   report, where a human under time pressure might not.

> The system does the gathering. The human keeps the decision.

---

## What we keep from the old process

**Full Approval.** A human signs off on every generated report before it is treated as
trusted or actionable. No reorder or transfer decision flows from an unapproved report.

What automates away: the manual gathering, cross-system reconciliation, and hand-merging.
What survives: human judgment on the final report — the sign-off that already existed.

The critic classifies each report `clean` or `flagged`, so the system is built to mature
from Full Approval toward **exception-only** review (humans see only flagged reports) once
the critic has a proven track record — a configuration change, not a rebuild.

---

## A note on the numbers

Processing time and cost are measured from real runs of the prototype, not projected. The
range (1–4 minutes) reflects genuine variance: a run takes longer specifically when the
critic catches an error and triggers a retry — i.e. the slower runs are the system doing
its job. Cost per run is estimated from ~8–12 API calls per run on a mid-tier model with
small payloads.
