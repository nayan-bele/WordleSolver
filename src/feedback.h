/**
 * feedback.h — Core Wordle feedback engine declarations.
 *
 * Feedback encoding:
 *   '2' = Green  (correct letter, correct position)
 *   '1' = Yellow (correct letter, wrong position)
 *   '0' = Gray   (letter not in word / already accounted for)
 */

#pragma once
#include <string>
#include <vector>
#include <array>

/**
 * Compute Wordle feedback for a guess against a known answer.
 * Uses the two-pass algorithm to correctly handle duplicate letters.
 *
 * @param guess  5-letter guess word (lowercase)
 * @param answer 5-letter answer word (lowercase)
 * @return       5-char pattern of '0', '1', '2'
 */
std::string get_feedback(const std::string& guess, const std::string& answer);

/**
 * Filter a candidate list to words that would produce the given
 * feedback pattern if 'guess' were played against them.
 *
 * @param candidates Current possible answer words
 * @param guess      The word that was guessed
 * @param pattern    The feedback received (e.g. "22010")
 * @return           Filtered candidate list
 */
std::vector<std::string> filter_candidates(
    const std::vector<std::string>& candidates,
    const std::string& guess,
    const std::string& pattern
);

/**
 * Load a word list from a plain text file (one word per line).
 *
 * @param filepath Path to the word list file
 * @return         Vector of lowercase words
 */
std::vector<std::string> load_words(const std::string& filepath);

/**
 * Convert a '210' pattern string to emoji for display.
 * '2' → 🟩  '1' → 🟨  '0' → ⬜
 */
std::string pattern_to_emoji(const std::string& pattern);
