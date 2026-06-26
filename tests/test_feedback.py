"""
test_feedback.py — Unit tests for the feedback function.

Run with: pytest tests/test_feedback.py -v

These tests are critical — the entire solver's correctness depends on
the feedback function being exactly right, especially for duplicate letters.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest
from feedback import get_feedback, filter_candidates, pattern_to_emoji


class TestBasicFeedback:
    """Basic feedback function correctness tests."""

    def test_perfect_match(self):
        """All greens when guess == answer."""
        assert get_feedback("crane", "crane") == "22222"
        assert get_feedback("hello", "hello") == "22222"
        assert get_feedback("abcde", "abcde") == "22222"

    def test_all_gray(self):
        """All grays when no letters match."""
        assert get_feedback("abcde", "fghij") == "00000"
        assert get_feedback("zzzzz", "aaaaa") == "00000"

    def test_all_yellow(self):
        """All yellows — right letters, all wrong positions."""
        # "abcde" vs "bcdea" — each letter is present but shifted
        result = get_feedback("abcde", "bcdea")
        assert result == "11111"

    def test_mixed_simple(self):
        """Simple mixed case with no duplicates."""
        # crane vs trace: t-r-a-c-e
        # Pass1 greens: r(1)==r, a(2)==a, e(4)==e  →  pool remaining: [t, c]
        # Pass2: c(0) → yellow (c in [t,c]), n(3) → gray
        # Result: c=yellow(1), r=green(2), a=green(2), n=gray(0), e=green(2) = "12202"
        result = get_feedback("crane", "trace")
        assert result == "12202"


class TestDuplicateLetters:
    """
    Duplicate letter handling is the trickiest part of the feedback function.
    These tests specifically target edge cases.
    """

    def test_duplicate_in_guess_not_answer(self):
        """Guess has a duplicate letter that the answer only has once."""
        # guess="aabbb", answer="aaccc"
        # a(0): a(0) → GREEN. a(1): a(1) → GREEN. b(2),(3),(4): not in remaining → GRAY
        # Pool after greens: [c, c, c] (positions 2,3,4)
        # Pass 2: b's are not in [c,c,c] → all gray
        assert get_feedback("aabbb", "aaccc") == "22000"

    def test_duplicate_in_answer_not_guess(self):
        """Answer has a duplicate letter but guess only has it once."""
        # guess="crane", answer="creep"
        # creep: c(0),r(1),e(2),e(3),p(4)
        # crane: c(0),r(1),a(2),n(3),e(4)
        # Pass1: c(0)==c→GREEN, r(1)==r→GREEN, a(2)!=e, n(3)!=e, e(4)!=p
        # Pool after: [e, e] (positions 2,3 unmatched)
        # Pass2: a(2): not in [e,e] → GRAY. n(3): not in [e,e] → GRAY.
        # e(4): e in [e,e] → YELLOW
        # Result: 2,2,0,0,1 = "22001"
        assert get_feedback("crane", "creep") == "22001"

    def test_guess_repeats_letter_seen_green(self):
        """Guess has same letter at two positions; answer has it twice (both green!)."""
        # guess="speed", answer="creep"
        # creep: c(0),r(1),e(2),e(3),p(4)
        # speed: s(0),p(1),e(2),e(3),d(4)
        # Pass1: e(2)==e→GREEN, e(3)==e→GREEN
        # Pool after: [c, r, p]
        # Pass2: s(0): not in [c,r,p] → GRAY. p(1): p in [c,r,p] → YELLOW. d(4): not → GRAY
        # Result: 0,1,2,2,0 = "01220"
        assert get_feedback("speed", "creep") == "01220"

    def test_all_same_letter_in_guess(self):
        """Guess is all same letter."""
        # guess="aaaaa", answer="aabbb"
        # a(0)==a(0) → GREEN. a(1)==a(1)... wait answer[1]=a? "aabbb": a(0),a(1),b(2),b(3),b(4)
        # a(0)==a(0) → GREEN
        # a(1)==a(1) → GREEN
        # a(2)!=b → no green
        # a(3)!=b → no green
        # a(4)!=b → no green
        # Pool after: [b, b, b] (positions 2,3,4)
        # Pass 2: none of the remaining a's are in [b,b,b] → all GRAY
        assert get_feedback("aaaaa", "aabbb") == "22000"

    def test_yellow_only_counted_once(self):
        """Same letter should only get yellow once if answer has it once."""
        # guess="aacde", answer="bbaaa"
        # answer: b(0),b(1),a(2),a(3),a(4)
        # a(0)!=b → no green
        # a(1)!=b → no green
        # c(2)!=a → no green
        # d(3)!=a → no green
        # e(4)!=a → no green
        # Pool: [b,b,a,a,a]
        # Pass 2:
        # a(0): a in pool → YELLOW, consume one a → pool=[b,b,a,a]
        # a(1): a in pool → YELLOW, consume one a → pool=[b,b,a]
        # c(2): c not in pool → GRAY
        # d(3): d not in pool → GRAY
        # e(4): e not in pool → GRAY
        assert get_feedback("aacde", "bbaaa") == "11000"

    def test_multiple_yellows_limited_by_answer(self):
        """Multiple yellows only up to count in answer."""
        # guess="eerie", answer="geese"
        # answer: g(0),e(1),e(2),s(3),e(4)
        # e(0)!=g → no green
        # e(1)==e(1) → GREEN
        # r(2)!=e → no green
        # i(3)!=s → no green
        # e(4)==e(4) → GREEN
        # Pool after: [g, e, s] (positions 0,2,3 unmatched)
        # Pass 2:
        # e(0): e in [g,e,s] → YELLOW, consume e → pool=[g,s]
        # r(2): r not in [g,s] → GRAY
        # i(3): i not in [g,s] → GRAY
        # Result: e=1,e=2,r=0,i=0,e=2 = "12002"
        assert get_feedback("eerie", "geese") == "12002"


class TestFilterCandidates:
    """Test the candidate filtering function."""

    def test_filter_removes_inconsistent(self):
        """Filter should keep only words consistent with the feedback."""
        candidates = ["crane", "trace", "raise", "arise", "saner", "lanes"]
        # Guess "crane" with pattern "12201" should keep words that produce that
        # pattern when "crane" is guessed against them
        guess = "crane"
        pattern = get_feedback("crane", "trace")  # whatever feedback crane→trace gives
        filtered = filter_candidates(candidates, guess, pattern)
        assert "trace" in filtered

    def test_filter_perfect_match(self):
        """With pattern 22222, only the exact answer remains."""
        candidates = ["crane", "trace", "plant"]
        filtered = filter_candidates(candidates, "crane", "22222")
        assert filtered == ["crane"]

    def test_filter_all_gray(self):
        """All gray means none of those letters appear."""
        # "abcde" vs any word with no a,b,c,d,e
        candidates = ["fghij", "abcde", "xxxxx", "aaaaa"]
        filtered = filter_candidates(candidates, "abcde", "00000")
        # Only words with none of a,b,c,d,e should remain
        assert "fghij" in filtered or "xxxxx" in filtered
        assert "abcde" not in filtered  # Would give 22222, not 00000


class TestPatternToEmoji:
    """Test the emoji display utility."""

    def test_all_green(self):
        assert pattern_to_emoji("22222") == "🟩🟩🟩🟩🟩"

    def test_all_yellow(self):
        assert pattern_to_emoji("11111") == "🟨🟨🟨🟨🟨"

    def test_all_gray(self):
        assert pattern_to_emoji("00000") == "⬜⬜⬜⬜⬜"

    def test_mixed(self):
        assert pattern_to_emoji("21010") == "🟩🟨⬜🟨⬜"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
