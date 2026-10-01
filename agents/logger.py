import json
import os
from datetime import datetime


class RunLogger:
    """Captures the full agent exchange for one pipeline run into a single timestamped file."""

    def __init__(self, log_dir: str = "logs"):
        os.makedirs(log_dir, exist_ok=True)
        self.start = datetime.now()
        stamp = self.start.strftime("%Y-%m-%d_%H-%M-%S")
        self.path = os.path.join(log_dir, f"run_{stamp}.json")
        self.entries = []

    def log(self, agent: str, input_data, output_data):
        """Record one agent exchange: who ran, what went in, what came out."""
        self.entries.append({
            "timestamp": datetime.now().isoformat(),
            "agent": agent,
            "input": input_data,
            "output": output_data,
        })

    def save(self, final_verdict: str, retries_used: int):
        """Write the whole run to disk. Called once at the end."""
        record = {
            "run_started": self.start.isoformat(),
            "run_finished": datetime.now().isoformat(),
            "final_verdict": final_verdict,
            "retries_used": retries_used,
            "exchanges": self.entries,
        }
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(record, f, indent=2)
        return self.path