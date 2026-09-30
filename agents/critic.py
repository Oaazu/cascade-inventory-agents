import json
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()
client = Anthropic()

MODEL = "claude-sonnet-4-5"

CRITIC_SYSTEM_PROMPT = """You are the quality critic for Cascade Retail's inventory reports.

You receive two things:
1. A draft network report produced by a synthesizer agent.
2. The underlying normalized warehouse data the report was built from.

Your job is to verify the report against the source data and decide if it can be trusted.
Be skeptical. Check every claim against the numbers. You are the last check before a human.

Check for:
- Unsupported or exaggerated claims: does each network_reorder item actually have low totals
  across the network, or is a healthy total wrongly labeled "low"? Does each imbalance reflect
  a genuine, actionable gap?
- Internal contradictions: e.g. a note says "low across the network" but the total is high.
- Missed critical issues: any forwarded data_issue that the report failed to carry.
- Accuracy: do the quantities cited in the report match the source data?

Return ONLY a single raw JSON object, nothing else. Start with { and end with }. Use exactly
this shape:
{
  "verdict": "clean" | "flagged",
  "issues": [
    {"type": "unsupported_claim|contradiction|missed_issue|inaccuracy",
     "detail": "<what is wrong and which SKU/warehouse>",
     "fixable_by_retry": true | false}
  ],
  "notes": "<1-2 sentences summarizing your assessment>"
}

Rules for the verdict:
- "clean" ONLY if there are no issues that would mislead a human decision-maker.
- "flagged" if any claim is unsupported, contradictory, inaccurate, or a real issue was missed.
- fixable_by_retry: true if re-running the synthesizer could fix it (e.g. a bad claim to drop).
  false if it stems from the source data itself (e.g. a genuine negative quantity) — that is
  not a synthesis error and must go to the human, not a retry."""


def run_critic(report: dict, worker_results: list[dict]) -> dict:
    """Verify the synthesizer's report against source data. Returns verdict + issues."""
    payload = json.dumps(
        {"draft_report": report, "source_data": worker_results}, indent=2
    )
    response = client.messages.create(
        model=MODEL,
        max_tokens=3000,
        system=CRITIC_SYSTEM_PROMPT,
        messages=[
            {"role": "user", "content": f"Review this report against its source data:\n{payload}"},
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
    from agents.synthesizer import run_synthesizer
    print("Gathering warehouse data...")
    results = gather_all()
    print("Synthesizing report...")
    report = run_synthesizer(results)
    print("Critiquing report...")
    verdict = run_critic(report, results)
    print(json.dumps(verdict, indent=2))

