"""
solver_v1.py — Brute-Force Filter Solver (Baseline)

Strategy: Always pick the alphabetically first remaining candidate as the guess.
This is purely a correctness baseline — it works but is not optimal.

Use this as a benchmark comparison against the entropy solver (v2).
"""

from feedback import get_feedback, filter_candidates


class SolverV1:
    """
    Brute-force Wordle solver.

    At each step, picks the lexicographically first word from the
    remaining candidates. No scoring, no strategy — just correctness.

    This gives us a baseline ~4.5–5.0 average guess count to compare
    against the entropy-optimized v2.
    """

    FIRST_GUESS = "crane"  # Fixed opener — decent common-word heuristic

    def __init__(self, answers: list[str]):
        """
        Args:
            answers: List of all valid answer words.
        """
        self.all_answers = answers

    def solve(self, hidden_word: str, verbose: bool = False) -> int:
        """
        Simulate solving a Wordle game where the answer is `hidden_word`.

        Args:
            hidden_word: The word the solver is trying to find.
            verbose:     If True, print each guess and feedback.

        Returns:
            Number of guesses taken to find the answer.
        """
        candidates = list(self.all_answers)
        guess_count = 0

        for attempt in range(1, 7):  # Wordle allows 6 guesses
            # Pick the first remaining candidate as our guess
            # (Use fixed opener on the first guess for a small edge)
            if attempt == 1:
                guess = self.FIRST_GUESS
            else:
                guess = candidates[0]

            guess_count += 1
            pattern = get_feedback(guess, hidden_word)

            if verbose:
                from feedback import pattern_to_emoji
                print(f"  Attempt {attempt}: '{guess}' → {pattern_to_emoji(pattern)}  "
                      f"(candidates remaining: {len(candidates)})")

            if pattern == "22222":
                if verbose:
                    print(f"  ✅ Solved in {guess_count} guesses!")
                return guess_count

            # Narrow down candidates using the feedback
            candidates = filter_candidates(candidates, guess, pattern)

            if not candidates:
                # This shouldn't happen with a correct feedback function
                if verbose:
                    print("  ⚠️  No candidates left — this indicates a bug!")
                return guess_count

        # Ran out of guesses
        if verbose:
            print(f"  ❌ Failed to solve '{hidden_word}' in 6 guesses!")
        return guess_count


# --------------------------------------------------------------------------
# Quick demo
# --------------------------------------------------------------------------
if __name__ == "__main__":
    import os
    import sys

    # Load word list
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    with open(os.path.join(data_dir, 'answers.txt')) as f:
        answers = [w.strip().lower() for w in f if w.strip()]

    solver = SolverV1(answers)

    # Test on a few words
    test_words = ["crane", "chess", "plant", "tiger", "oxide", "jazzy", "glyph"]
    print("V1 Solver Demo — Brute Force\n")
    print(f"{'Word':<10} {'Guesses'}")
    print("-" * 20)

    for word in test_words:
        if word in answers:
            n = solver.solve(word)
            print(f"{word:<10} {n}")
        else:
            print(f"{word:<10} (not in answer list)")

    print("\n--- Detailed trace for 'chess' ---")
    solver.solve("chess", verbose=True)
