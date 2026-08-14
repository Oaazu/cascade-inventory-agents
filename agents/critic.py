"""Critic / Reviewer — validates the merged report; flags gaps/inconsistencies/impossible values; triggers retry."""

SYSTEM_PROMPT = """TODO (Phase 2/3): critic system prompt.
Role: check the merged report for inconsistencies, gaps, and impossible values.
Return a pass/fail verdict plus reasons."""


def run_critic(merged_report):
    # TODO Phase 3: call the model with SYSTEM_PROMPT, return verdict (+reasons)
    raise NotImplementedError
