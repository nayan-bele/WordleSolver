"""
benchmark.py — Run both solvers against all answers and compare.

This is the "proof" component — the result you cite on your resume.

Runs:
    - SolverV1 (brute-force / first candidate)
    - SolverV2 (entropy-optimal)

Outputs:
    - Per-word guess counts
    - Average, max, distribution
    - % solved within 6 guesses
    - Saves results/benchmark_results.csv

Usage:
    python benchmark.py [--quick]   # --quick runs on first 100 words only
"""

import os
import sys
import csv
import time
import argparse
from collections import Counter

# Add src to path
sys.path.insert(0, os.path.dirname(__file__))
from solver_v1 import SolverV1
from solver_v2 import SolverV2


def load_words(filepath: str) -> list[str]:
    """Load a word list from a plain text file (one word per line)."""
    with open(filepath) as f:
        return [w.strip().lower() for w in f if w.strip()]


def run_benchmark(solver, answers: list[str], name: str) -> dict:
    """
    Run `solver` against every word in `answers` and collect statistics.

    Args:
        solver:  Solver instance with a .solve(word) method.
        answers: List of all answer words to simulate.
        name:    Label for progress display.

    Returns:
        Dictionary with 'results' (list of guess counts) and summary stats.
    """
    results = []
    n = len(answers)
    start = time.time()

    print(f"\n{'='*50}")
    print(f" Running {name} on {n} words...")
    print(f"{'='*50}")

    for i, word in enumerate(answers):
        guesses = solver.solve(word, verbose=False)
        results.append(guesses)

        # Progress bar every 100 words
        if (i + 1) % 100 == 0 or (i + 1) == n:
            elapsed = time.time() - start
            rate = (i + 1) / elapsed
            eta = (n - i - 1) / rate if rate > 0 else 0
            bar_len = 30
            filled = int(bar_len * (i + 1) / n)
            bar = '█' * filled + '░' * (bar_len - filled)
            print(f"  [{bar}] {i+1}/{n} ({rate:.1f} w/s, ETA: {eta:.0f}s)", end='\r')

    elapsed = time.time() - start
    print(f"\n  Completed in {elapsed:.1f}s")

    # Compute summary stats
    avg = sum(results) / len(results)
    max_g = max(results)
    min_g = min(results)
    dist = Counter(results)
    within_6 = sum(1 for r in results if r <= 6) / len(results) * 100
    failed = sum(1 for r in results if r > 6)

    return {
        'name': name,
        'results': results,
        'avg': avg,
        'max': max_g,
        'min': min_g,
        'dist': dist,
        'within_6_pct': within_6,
        'failed': failed,
        'total': len(results),
        'time_s': elapsed,
    }


def print_summary(stats: dict):
    """Print a formatted summary for one solver's benchmark results."""
    print(f"\n  📊 Results for: {stats['name']}")
    print(f"  {'─'*40}")
    print(f"  Average guesses : {stats['avg']:.4f}")
    print(f"  Min guesses     : {stats['min']}")
    print(f"  Max guesses     : {stats['max']}")
    print(f"  Within 6 guesses: {stats['within_6_pct']:.2f}%  ({stats['total'] - stats['failed']}/{stats['total']})")
    print(f"  Failed (>6)     : {stats['failed']}")
    print(f"\n  Guess distribution:")
    for k in sorted(stats['dist'].keys()):
        count = stats['dist'][k]
        bar = '▓' * (count // 10)
        label = "FAIL" if k == 7 else str(k)
        print(f"    {label} guesses: {count:4d}  {bar}")


def save_csv(all_stats: list[dict], answers: list[str], out_path: str):
    """Save per-word results to a CSV file for further analysis."""
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    
    headers = ['word'] + [s['name'] for s in all_stats]
    with open(out_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for i, word in enumerate(answers):
            row = [word] + [s['results'][i] for s in all_stats]
            writer.writerow(row)
    print(f"\n  💾 Results saved to: {out_path}")


def print_comparison(v1_stats: dict, v2_stats: dict):
    """Print a side-by-side comparison table."""
    print("\n" + "=" * 55)
    print(f"  {'COMPARISON TABLE':^51}")
    print("=" * 55)
    print(f"  {'Metric':<25} {'V1 (Brute Force)':>12} {'V2 (Entropy)':>12}")
    print(f"  {'-'*25} {'-'*12} {'-'*12}")
    print(f"  {'Average guesses':<25} {v1_stats['avg']:>12.4f} {v2_stats['avg']:>12.4f}")
    print(f"  {'Max guesses':<25} {v1_stats['max']:>12} {v2_stats['max']:>12}")
    print(f"  {'Solved within 6 (%)':<25} {v1_stats['within_6_pct']:>11.2f}% {v2_stats['within_6_pct']:>11.2f}%")
    print(f"  {'Failed (>6 guesses)':<25} {v1_stats['failed']:>12} {v2_stats['failed']:>12}")
    print(f"  {'Runtime':<25} {v1_stats['time_s']:>11.1f}s {v2_stats['time_s']:>11.1f}s")
    print("=" * 55)
    improvement = v1_stats['avg'] - v2_stats['avg']
    print(f"\n  🔥 Entropy solver saves {improvement:.2f} avg guesses vs brute force!")


def main():
    parser = argparse.ArgumentParser(description="Wordle Solver Benchmark")
    parser.add_argument('--quick', action='store_true',
                        help='Quick mode: only run first 100 words (for testing)')
    parser.add_argument('--v2-only', action='store_true',
                        help='Skip V1 benchmark (much faster)')
    args = parser.parse_args()

    # File paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, '..', 'data')
    results_dir = os.path.join(script_dir, '..', 'results')

    # Load word lists
    answers_path = os.path.join(data_dir, 'answers.txt')
    print(f"Loading words from: {answers_path}")
    answers = load_words(answers_path)

    if args.quick:
        answers = answers[:100]
        print(f"⚡ Quick mode: using first {len(answers)} words")

    print(f"Loaded {len(answers)} answer words")

    all_stats = []

    # --- Run V1 ---
    if not args.v2_only:
        v1 = SolverV1(answers)
        v1_stats = run_benchmark(v1, answers, "V1 — Brute Force")
        print_summary(v1_stats)
        all_stats.append(v1_stats)

    # --- Run V2 ---
    v2 = SolverV2(answers)
    v2_stats = run_benchmark(v2, answers, "V2 — Entropy Optimal")
    print_summary(v2_stats)
    all_stats.append(v2_stats)

    # --- Comparison ---
    if not args.v2_only:
        print_comparison(v1_stats, v2_stats)

    # --- Save results ---
    csv_path = os.path.join(results_dir, 'benchmark_results.csv')
    save_csv(all_stats, answers, csv_path)

    print("\n✅ Benchmark complete!")


if __name__ == "__main__":
    main()
