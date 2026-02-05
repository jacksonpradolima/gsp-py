"""
Comprehensive example demonstrating custom hooks in GSP-Py.

This example shows how to use preprocessing, candidate filtering, and
postprocessing hooks to customize the GSP mining process.
"""

from functools import partial

from gsppy.gsp import GSP


def normalize_lowercase(txs):
    """Normalize all items to lowercase."""
    result = []
    for tx in txs:
        converted_tx = []
        for itemset in tx:
            if itemset:
                converted_itemset = tuple(item.lower() if isinstance(item, str) else item for item in itemset)
                converted_tx.append(converted_itemset)
        result.append(tuple(converted_tx))
    return result


def high_confidence_filter(_candidate, support_count, context):
    """Keep only high-confidence patterns."""
    min_support = context.get("min_support_count", 0)
    return support_count >= min_support * 1.5


def top_k_patterns(patterns, k=3):
    """Keep only top-k patterns per level."""
    result = []
    for level in patterns:
        if level:
            sorted_patterns = sorted(level.items(), key=lambda x: x[1], reverse=True)[:k]
            result.append(dict(sorted_patterns))
        else:
            result.append(level)
    return result


def add_metadata(patterns):
    """Add statistics to results."""
    total_patterns = sum(len(level) for level in patterns)
    max_support = max((max(level.values()) if level else 0) for level in patterns)
    metadata = {
        "_metadata": {
            "total_patterns": total_patterns,
            "levels": len(patterns),
            "max_support": max_support,
        }
    }
    return [metadata] + patterns


def progressive_filter(candidate, support_count, context):
    """Apply stricter filtering for longer patterns."""
    min_support = context.get("min_support_count", 1)
    length = len(candidate)
    if length <= 2:
        return True
    elif length <= 4:
        return support_count >= min_support * 1.3
    else:
        return support_count >= min_support * 1.5


def run_example_1_basic(transactions):
    """Example 1: Basic GSP without hooks (baseline)."""
    print("Example 1: Basic GSP (no hooks)")  # noqa: T201
    print("-" * 70)  # noqa: T201
    gsp1 = GSP(transactions)
    patterns1 = gsp1.search(min_support=0.3)
    print(f"Total patterns found: {sum(len(level) for level in patterns1)}")  # noqa: T201
    print(f"Levels: {len(patterns1)}")  # noqa: T201
    print()  # noqa: T201


def run_example_2_preprocessing(transactions):
    """Example 2: Preprocessing - Normalize to lowercase."""
    print("Example 2: Preprocessing - Normalize case")  # noqa: T201
    print("-" * 70)  # noqa: T201
    gsp2 = GSP(transactions)
    patterns2 = gsp2.search(min_support=0.3, preprocess_fn=normalize_lowercase)
    print(f"Total patterns found: {sum(len(level) for level in patterns2)}")  # noqa: T201
    print("Sample patterns:")  # noqa: T201
    if patterns2 and patterns2[0]:
        for pattern, support in list(patterns2[0].items())[:5]:
            print(f"  {pattern}: {support}")  # noqa: T201
    print()  # noqa: T201


def run_example_3_lambda_filter(transactions):
    """Example 3: Candidate filtering with lambda."""
    print("Example 3: Candidate filtering - Length constraint")  # noqa: T201
    print("-" * 70)  # noqa: T201
    gsp3 = GSP(transactions)
    patterns3 = gsp3.search(
        min_support=0.3,
        preprocess_fn=normalize_lowercase,
        candidate_filter_fn=lambda candidate, _support, _ctx: len(candidate) <= 2,
    )
    print(f"Total patterns found: {sum(len(level) for level in patterns3)}")  # noqa: T201
    print(f"Levels: {len(patterns3)} (limited by filter)")  # noqa: T201
    print()  # noqa: T201


