def request_approval(report: dict, verdict: dict) -> dict:
    """Present the report to a human and capture an approve/reject decision."""
    print("\n" + "=" * 60)
    print("HUMAN APPROVAL REQUIRED")
    print("=" * 60)

    print(f"\nCritic verdict: {verdict['verdict'].upper()}")
    if verdict.get("issues"):
        print("Critic flagged:")
        for issue in verdict["issues"]:
            print(f"  - {issue['detail']}")

    print("\n--- NETWORK REPORT SUMMARY ---")
    print(report.get("summary", "(no summary)"))

    if report.get("network_reorder"):
        print("\nNetwork reorder needed:")
        for item in report["network_reorder"]:
            print(f"  - {item['product']} ({item['sku']}): {item.get('total_quantity', '?')} total")

    if report.get("imbalances"):
        print("\nImbalances (transfer opportunities):")
        for item in report["imbalances"]:
            print(f"  - {item['product']} ({item['sku']}): {item['detail']}")

    if report.get("data_issues_forwarded"):
        print("\nData issues needing attention:")
        for issue in report["data_issues_forwarded"]:
            print(f"  - {issue['sku']} at {issue['warehouse_id']}: {issue['issue']}")

    print("\n" + "-" * 60)
    while True:
        choice = input("Approve this report? (yes/no): ").strip().lower()
        if choice in ("yes", "y"):
            decision = "approved"
            break
        if choice in ("no", "n"):
            decision = "rejected"
            break
        print("Please type 'yes' or 'no'.")

    note = input("Optional note (press Enter to skip): ").strip()

    print(f"\nReport {decision.upper()} by human reviewer.")
    return {"decision": decision, "note": note}