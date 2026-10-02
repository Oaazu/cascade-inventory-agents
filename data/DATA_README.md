# Cascade Retail — Simulated Warehouse Data

Six "separate system" inventory files for the capstone. Drop them into `/data`. The formats are **deliberately inconsistent** — that's the point: it's what makes 6 real systems slow to reconcile by hand, and it justifies a worker agent per warehouse that normalizes into shared state.

## Files & schemas

| File | Warehouse | Format | Field names |
|---|---|---|---|
| `warehouse_01.csv` | WH-01 Los Angeles | CSV (standard) | `sku, product_name, quantity_on_hand, reorder_point, last_updated` |
| `warehouse_02.csv` | WH-02 Dallas | CSV (standard) | same as above |
| `warehouse_03.csv` | WH-03 Chicago | CSV (standard) | same as above |
| `warehouse_04.csv` | WH-04 Atlanta | CSV (standard) | same as above |
| `warehouse_05.csv` | WH-05 Newark | CSV (**legacy naming**) | `item_code, description, qty, min_stock, updated_at` |
| `warehouse_06.json` | WH-06 Phoenix | **JSON** (nested) | `sku, product, on_hand, reorder_at, updated` inside `inventory[]` |

All six share the same 16-SKU catalog, so a merge across warehouses is meaningful (network totals, imbalances, reorder flags).

`generate_data.py` reproduces all six deterministically (`seed=42`). Keep it in the repo — being able to regenerate the data is a point in your favor during the pitch.

## Seeded signals — your test answer key

A correct system should surface these. Use them to check your agents actually work, not just run.

1. **Network-wide reorder — Ground Coffee (SKU-1005).** Single-digit quantities in every warehouse, all below the reorder point of 30. Your merged report should flag it as a network-level reorder.
2. **Imbalance — Chicken Breast (SKU-1009).** `0` in WH-03 (Chicago stockout) but `260` in WH-05 (Newark overstock). The report should catch this as a transfer/rebalance opportunity, not just two separate numbers.
3. **Data-quality trap — Rice (SKU-1013) in WH-02 = `-5`.** An impossible value. **This is the Critic agent's job.** A run where the critic *misses* this is a failing run. Decide how the system handles it (flag, exclude, or retry the worker) and be able to explain the choice.
4. **Freshness gap — WH-04 (Atlanta).** Three SKUs (eggs, ground beef, tomato sauce) carry timestamps 35–60 days old, simulating a lagging system. Optional stretch: have the report note stale data rather than trusting it silently.

## How this maps to the build (see the playbook)

- **Phase 3, worker agents:** the format differences above are exactly what each worker normalizes. WH-05's legacy names and WH-06's JSON are the interesting cases — get WH-01 working first, then handle those.
- **Phase 3, critic + retry:** the `-5` rice value is your live test that the critic does something real.
- **Phase 1, business case:** signals 1 and 2 are the kind of insight the manual analyst spends half a day assembling — name them in your before/after as "what the automated report catches."