def run_example_4_high_confidence(transactions):
    """Example 4: High confidence filtering."""
    print("Example 4: Candidate filtering - High confidence")  # noqa: T201
    print("-" * 70)  # noqa: T201
    gsp4 = GSP(transactions)
    patterns4 = gsp4.search(
        min_support=0.3, preprocess_fn=normalize_lowercase, candidate_filter_fn=high_confidence_filter
    )
    print(f"Total patterns found: {sum(len(level) for level in patterns4)}")  # noqa: T201
    print("High-confidence patterns (support >= 1.5x minimum):")  # noqa: T201
    for level_idx, level in enumerate(patterns4, start=1):
        print(f"  Level {level_idx}: {len(level)} patterns")  # noqa: T201
    print()  # noqa: T201


def run_example_5_topk(transactions):
    """Example 5: Postprocessing - Top-k patterns."""
    print("Example 5: Postprocessing - Top-3 per level")  # noqa: T201
    print("-" * 70)  # noqa: T201
    gsp5 = GSP(transactions)
    patterns5 = gsp5.search(
        min_support=0.2, preprocess_fn=normalize_lowercase, postprocess_fn=partial(top_k_patterns, k=3)
    )
    print("Top-3 patterns per level:")  # noqa: T201
    for level_idx, level in enumerate(patterns5, start=1):
        print(f"\n  Level {level_idx}:")  # noqa: T201
        for pattern, support in level.items():
            print(f"    {pattern}: {support}")  # noqa: T201
    print()  # noqa: T201


def run_example_6_combined(transactions):
    """Example 6: Combined hooks - Complete workflow."""
    print("Example 6: Combined hooks - Complete workflow")  # noqa: T201
    print("-" * 70)  # noqa: T201
    gsp6 = GSP(transactions)
    patterns6 = gsp6.search(
        min_support=0.3,
        preprocess_fn=normalize_lowercase,
        candidate_filter_fn=lambda c, s, ctx: len(c) <= 2 and s >= ctx.get("min_support_count", 0) * 1.2,
        postprocess_fn=add_metadata,
    )
    print("Mining with combined hooks:")  # noqa: T201
    print("  - Preprocessing: case normalization")  # noqa: T201
    print("  - Candidate filter: length <= 2 AND support >= 1.2x minimum")  # noqa: T201
    print("  - Postprocessing: add metadata")  # noqa: T201
    print()  # noqa: T201
    print("Results:")  # noqa: T201
    if patterns6 and "_metadata" in patterns6[0]:
        print(f"  Metadata: {patterns6[0]['_metadata']}")  # type: ignore # noqa: T201
        print(f"  Patterns: {len(patterns6) - 1} levels")  # noqa: T201
    print()  # noqa: T201


def run_example_7_progressive(transactions):
    """Example 7: Progressive filtering."""
    print("Example 7: Progressive length-based filtering")  # noqa: T201
    print("-" * 70)  # noqa: T201
    gsp7 = GSP(transactions)
    patterns7 = gsp7.search(min_support=0.25, preprocess_fn=normalize_lowercase, candidate_filter_fn=progressive_filter)
    print("Progressive filtering results:")  # noqa: T201
    for level_idx, level in enumerate(patterns7, start=1):
        if level:
            avg_support = sum(level.values()) / len(level)
            print(f"  Level {level_idx}: {len(level)} patterns, avg support: {avg_support:.2f}")  # noqa: T201
    print()  # noqa: T201


def main() -> None:
    """Run examples demonstrating custom hooks."""
    # Sample transactions for demonstration
    transactions = [
        ["Bread", "Milk", "Eggs"],
        ["bread", "butter", "milk"],
        ["Bread", "Milk", "Butter", "Cheese"],
        ["milk", "eggs"],
        ["Bread", "Butter"],
        ["BREAD", "MILK", "BUTTER", "EGGS"],
    ]

    print("=" * 70)  # noqa: T201
    print("GSP-Py Custom Hooks Examples")  # noqa: T201
    print("=" * 70)  # noqa: T201
    print()  # noqa: T201

    run_example_1_basic(transactions)
    run_example_2_preprocessing(transactions)
    run_example_3_lambda_filter(transactions)
    run_example_4_high_confidence(transactions)
    run_example_5_topk(transactions)
    run_example_6_combined(transactions)
    run_example_7_progressive(transactions)

    print("=" * 70)  # noqa: T201
    print("Examples complete!")  # noqa: T201
    print("=" * 70)  # noqa: T201


if __name__ == "__main__":
    main()
