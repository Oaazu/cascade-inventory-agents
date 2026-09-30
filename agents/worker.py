import json
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()    #Loads Anthropic API KEY from .env into this enviroment
client = Anthropic()  # the SDK reads the key from the enviroment automatically

MODEL = "claude-sonnet-4-5"

WORKER_SYSTEM_PROMPT = """You are a warehouse inventory normalization agent for Cascade Retail.
You receive raw inventory data from ONE warehouse. The format varies between warehouses
(standard CSV, legacy CSV with different column names, or JSON), so map whatever you
receive onto the common schema below.

Your entire response must be a single raw JSON object and nothing else. Do not write a
report, tables, headings, or any prose. Start your response with { and end with }. Use
exactly this shape:
{
  "warehouse_id": "<the id you were given>",
  "items": [
    {"sku": "...", "product": "...", "quantity": <int>, "reorder_point": <int>, "last_updated": "..."}
  ],
  "assessment": {
    "below_reorder": ["<sku>", ...],
    "data_issues": [{"sku": "...", "issue": "..."}]
  }
}

Rules:
- Map differing column names to the schema (e.g. item_code->sku, qty->quantity, min_stock->reorder_point).
- below_reorder: every sku whose quantity <= reorder_point.
- - data_issues: flag ONLY objectively impossible values — a negative quantity, a missing or
  non-numeric quantity or reorder_point, or a missing sku. Do NOT flag stale dates, zero
  quantities, low stock, or anything that needs judgment; those are handled elsewhere.
  If every field is present and every quantity is a valid number, data_issues MUST be [].
- Do not invent items. Report only what is in the data."""

def run_worker(warehouse_id: str, raw_data: str) -> dict:
    """Run one warehouse worker agent. Returns the normalized + assessed result as a dict."""
    response = client.messages.create(
        model=MODEL,
        max_tokens=3000,
        system=WORKER_SYSTEM_PROMPT,
        messages=[
            {"role": "user", "content": f"warehouse_id: {warehouse_id}\n\nRaw data:\n{raw_data}"},
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
    with open("data/warehouse_01.csv", "r", encoding="utf-8") as f:
        raw = f.read()
    result = run_worker("WH-01", raw)
    print(json.dumps(result, indent=2))