/**
 * solver.h — Wordle solver declarations (V1 brute-force + V2 entropy-optimal).
 */

#pragma once
#include <string>
#include <vector>
#include <utility>  // std::pair

/// Precomputed best opening guess (highest entropy against the full answer set)
extern const std::string BEST_FIRST_GUESS;

/**
 * Compute Shannon entropy of a guess against the current candidate set.
 *
 * For each possible feedback pattern p, let prob(p) = |bucket_p| / |candidates|.
 * H(guess) = -Σ prob(p) * log2(prob(p))
 *
 * Higher entropy → guess splits candidates more evenly → more info gained.
 *
 * @param guess      Word to evaluate
 * @param candidates Current possible answers
 * @return           Entropy in bits
 */
double compute_entropy(const std::string& guess,
                       const std::vector<std::string>& candidates);

/**
 * Find the candidate that maximizes expected entropy.
 * Searches only 'candidates' (not the full 14k guess list) for speed.
 *
 * @param candidates Current possible answers
 * @return           {best_word, entropy_bits}
 */
std::pair<std::string, double> best_guess(const std::vector<std::string>& candidates);

/**
 * V1: Brute-force solver — always picks the first remaining candidate.
 *
 * @param hidden_word  The word to guess
 * @param all_answers  Full answer word list
 * @param verbose      Print each attempt if true
 * @return             Number of guesses (7 = failed in 6)
 */
int solve_v1(const std::string& hidden_word,
             const std::vector<std::string>& all_answers,
             bool verbose = false);

/**
 * V2: Entropy-optimal solver — picks the information-maximizing guess.
 *
 * @param hidden_word  The word to guess
 * @param all_answers  Full answer word list
 * @param verbose      Print each attempt + entropy score if true
 * @return             Number of guesses (7 = failed in 6)
 */
int solve_v2(const std::string& hidden_word,
             const std::vector<std::string>& all_answers,
             bool verbose = false);
