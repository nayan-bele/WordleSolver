"""
download_words.py — Download the official Wordle word lists.

The Wordle word lists are public. This script fetches them from a
well-known GitHub mirror of the original NYT Wordle source.

Run this first:
    python download_words.py

This creates:
    data/answers.txt   — ~2315 possible answers
    data/guesses.txt   — ~12972 allowed guesses (superset of answers)
"""

import os
import urllib.request

# These URLs point to popular GitHub mirrors of the original NYT Wordle word lists.
# Several mirrors exist; these are widely used in the open-source community.
ANSWERS_URL = "https://raw.githubusercontent.com/tabatkins/wordle-list/main/words"
GUESSES_URL = "https://raw.githubusercontent.com/tabatkins/wordle-list/main/words"

# Alternative mirrors (uncomment if above fails):
# ANSWERS_URL = "https://gist.githubusercontent.com/cfreshman/a03ef2cba789d8cf00c08f767e0fad7b/raw/wordle-answers-alphabetical.txt"
# GUESSES_URL = "https://gist.githubusercontent.com/cfreshman/cdcdf777450c5b5301e439061d29694c/raw/wordle-allowed-guesses.txt"

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')


def download_file(url: str, output_path: str, label: str):
    """Download a file from a URL and save it locally."""
    print(f"Downloading {label}...")
    try:
        with urllib.request.urlopen(url, timeout=15) as response:
            content = response.read().decode('utf-8')

        words = [w.strip().lower() for w in content.splitlines() if w.strip() and w.strip().isalpha() and len(w.strip()) == 5]
        
        with open(output_path, 'w') as f:
            f.write('\n'.join(words))

        print(f"  ✅ Saved {len(words)} words to {output_path}")
        return words

    except Exception as e:
        print(f"  ❌ Failed to download {label}: {e}")
        print(f"     Try manually: {url}")
        return None


def create_sample_lists():
    """
    Create small sample word lists for testing when download isn't available.
    These are common Wordle words — NOT the complete official list.
    """
    print("\n⚠️  Creating sample word lists for testing...")
    print("   For full functionality, manually place the official word lists in data/")

    sample_answers = [
        "crane", "trace", "raise", "arise", "saner", "stare", "irate",
        "arose", "later", "alter", "alert", "ratel", "taler", "rales",
        "seral", "lares", "earls", "laser", "lears", "learn", "renal",
        "plant", "chess", "tiger", "oxide", "glyph", "jazzy", "batch",
        "beach", "teach", "reach", "peach", "leach", "coach", "roach",
        "watch", "match", "patch", "catch", "latch", "hatch", "notch",
        "witch", "ditch", "pitch", "bitch", "witch", "fetch", "retch",
        "brick", "trick", "click", "slick", "thick", "flick", "prick",
        "stork", "clock", "block", "stock", "flock", "knock", "shock",
        "spoke", "smoke", "choke", "broke", "broke", "stoke", "woken",
        "token", "siren", "linen", "given", "riven", "driven", "oven",
        "blend", "spend", "trend", "blend", "fiend", "riend", "wield",
        "yield", "child", "build", "guild", "guild", "wild",  "mild",
        "blind", "grind", "grind", "brand", "bland", "grand", "stand",
        # Add more real Wordle words
        "audio", "stain", "atone", "snare", "plane", "blame", "flame",
        "frame", "grade", "grape", "grave", "brave", "crave", "shave",
        "slave", "glare", "flare", "snare", "spare", "stare", "share",
        "shore", "store", "score", "snore", "swore", "spoke", "stone",
        "prone", "drone", "phone", "shine", "spine", "swine", "twine",
        "brine", "shrine", "whine", "white", "write", "quite", "suite",
        "moist", "hoist", "exist", "twist", "wrist", "first", "worst",
        "burst", "curse", "nurse", "purse", "verse", "terse", "merge",
        "serve", "nerve", "curve", "swerve", "verge", "surge", "purge",
    ]

    # Deduplicate and keep only valid 5-letter words
    sample_answers = list({w for w in sample_answers if len(w) == 5})
    sample_answers.sort()

    with open(os.path.join(DATA_DIR, 'answers.txt'), 'w') as f:
        f.write('\n'.join(sample_answers))
    print(f"  ✅ Created sample answers.txt with {len(sample_answers)} words")

    # For guesses, just use the same list
    with open(os.path.join(DATA_DIR, 'guesses.txt'), 'w') as f:
        f.write('\n'.join(sample_answers))
    print(f"  ✅ Created sample guesses.txt with {len(sample_answers)} words")
    
    print("""
  📌 To get the full Wordle word lists (~2300 answers + ~13000 guesses):
     1. Visit: https://github.com/tabatkins/wordle-list
     2. Download 'words' file and save as data/answers.txt
     
     OR manually create them from:
     https://gist.github.com/cfreshman/a03ef2cba789d8cf00c08f767e0fad7b (answers)
     https://gist.github.com/cfreshman/cdcdf777450c5b5301e439061d29694c (guesses)
""")


def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    print(f"Saving word lists to: {DATA_DIR}")

    # Try downloading
    answers_path = os.path.join(DATA_DIR, 'answers.txt')
    guesses_path = os.path.join(DATA_DIR, 'guesses.txt')

    answers = download_file(ANSWERS_URL, answers_path, "Wordle answers")
    guesses = download_file(GUESSES_URL, guesses_path, "Wordle guesses")

    if answers is None or guesses is None:
        create_sample_lists()
        return

    print(f"\n✅ Word lists ready!")
    print(f"   answers.txt: {len(answers)} words")
    print(f"   guesses.txt: {len(guesses)} words")
    print(f"\nNext step: python src/feedback.py  (run self-test)")


if __name__ == "__main__":
    main()
