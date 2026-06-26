"""
feedback.py — Core feedback engine for the Wordle Solver.

This is the most critical piece of the project. The feedback function must
correctly handle duplicate letters exactly as the real Wordle game does.

Feedback encoding:
    '2' = Green  (correct letter, correct position)
    '1' = Yellow (correct letter, wrong position)
    '0' = Gray   (letter not in word, or already accounted for)

    Example:
        get_feedback("crane", "trace") -> "12202"
        get_feedback("speed", "creep") -> "01220"
        get_feedback("hello", "hello") -> "22222"
"""

from collections import Counter


def get_feedback(guess: str, answer: str) -> str:
    """
    Compute the Wordle feedback pattern for a given guess against an answer.

    The algorithm (matching Wordle's real rules):
    1. First pass — mark all exact position matches as GREEN (2).
       Remove these letters from the "available pool".
    2. Second pass — for remaining positions, check if the guessed letter
       exists in the pool. If yes, mark YELLOW (1) and remove from pool.
       Otherwise, mark GRAY (0).

    This two-pass approach is essential to handle duplicate letters correctly.
    For example: guess="speed", answer="creep"
        - 's' -> gray (no 's' in answer)
        - 'p' -> check: 'p' in answer but not green -> yellow
        - 'e' -> green ('e' at index 2 matches)
        - 'e' -> 'e' appears once more in answer (the 'e' at index 3)
                 but we only have one 'e' left in the pool -> yellow
        - 'd' -> gray
        Result: "01121"

    Args:
        guess:  5-letter guess word (lowercase)
        answer: 5-letter answer word (lowercase)

    Returns:
        5-character string of '2', '1', '0' representing the feedback.
    """
    assert len(guess) == 5, f"Guess must be 5 letters, got: '{guess}'"
    assert len(answer) == 5, f"Answer must be 5 letters, got: '{answer}'"

    result = ['0'] * 5

    # Track which answer letters are still "available" (not yet matched green)
    answer_pool = list(answer)

    # --- Pass 1: Mark greens and remove matched letters from pool ---
    for i in range(5):
        if guess[i] == answer[i]:
            result[i] = '2'
            answer_pool[i] = None  # Consume this letter

    # --- Pass 2: Mark yellows for remaining positions ---
    for i in range(5):
        if result[i] == '2':
            continue  # Already matched green

        letter = guess[i]
        if letter in answer_pool:
            result[i] = '1'
            # Consume one occurrence so duplicates are handled correctly
            answer_pool[answer_pool.index(letter)] = None

    return ''.join(result)


def filter_candidates(candidates: list[str], guess: str, pattern: str) -> list[str]:
    """
    Filter the candidate word list to only words that would produce
    the given feedback pattern if 'guess' were played against them.

    This is how we narrow the search space after each guess.

    Args:
        candidates: Current list of possible answer words
        guess:      The word that was guessed
        pattern:    The feedback pattern received (e.g. "22010")

    Returns:
        Filtered list of candidates consistent with the feedback.
    """
    return [word for word in candidates if get_feedback(guess, word) == pattern]


def pattern_to_emoji(pattern: str) -> str:
    """Convert a '210' pattern string to emoji for display."""
    mapping = {'2': '🟩', '1': '🟨', '0': '⬜'}
    return ''.join(mapping[c] for c in pattern)


# --------------------------------------------------------------------------
# Quick self-test (run this file directly to verify the feedback function)
# --------------------------------------------------------------------------
if __name__ == "__main__":
    test_cases = [
        # (guess, answer, expected_pattern)
        ("crane", "trace", "12202"),   # c=yellow,r=green,a=green,n=gray,e=green
        ("hello", "hello", "22222"),   # Perfect match
        ("speed", "creep", "01220"),   # s=gray,p=yellow,e=green,e=green,d=gray
        ("aabbb", "bbaaa", "11110"),   # All duplicates
        ("aaaaa", "aabbb", "22000"),   # Only first two a's are green
        ("tower", "tower", "22222"),   # Trivial
        ("crane", "crane", "22222"),   # Trivial
        ("abcde", "fghij", "00000"),   # All gray
        ("speed", "speed", "22222"),   # Perfect
    ]

    print("Running feedback function tests...\n")
    all_passed = True

    for guess, answer, expected in test_cases:
        result = get_feedback(guess, answer)
        emoji = pattern_to_emoji(result)
        status = "✅" if result == expected else "❌"
        if result != expected:
            all_passed = False
        print(f"{status} guess='{guess}', answer='{answer}' → {result} {emoji} (expected: {expected})")

    print(f"\n{'All tests passed! ✅' if all_passed else 'Some tests FAILED ❌'}")

    # Demo the filter function
    print("\n--- Filter Demo ---")
    sample_candidates = ["crane", "trace", "raise", "arise", "saner"]
    guess, pattern = "crane", "01220"
    filtered = filter_candidates(sample_candidates, guess, pattern)
    print(f"Guess: '{guess}', Pattern: {pattern} {pattern_to_emoji(pattern)}")
    print(f"Candidates before: {sample_candidates}")
    print(f"Candidates after:  {filtered}")
