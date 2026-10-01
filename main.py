import json
from agents.orchestrator import gather_all
from agents.synthesizer import run_synthesizer
from agents.critic import run_critic
from agents.logger import RunLogger

MAX_RETRIES = 2


def has_retryable_issues(verdict: dict) -> bool:
    """True if the critic flagged at least one issue a retry could fix."""
    return any(issue.get("fixable_by_retry") for issue in verdict.get("issues", []))


def run_pipeline() -> dict:
    """Full flow: gather -> synthesize -> critique -> retry if fixable -> return for approval."""
    logger = RunLogger()

    print("[1/3] Gathering warehouse data (6 workers in parallel)...")
    worker_results = gather_all()
    logger.log("workers", {"warehouses": 6}, worker_results)

    print("[2/3] Synthesizing network report...")
    report = run_synthesizer(worker_results)
    logger.log("synthesizer", worker_results, report)

    print("[3/3] Critiquing report...")
    verdict = run_critic(report, worker_results)
    logger.log("critic", report, verdict)

    attempt = 0
    while verdict["verdict"] == "flagged" and has_retryable_issues(verdict) and attempt < MAX_RETRIES:
        attempt += 1
        print(f"    -> Flagged with retryable issues. Retry {attempt}/{MAX_RETRIES}...")
        report = run_synthesizer(worker_results, critic_feedback=verdict)
        logger.log(f"synthesizer_retry_{attempt}", verdict, report)
        verdict = run_critic(report, worker_results)
        logger.log(f"critic_retry_{attempt}", report, verdict)

    log_path = logger.save(verdict["verdict"], attempt)
    print(f"    Full exchange logged to {log_path}")

    return {"report": report, "verdict": verdict, "retries_used": attempt}


if __name__ == "__main__":
    result = run_pipeline()
    print("\n" + "=" * 60)
    print(f"FINAL VERDICT: {result['verdict']['verdict'].upper()}  (retries used: {result['retries_used']})")
    print("=" * 60)
    print("\n--- NETWORK REPORT ---")
    print(json.dumps(result["report"], indent=2))
    print("\n--- CRITIC VERDICT ---")
    print(json.dumps(result["verdict"], indent=2))