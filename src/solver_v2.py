"""
solver_v2.py — Entropy-Optimal Wordle Solver

The core idea: at each step, pick the guess that maximizes expected
information gain (Shannon entropy) over the remaining candidate set.

Math recap:
    For a guess g and candidate pool C:
    1. Partition C into buckets by feedback pattern:
       buckets[pattern] = [word in C | get_feedback(g, word) == pattern]
    2. Probability of each bucket: p_k = |bucket_k| / |C|
    3. Entropy of guess g: H(g) = -Σ p_k * log2(p_k)
    4. Best guess = argmax H(g) over all allowed guesses

Higher entropy → guess splits the candidates more evenly → more info gained.
A perfect split of 256 candidates into 256 buckets of 1 each gives log2(256)=8 bits.
A terrible guess that puts all 256 into one bucket gives 0 bits.

Speed optimization:
    - Turn 1: Use a precomputed best opener ("CRANE" or "SALET") — saves ~30s
    - Turn 2+: Only score remaining candidates as potential guesses (not all 13k)
               This is a small accuracy tradeoff for a massive speed win.
"""

import math
from collections import defaultdict
from feedback import get_feedback, filter_candidates


# Best first guess — precomputed offline by running entropy on all 12,972 guesses
# Against the full 2,315-word answer set. Top contenders: "salet", "crane", "trace"
BEST_FIRST_GUESS = "crane"


def compute_entropy(guess: str, candidates: list[str]) -> float:
    """
    Compute the expected information gain (Shannon entropy) of a guess
    given the current candidate set.

    This is the core of the entropy-based solver.

    Args:
        guess:      The candidate guess word to evaluate.
        candidates: Current list of possible answers.

    Returns:
        Entropy H(guess) in bits. Higher is better.
    """
    n = len(candidates)
    if n == 0:
        return 0.0

    # Group candidates by the feedback pattern they'd produce vs this guess
    buckets: dict[str, int] = defaultdict(int)
    for word in candidates:
        pattern = get_feedback(guess, word)
        buckets[pattern] += 1

    # Shannon entropy: H = -Σ p * log2(p)
    entropy = 0.0
    for count in buckets.values():
        p = count / n
        entropy -= p * math.log2(p)

    return entropy


def best_guess(candidates: list[str], all_guesses: list[str] | None = None) -> tuple[str, float]:
    """
    Find the guess that maximizes expected entropy over the candidate set.

    Strategy:
    - If candidates <= 2, just guess the first candidate (no need to compute).
    - Otherwise, score all candidates (+ optionally all allowed guesses)
      and return the one with highest entropy.

    We search only `candidates` for turns 2+ (not all 13k guesses). This is
    intentional: it's ~10x faster with negligible accuracy loss in practice.

    Args:
        candidates:  Current list of possible answers.
        all_guesses: Full allowed guess list (used for turn 1 only, or if passed in).

    Returns:
        Tuple of (best_word, entropy_score).
    """
    if len(candidates) <= 2:
        return candidates[0], 1.0  # Only 1–2 options left, just guess it

    # Which pool do we search? Default to candidates (fast for turns 2+)
    search_pool = all_guesses if all_guesses is not None else candidates

    best_word = candidates[0]
    best_score = -1.0

    for guess in search_pool:
        score = compute_entropy(guess, candidates)
        if score > best_score:
            best_score = score
            best_word = guess

    return best_word, best_score


class SolverV2:
    """
    Entropy-optimal Wordle solver.

    At each step, picks the guess that maximizes expected information gain
    (Shannon entropy) over the current candidate pool.

    Turn 1: Always uses the precomputed best opener (CRANE) to skip a slow search.
    Turn 2+: Searches remaining candidates for the entropy-maximizing next guess.
    """

    def __init__(self, answers: list[str], all_guesses: list[str] | None = None):
        """
        Args:
            answers:    List of all valid answer words.
            all_guesses: Full allowed guess list (optional). If None, uses `answers`.
        """
        self.all_answers = answers
        self.all_guesses = all_guesses if all_guesses is not None else answers

    def solve(self, hidden_word: str, verbose: bool = False) -> int:
        """
        Simulate solving a Wordle game where the answer is `hidden_word`.

        Args:
            hidden_word: The word the solver is trying to find.
            verbose:     If True, print each guess, feedback, and candidate count.

        Returns:
            Number of guesses taken (1–6, or 7 if failed within 6).
        """
        candidates = list(self.all_answers)
        guess_count = 0

        for attempt in range(1, 8):  # Allow 7 as a "fail" sentinel
            # --- Pick our guess ---
            if attempt == 1:
                # Use precomputed best opener to skip slow full-search on turn 1
                guess = BEST_FIRST_GUESS
                entropy_score = None
            else:
                guess, entropy_score = best_guess(candidates)

            guess_count += 1
            pattern = get_feedback(guess, hidden_word)

            if verbose:
                from feedback import pattern_to_emoji
                ent_str = f", H={entropy_score:.3f} bits" if entropy_score else ""
                print(f"  Attempt {attempt}: '{guess}' → {pattern_to_emoji(pattern)}"
                      f"  [{len(candidates)} candidates{ent_str}]")

            # --- Check if solved ---
            if pattern == "22222":
                if verbose:
                    print(f"  ✅ Solved '{hidden_word}' in {guess_count} guesses!")
                return guess_count

            # --- Filter candidates ---
            candidates = filter_candidates(candidates, guess, pattern)

            if not candidates:
                if verbose:
                    print(f"  ⚠️  No candidates left — bug or word not in list!")
                return guess_count

            if attempt >= 6:
                if verbose:
                    print(f"  ❌ Ran out of guesses for '{hidden_word}'!")
                return 7  # Failed sentinel

        return guess_count

    def suggest(self, candidates: list[str]) -> tuple[str, float]:
        """
        For use in interactive (CLI) mode — suggest the best guess
        given the current candidate pool without simulating.

        Args:
            candidates: Current possible answers.

        Returns:
            Tuple of (best_guess, entropy_bits).
        """
        return best_guess(candidates)


# --------------------------------------------------------------------------
# Quick demo
# --------------------------------------------------------------------------
if __name__ == "__main__":
    import os

    data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    with open(os.path.join(data_dir, 'answers.txt')) as f:
        answers = [w.strip().lower() for w in f if w.strip()]

    solver = SolverV2(answers)

    # Test on a few words with verbose output
    test_words = ["chess", "plant", "oxide", "glyph"]
    print("V2 Solver Demo — Entropy-Optimal\n")

    for word in test_words:
        if word in answers:
            print(f"\nSolving '{word}':")
            solver.solve(word, verbose=True)
        else:
            print(f"'{word}' not in answer list, skipping")
