/**
 * test_feedback.cpp — Unit tests for the feedback engine.
 *
 * Uses a lightweight custom test framework (no external dependencies).
 * Tests all edge cases, especially duplicate-letter handling.
 *
 * Build & run:
 *   make test
 *   # or: g++ -std=c++17 -o test_feedback tests/test_feedback.cpp src/feedback.cpp && ./test_feedback
 */

#include "../src/feedback.h"
#include <iostream>
#include <string>
#include <vector>

// -----------------------------------------------------------------------
// Minimal test framework
// -----------------------------------------------------------------------
static int total = 0, passed = 0, failed_count = 0;

#define EXPECT_EQ(name, got, expected)                                          \
    do {                                                                        \
        total++;                                                                \
        if ((got) == (expected)) {                                              \
            passed++;                                                           \
            std::cout << "  PASS  " << (name) << "\n";                         \
        } else {                                                                \
            failed_count++;                                                     \
            std::cout << "  FAIL  " << (name) << "\n"                          \
                      << "        got:      \"" << (got) << "\"\n"              \
                      << "        expected: \"" << (expected) << "\"\n";        \
        }                                                                       \
    } while (0)

void section(const std::string& name) {
    std::cout << "\n[" << name << "]\n";
}

// -----------------------------------------------------------------------
// Tests
// -----------------------------------------------------------------------
void test_basic() {
    section("Basic Cases");

    // Perfect match — all green
    EXPECT_EQ("perfect match 'hello'", get_feedback("hello", "hello"), "22222");
    EXPECT_EQ("perfect match 'crane'", get_feedback("crane", "crane"), "22222");

    // All gray — no letters in common
    EXPECT_EQ("all gray 'abcde'→'fghij'", get_feedback("abcde", "fghij"), "00000");
    EXPECT_EQ("all gray 'zzzzz'→'aaaaa'", get_feedback("zzzzz", "aaaaa"), "00000");

    // All yellow — right letters, all wrong positions
    // abcde vs bcdea: each letter shifted by one position
    EXPECT_EQ("all yellow 'abcde'→'bcdea'", get_feedback("abcde", "bcdea"), "11111");
}

void test_mixed() {
    section("Mixed Green/Yellow/Gray");

    // crane vs trace: t(0)r(1)a(2)c(3)e(4)
    // c(0)!=t → pool check: c in [t,c] (pos 3 unmatched) → yellow
    // r(1)==r → green
    // a(2)==a → green
    // n(3)!=c → pool check: n not in [t] → gray
    // e(4)==e → green
    // Result: 1 2 2 0 2
    EXPECT_EQ("crane→trace", get_feedback("crane", "trace"), "12202");

    // speed vs creep: c(0)r(1)e(2)e(3)p(4)
    // s(0)!=c → gray
    // p(1)!=r → pool check: p in [c,r,p]? yes → yellow (pool[4] consumed)
    // e(2)==e → green
    // e(3)==e → green
    // d(4)!=p → pool=[c,r] → gray
    // Result: 0 1 2 2 0
    EXPECT_EQ("speed→creep", get_feedback("speed", "creep"), "01220");
}

void test_duplicate_in_guess() {
    section("Duplicate Letters in Guess");

    // guess has 'a' twice, answer has 'a' twice — both green
    // aabbb vs aaccc: a(0)==a→green, a(1)==a→green, b's not in pool [c,c,c] → gray
    EXPECT_EQ("aabbb→aaccc (aa both green)", get_feedback("aabbb", "aaccc"), "22000");

    // aaaaa vs aabbb: first two a's are green, rest gray (no more a's in pool)
    EXPECT_EQ("aaaaa→aabbb", get_feedback("aaaaa", "aabbb"), "22000");

    // speed vs speed: perfect
    EXPECT_EQ("speed→speed (perfect)", get_feedback("speed", "speed"), "22222");
}

void test_duplicate_in_answer() {
    section("Duplicate Letters in Answer");

    // crane vs creep: c(0)r(1)e(2)e(3)p(4)
    // c(0)==c→green, r(1)==r→green
    // a(2): pool=[e,e]→gray, n(3): pool=[e,e]→gray, e(4): e in pool→yellow
    EXPECT_EQ("crane→creep", get_feedback("crane", "creep"), "22001");

    // eerie vs geese: g(0)e(1)e(2)s(3)e(4)
    // e(0)!=g → pass2: e in [g,e,s]→yellow (consume pos1 e)
    // e(1)==e→green (consume)
    // r(2)!=e → r not in remaining [g,s]→gray
    // i(3)!=s → i not in [g,s]→gray
    // e(4)==e→green
    EXPECT_EQ("eerie→geese", get_feedback("eerie", "geese"), "12002");
}

void test_yellow_cap() {
    section("Yellow Count Capped by Answer Occurrences");

    // aacde vs bbaaa: b(0)b(1)a(2)a(3)a(4)
    // a(0): pool=[b,b,a,a,a]→yellow (consume one a)
    // a(1): pool=[b,b,a,a]→yellow (consume one a)
    // c(2): c not in pool→gray
    // d(3): d not in pool→gray
    // e(4): e not in pool→gray
    EXPECT_EQ("aacde→bbaaa (yellows capped)", get_feedback("aacde", "bbaaa"), "11000");

    // guess all same, answer has one: aaaaa vs bbbba
    // a(0)!=b, a(1)!=b, a(2)!=b, a(3)!=b, a(4)==a→green
    // Pool after pass1: [b,b,b,b]
    // Pass2: none of a(0-3) in [b,b,b,b]→all gray
    EXPECT_EQ("aaaaa→bbbba", get_feedback("aaaaa", "bbbba"), "00002");
}

void test_filter() {
    section("Filter Candidates");

    std::vector<std::string> candidates = {"crane", "trace", "plant", "chess"};

    // After guessing "crane" and getting all-green pattern, only "crane" remains
    auto r1 = filter_candidates(candidates, "crane", "22222");
    EXPECT_EQ("filter perfect match", r1.size() == 1 && r1[0] == "crane", true);

    // After getting all-gray, crane should be removed
    auto r2 = filter_candidates(candidates, "crane", "00000");
    bool no_crane = true;
    for (const auto& w : r2) if (w == "crane") no_crane = false;
    EXPECT_EQ("filter removes crane on 00000", no_crane, true);
}

// -----------------------------------------------------------------------
// Main
// -----------------------------------------------------------------------
int main() {
    std::cout << "=========================================\n";
    std::cout << "  Wordle Solver — Feedback Engine Tests\n";
    std::cout << "=========================================\n";

    test_basic();
    test_mixed();
    test_duplicate_in_guess();
    test_duplicate_in_answer();
    test_yellow_cap();
    test_filter();

    std::cout << "\n=========================================\n";
    std::cout << "  Results: " << passed << "/" << total << " passed";
    if (failed_count == 0) {
        std::cout << "  ALL TESTS PASSED ✓\n";
    } else {
        std::cout << "  " << failed_count << " FAILED\n";
    }
    std::cout << "=========================================\n";

    return (failed_count == 0) ? 0 : 1;
}
