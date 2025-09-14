use pyo3::prelude::*;
use rayon::prelude::*;
use std::collections::HashSet;
use std::env;

/// Check if `needle` appears as a contiguous subsequence in `hay`.
fn is_subseq_contiguous(hay: &[u32], needle: &[u32]) -> bool {
    let n = needle.len();
    if n == 0 { return false; }
    let m = hay.len();
    if n > m { return false; }
    let first = needle[0];
    let last = needle[n - 1];
    let mut i: usize = 0;
    while i + n <= m {
        if hay[i] != first { i += 1; continue; }
        if hay[i + n - 1] != last { i += 1; continue; }
        if &hay[i..i+n] == needle { return true; }
        i += 1;
    }
    false
}

/// Compute supports for candidate patterns across transactions.
///
/// This uses contiguous subsequence matching. The computation parallelizes over
/// candidates, and iterates transactions sequentially to avoid nested Rayon overhead.
#[pyfunction]
#[pyo3(text_signature = "(transactions, candidates, min_support, /)")]
fn compute_supports_py(py: Python<'_>, transactions: Bound<PyAny>, candidates: Bound<PyAny>, min_support: u32) -> PyResult<Vec<(Vec<u32>, u32)>> {
    // Convert Python lists -> Vec<Vec<u32>>
    let tx: Vec<Vec<u32>> = transactions.extract()?;
    let cands: Vec<Vec<u32>> = candidates.extract()?;

    // Optional presence prefilter controlled by env var GSPPY_PREFILTER ("1"/"true")
    let prefilter = env::var("GSPPY_PREFILTER")
        .ok()
        .map(|v| v == "1" || v.eq_ignore_ascii_case("true"))
        .unwrap_or(false);

    // Precompute per-transaction item sets if prefilter is enabled
    let tx_sets: Option<Vec<HashSet<u32>>> = if prefilter {
        Some(tx.iter().map(|t| t.iter().copied().collect::<HashSet<u32>>()).collect())
    } else { None };

    let out = py.allow_threads(|| {
        // Parallelize over candidates; iterate transactions sequentially per candidate
        let out: Vec<(Vec<u32>, u32)> = cands.par_iter()
            .map(|cand| {
                let mut freq: u32 = 0;
                for (idx, t) in tx.iter().enumerate() {
                    if let Some(ref sets) = tx_sets {
                        // Quick reject if any item in candidate is not present in this transaction
                        let set = &sets[idx];
                        if !cand.iter().all(|it| set.contains(it)) { continue; }
                    }
                    if is_subseq_contiguous(t, cand) { freq += 1; }
                }
                (cand.clone(), freq)
            })
            .filter(|(_, f)| *f >= min_support)
            .collect();
        out
    });

    Ok(out)
}

#[pymodule]
fn _gsppy_rust(_py: Python, m: &Bound<PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(compute_supports_py, m)?)?;
    Ok(())
}
