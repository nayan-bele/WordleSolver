"""
cli.py — Interactive Wordle Solver Assistant

Use this tool while playing the real Wordle game at nytimes.com/games/wordle.

How to use:
    1. Run: python cli.py
    2. The solver suggests the best word to type into Wordle.
    3. Type that word into Wordle and see what colors you get.
    4. Enter the feedback here as a 5-character string:
         2 = Green  🟩 (correct letter + position)
         1 = Yellow 🟨 (correct letter, wrong position)
         0 = Gray   ⬜ (letter not in word)
    5. Repeat until solved!

Example session:
    Suggested guess: CRANE
    Enter feedback (e.g. 22010): 00120
    [🟩🟩🟨⬜🟩] candidates: 47 remaining

    Suggested guess: TRAIL
    Enter feedback: 22222
    ✅ Solved in 2 guesses!
"""

import os
import sys
import readline  # For nicer input editing in terminal

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from feedback import get_feedback, filter_candidates, pattern_to_emoji
from solver_v2 import BEST_FIRST_GUESS, best_guess


BANNER = """
╔══════════════════════════════════════════════════════╗
║          🟩 WORDLE SOLVER — Entropy Edition 🟩        ║
║   Powered by Shannon Information Theory              ║
╚══════════════════════════════════════════════════════╝
"""

HELP_TEXT = """
Feedback guide:
  2 → 🟩 Green  (correct letter, correct position)
  1 → 🟨 Yellow (correct letter, wrong position)
  0 → ⬜ Gray   (letter not in word)

Enter feedback as 5 digits, e.g.:  22010
Commands:  'quit' to exit  |  'list' to show remaining candidates
"""


def validate_feedback(feedback: str) -> bool:
    """Check that feedback is a valid 5-char string of 0/1/2."""
    return len(feedback) == 5 and all(c in '012' for c in feedback)


def load_answers(data_dir: str) -> list[str]:
    """Load the answer word list."""
    path = os.path.join(data_dir, 'answers.txt')
    with open(path) as f:
        return [w.strip().lower() for w in f if w.strip()]


def run_cli(answers: list[str]):
    """Main interactive loop for the Wordle assistant."""
    print(BANNER)
    print(HELP_TEXT)

    candidates = list(answers)
    attempt = 0
    solved = False

    while attempt < 6:
        attempt += 1

        print(f"\n── Turn {attempt} ──────────────────────────────")
        print(f"   Remaining candidates: {len(candidates)}")

        # Show top candidates if small enough
        if len(candidates) <= 10:
            print(f"   Possible answers: {', '.join(candidates[:10])}")

        # Pick best guess
        if attempt == 1:
            guess = BEST_FIRST_GUESS
            print(f"\n   💡 Suggested guess: {guess.upper()}  (precomputed best opener)")
        else:
            if len(candidates) == 1:
                guess = candidates[0]
                print(f"\n   💡 Only one candidate left!")
                print(f"   💡 Suggested guess: {guess.upper()}")
            else:
                guess, entropy = best_guess(candidates)
                print(f"\n   💡 Suggested guess: {guess.upper()}  "
                      f"(H = {entropy:.3f} bits)")

        # Get feedback from user
        while True:
            try:
                raw = input("\n   Enter feedback (or 'list'/'quit'): ").strip().lower()
            except (KeyboardInterrupt, EOFError):
                print("\n\nExiting solver. Good luck! 🍀")
                return

            if raw == 'quit':
                print("\nExiting solver. Good luck! 🍀")
                return

            if raw == 'list':
                print(f"\n   Candidates ({len(candidates)}):")
                cols = 6
                for i in range(0, len(candidates), cols):
                    print("   " + "  ".join(f"{w:<8}" for w in candidates[i:i+cols]))
                continue

            if validate_feedback(raw):
                feedback = raw
                break
            else:
                print("   ⚠️  Invalid feedback — enter 5 digits using only 0, 1, 2")

        # Display what was entered
        emoji = pattern_to_emoji(feedback)
        print(f"   {guess.upper()} → {emoji}")

        # Check if solved
        if feedback == '22222':
            print(f"\n╔═══════════════════════════════════════╗")
            print(f"║  🎉 Solved in {attempt} guess{'es' if attempt > 1 else ''}!             ║")
            print(f"╚═══════════════════════════════════════╝")
            solved = True
            break

        # Filter candidates
        candidates = filter_candidates(candidates, guess, feedback)

        if not candidates:
            print("\n   ⚠️  No valid candidates remain!")
            print("   This might mean the answer isn't in our word list,")
            print("   or you entered feedback incorrectly.")
            break

    if not solved:
        print("\n   ❌ Couldn't solve this one within 6 guesses.")
        print(f"   Remaining candidates were: {candidates[:20]}")

    # Ask to play again
    print()
    try:
        again = input("Play again? (y/n): ").strip().lower()
        if again == 'y':
            run_cli(answers)
    except (KeyboardInterrupt, EOFError):
        pass
    print("\nThanks for using the Wordle Solver! 🟩🟨⬜")


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, '..', 'data')

    if not os.path.exists(os.path.join(data_dir, 'answers.txt')):
        print("❌ Error: answers.txt not found in data/ directory.")
        print("   Run: python download_words.py")
        sys.exit(1)

    answers = load_answers(data_dir)
    print(f"Loaded {len(answers)} answer words.")
    run_cli(answers)


if __name__ == "__main__":
    main()
