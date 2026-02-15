import marimo

__generated_with = "0.19.11"
app = marimo.App()


@app.cell
def _():
    """
    Example custom hooks for GSP-Py demonstrating preprocessing, postprocessing,
    and candidate filtering capabilities.

    This module provides practical examples of how to create custom hooks for
    the GSP algorithm to implement advanced filtering, transformation, and
    pattern mining strategies.

    Note on Hook Signatures:
        Many functions in this module accept additional parameters beyond the
        standard hook signature. These are designed to be used with functools.partial
        to create parameterized hooks. For example:

            from functools import partial
            filter_fn = partial(length_constraint_filter, max_length=2)
            patterns = gsp.search(min_support=0.3, candidate_filter_fn=filter_fn)

        Standard signatures (without additional parameters):
        - preprocess_fn(transactions) -> transactions
        - candidate_filter_fn(candidate, support_count, context) -> bool
        - postprocess_fn(patterns) -> patterns
    """

    from typing import Any, Dict, List, Tuple, Optional

    # ============================================================================
    # Preprocessing Hooks - Transform transactions before mining
    # ============================================================================


    def normalize_to_lowercase(transactions: Any) -> Any:
        """
        Normalize all items in transactions to lowercase.

        Useful for case-insensitive pattern mining.

        Example:
            >>> from gsppy.gsp import GSP
            >>> from examples.custom_hooks import normalize_to_lowercase
            >>> transactions = [["Apple", "Banana"], ["APPLE", "orange"]]
            >>> gsp = GSP(transactions)
            >>> patterns = gsp.search(min_support=0.5, preprocess_fn=normalize_to_lowercase)
        """
        result = []
        for tx in transactions:
            converted_tx = []
            for itemset in tx:
                if itemset:
                    converted_itemset = tuple(item.lower() if isinstance(item, str) else item for item in itemset)
                    converted_tx.append(converted_itemset)
            result.append(tuple(converted_tx))
        return result


    def filter_short_transactions(transactions: Any, min_length: int = 3) -> Any:
        """
        Filter out transactions with fewer than min_length items.

        Useful for focusing on longer, more meaningful patterns.

        Example:
            >>> from functools import partial
            >>> preprocess = partial(filter_short_transactions, min_length=4)
            >>> patterns = gsp.search(min_support=0.3, preprocess_fn=preprocess)
        """
        return [tx for tx in transactions if len(tx) >= min_length]


    # ============================================================================
    # Candidate Filter Hooks - Dynamic runtime filtering
    # ============================================================================


    def length_constraint_filter(
        candidate: Tuple[str, ...], _support_count: int, _context: Dict[str, Any], max_length: int = 3
    ) -> bool:
        """
        Keep only patterns up to a maximum length.

        Useful for controlling pattern complexity and mining time.

        Example:
            >>> from functools import partial
            >>> filter_fn = partial(length_constraint_filter, max_length=2)
            >>> patterns = gsp.search(min_support=0.3, candidate_filter_fn=filter_fn)
        """
        return len(candidate) <= max_length


    def high_confidence_filter(_candidate: Tuple[str, ...], support_count: int, context: Dict[str, Any]) -> bool:
        """
        Keep candidates with support significantly above minimum threshold.

        Filters for high-confidence patterns by requiring support >= 1.5x minimum.

        Example:
            >>> patterns = gsp.search(min_support=0.3, candidate_filter_fn=high_confidence_filter)
        """
        min_support = context.get("min_support_count", 0)
        return support_count >= min_support * 1.5


    def item_whitelist_filter(
        candidate: Tuple[str, ...],
        _support_count: int,
        _context: Dict[str, Any],
        required_items: Optional[List[str]] = None,
    ) -> bool:
        """
        Keep only patterns containing at least one item from the whitelist.

        Useful for focusing on specific items of interest.

        Example:
            >>> from functools import partial
            >>> filter_fn = partial(item_whitelist_filter, required_items=["milk", "bread"])
            >>> patterns = gsp.search(min_support=0.3, candidate_filter_fn=filter_fn)
        """
        if required_items is None:
            return True
        return any(item in candidate for item in required_items)


    def progressive_length_filter(candidate: Tuple[str, ...], support_count: int, context: Dict[str, Any]) -> bool:
        """
        Apply progressive filtering: stricter requirements for longer patterns.

        - Length 1-2: keep all (above min support)
        - Length 3-4: require 1.2x min support
        - Length 5+: require 1.5x min support

        Example:
            >>> patterns = gsp.search(min_support=0.3, candidate_filter_fn=progressive_length_filter)
        """
        min_support = context.get("min_support_count", 1)
        length = len(candidate)

        if length <= 2:
            return True
        elif length <= 4:
            return support_count >= min_support * 1.2
        else:
            return support_count >= min_support * 1.5


    # ============================================================================
    # Postprocessing Hooks - Transform results after mining
    # ============================================================================


    def top_k_patterns_per_level(patterns: Any, k: int = 5) -> Any:
        """
        Keep only the top-k most frequent patterns at each level.

        Useful for reducing output size and focusing on most important patterns.

        Example:
            >>> from functools import partial
            >>> postprocess = partial(top_k_patterns_per_level, k=10)
            >>> patterns = gsp.search(min_support=0.2, postprocess_fn=postprocess)
        """
        result = []
        for level in patterns:
            if level:
                # Sort by support (descending) and take top k
                sorted_patterns = sorted(level.items(), key=lambda x: x[1], reverse=True)[:k]
                result.append(dict(sorted_patterns))
            else:
                result.append(level)
        return result


    def limit_pattern_levels(patterns: Any, max_levels: int = 3) -> Any:
        """
        Limit output to first N levels of patterns.

        Useful for controlling output size and mining time.

        Example:
            >>> from functools import partial
            >>> postprocess = partial(limit_pattern_levels, max_levels=2)
            >>> patterns = gsp.search(min_support=0.3, postprocess_fn=postprocess)
        """
        return patterns[:max_levels]


    def filter_by_minimum_support(patterns: Any, min_support: int = 5) -> Any:
        """
        Post-filter patterns by absolute minimum support count.

        Applies additional support threshold after initial mining.

        Example:
            >>> from functools import partial
            >>> postprocess = partial(filter_by_minimum_support, min_support=10)
            >>> patterns = gsp.search(min_support=0.1, postprocess_fn=postprocess)
        """
        return [{k: v for k, v in level.items() if v >= min_support} for level in patterns]


    def add_pattern_statistics(patterns: Any) -> Any:
        """
        Add metadata with pattern statistics as first element.

        Enriches results with summary information.

        Example:
            >>> patterns = gsp.search(min_support=0.3, postprocess_fn=add_pattern_statistics)
            >>> print(patterns[0])  # {'_metadata': {'total_patterns': 42, ...}}
        """
        total_patterns = sum(len(level) for level in patterns)
        max_support = max((max(level.values()) if level else 0) for level in patterns)
        avg_support = sum(sum(level.values()) for level in patterns) / total_patterns if total_patterns > 0 else 0

        metadata = {
            "_metadata": {
                "total_patterns": total_patterns,
                "num_levels": len(patterns),
                "max_support": max_support,
                "avg_support": avg_support,
            }
        }
        return [metadata] + patterns


    # ============================================================================
    # Combined Workflow Examples
    # ============================================================================


    def market_basket_workflow(transactions: List[List[str]], min_support: float = 0.3) -> Any:
        """
        Complete market basket analysis workflow with preprocessing and filtering.

        Combines:
        - Lowercase normalization
        - Length-based filtering
        - Top-10 results per level

        Example:
            >>> from gsppy.gsp import GSP
            >>> transactions = [["Bread", "Milk"], ["bread", "BUTTER"], ...]
            >>> gsp = GSP(transactions)
            >>> patterns = gsp.search(
            ...     min_support=0.3,
            ...     preprocess_fn=normalize_to_lowercase,
            ...     candidate_filter_fn=lambda c, s, ctx: len(c) <= 3,
            ...     postprocess_fn=lambda p: top_k_patterns_per_level(p, k=10),
            ... )
        """
        from gsppy.gsp import GSP

        gsp = GSP(transactions)
        return gsp.search(
            min_support=min_support,
            preprocess_fn=normalize_to_lowercase,
            candidate_filter_fn=lambda c, _s, _ctx: len(c) <= 3,
            postprocess_fn=lambda p: top_k_patterns_per_level(p, k=10),
        )


    # ============================================================================
    # CLI Usage Examples (documented in strings)
    # ============================================================================

    """
    CLI Examples:

    1. Basic filtering:
       $ gsppy --file data.json --min_support 0.3 \\
               --candidate-filter-hook examples.custom_hooks.high_confidence_filter

    2. Preprocessing:
       $ gsppy --file data.json --min_support 0.3 \\
               --preprocess-hook examples.custom_hooks.normalize_to_lowercase

    3. Postprocessing:
       $ gsppy --file data.json --min_support 0.2 \\
               --postprocess-hook examples.custom_hooks.add_pattern_statistics

    4. Combined hooks:
       $ gsppy --file data.json --min_support 0.3 \\
               --preprocess-hook examples.custom_hooks.normalize_to_lowercase \\
               --candidate-filter-hook examples.custom_hooks.progressive_length_filter \\
               --postprocess-hook examples.custom_hooks.add_pattern_statistics

    Note: The hooks module must be in Python path (e.g., in examples/ directory)
    """
    return


if __name__ == "__main__":
    app.run()
