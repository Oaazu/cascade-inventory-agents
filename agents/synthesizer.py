import json
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()
client = Anthropic()

MODEL = "claude-sonnet-4-5"

SYNTHESIZER_SYSTEM_PROMPT = """You are the network inventory synthesizer for Cascade Retail.

You receive normalized inventory results from all warehouses (already validated by worker
agents). Your job is to reason ACROSS warehouses and produce one consolidated network report.

Return ONLY a single raw JSON object, nothing else. Start with { and end with }. Do not write
prose, tables, or headings. Use exactly this shape:
{
  "network_reorder": [
    {"sku": "...", "product": "...", "total_quantity": <int>, "note": "low across the network"}
  ],
  "imbalances": [
    {"sku": "...", "product": "...", "detail": "0 at WH-XX but <n> at WH-YY; consider transfer"}
  ],
  "data_issues_forwarded": [
    {"sku": "...", "warehouse_id": "WH-XX", "issue": "..."}
  ],
  "summary": "<2-3 sentence plain-language overview for the analyst>"
}

How to reason:
- network_reorder: a SKU whose quantity is at or below its reorder_point in most or all
  warehouses (a network-wide shortage, not a single-store dip).
- imbalances: a SKU that is critically low or zero in one warehouse while heavily overstocked
  in another — a transfer opportunity. State both sides with warehouse ids.
- data_issues_forwarded: carry forward every data_issue the workers flagged, so nothing an
  agent caught gets silently dropped before the human sees it.
- summary: what an ops analyst most needs to know, in plain language.
- Do not invent SKUs or warehouses. Use only what is in the input."""


def run_synthesizer(worker_results: list[dict], critic_feedback: dict = None) -> dict:
    """Take the six worker results, return the consolidated network report.
    If critic_feedback is provided, address it in this revision."""
    payload = json.dumps(worker_results, indent=2)
    user_content = f"Normalized results from all warehouses:\n{payload}"
    if critic_feedback:
        fb = json.dumps(critic_feedback, indent=2)
        user_content += (
            f"\n\nA previous draft was reviewed by a critic who found these issues. "
            f"Produce a corrected report that addresses them:\n{fb}"
        )
    response = client.messages.create(
        model=MODEL,
        max_tokens=4000,
        system=SYNTHESIZER_SYSTEM_PROMPT,
        messages=[
            {"role": "user", "content": user_content},
            {"role": "assistant", "content": "{"},
        ],
    )
    return _extract_json("{" + response.content[0].text)


def _extract_json(text: str) -> dict:
    """Parse the model's reply as JSON, tolerating code fences or stray prose."""
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError(f"No JSON object in model output. Raw response was:\n{text!r}")
    return json.loads(text[start:end + 1])


if __name__ == "__main__":
    from agents.orchestrator import gather_all
    print("Gathering warehouse data...")
    results = gather_all()
    print("Synthesizing network report...")
    report = run_synthesizer(results)
    print(json.dumps(report, indent=2))