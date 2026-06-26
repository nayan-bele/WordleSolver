/**
 * feedback.cpp — Core Wordle feedback engine implementation.
 *
 * The two-pass algorithm for correct duplicate-letter handling:
 *   Pass 1: Mark exact position matches (Green/2). Remove from pool.
 *   Pass 2: For remaining, check if letter exists in pool (Yellow/1). Consume it.
 *
 * Example: guess="speed", answer="creep"
 *   Pass1: e[2]==e → green, e[3]==e → green. Pool: [c, r, _, _, p]
 *   Pass2: s→gray, p→yellow(consume p), d→gray
 *   Result: "01220"
 */

#include "feedback.h"
#include <fstream>
#include <stdexcept>
#include <algorithm>

std::string get_feedback(const std::string& guess, const std::string& answer) {
    std::string result(5, '0');

    // Pool tracks which answer letters are still "available" (not yet matched)
    std::array<char, 5> pool;
    for (int i = 0; i < 5; i++) pool[i] = answer[i];

    // --- Pass 1: Mark greens and consume from pool ---
    for (int i = 0; i < 5; i++) {
        if (guess[i] == answer[i]) {
            result[i] = '2';
            pool[i] = '\0';  // Consumed — no longer available for yellows
        }
    }

    // --- Pass 2: Mark yellows for remaining positions ---
    for (int i = 0; i < 5; i++) {
        if (result[i] == '2') continue;  // Already matched green

        // Search pool for this letter
        for (int j = 0; j < 5; j++) {
            if (pool[j] != '\0' && pool[j] == guess[i]) {
                result[i] = '1';
                pool[j] = '\0';  // Consume so duplicates aren't double-counted
                break;
            }
        }
    }

    return result;
}

std::vector<std::string> filter_candidates(
    const std::vector<std::string>& candidates,
    const std::string& guess,
    const std::string& pattern)
{
    std::vector<std::string> result;
    result.reserve(candidates.size());

    for (const auto& word : candidates) {
        if (get_feedback(guess, word) == pattern) {
            result.push_back(word);
        }
    }
    return result;
}

std::vector<std::string> load_words(const std::string& filepath) {
    std::vector<std::string> words;
    std::ifstream file(filepath);
    if (!file.is_open()) {
        throw std::runtime_error("Cannot open file: " + filepath);
    }

    std::string line;
    while (std::getline(file, line)) {
        // Trim whitespace and skip empty/invalid lines
        while (!line.empty() && (line.back() == '\r' || line.back() == '\n' || line.back() == ' '))
            line.pop_back();
        if (line.size() == 5) {
            // Lowercase the word
            std::transform(line.begin(), line.end(), line.begin(), ::tolower);
            words.push_back(line);
        }
    }
    return words;
}

std::string pattern_to_emoji(const std::string& pattern) {
    std::string result;
    result.reserve(pattern.size() * 4);  // Each emoji is ~4 bytes in UTF-8
    for (char c : pattern) {
        if      (c == '2') result += "\U0001F7E9";  // 🟩
        else if (c == '1') result += "\U0001F7E8";  // 🟨
        else               result += "\u2B1C";      // ⬜
    }
    return result;
}
