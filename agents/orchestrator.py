import json 
from concurrent.futures import ThreadPoolExecutor
from agents.worker import run_worker

# The explicit registry: one line per warehouse. This IS the system's answer to how does it know
#"about the six warehouses?" - here the clarification.
WAREHOUSES = [
    {"id": "WH-01", "data_file": "data/warehouse_01.csv"},
    {"id": "WH-02", "data_file": "data/warehouse_02.csv"},
    {"id": "WH-03", "data_file": "data/warehouse_03.csv"},
    {"id": "WH-04", "data_file": "data/warehouse_04.csv"},
    {"id": "WH-05", "data_file": "data/warehouse_05.csv"},
    {"id": "WH-06", "data_file": "data/warehouse_06.json"},
]

def _load_and_run(warehouse: dict) -> dict:
    """Read one warehouse's file and run the worker agent."""
    with open(warehouse["data_file"], "r", encoding="utf-8") as f:
        raw = f.read()
    return run_worker(warehouse["id"], raw)

def gather_all() -> list[dict]:
    """Run all six warehouse workers in parallel, return their results as a list."""
    with ThreadPoolExecutor(max_workers=6) as executor:
        results = list(executor.map(_load_and_run, WAREHOUSES))
    return results

if __name__ == "__main__":
    all_results = gather_all()
    for r in all_results:
        issues = len(r["assessment"]["data_issues"])
        low = len(r["assessment"]["below_reorder"])
        print(f"{r['warehouse_id']}: {len(r['items'])} items, {low} below reorder, {issues} data issues")
        