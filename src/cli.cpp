/**
 * cli.cpp — Interactive Wordle Solver Assistant.
 *
 * Use this while playing the real Wordle at nytimes.com/games/wordle.
 *
 * Usage:
 *   ./wordle_cli
 *
 * The solver suggests the best word each turn. You type that word into
 * Wordle, then enter the feedback here as a 5-digit string:
 *   2 = Green  🟩 (correct letter + position)
 *   1 = Yellow 🟨 (correct letter, wrong position)
 *   0 = Gray   ⬜ (letter not in word)
 *
 * Example session:
 *   Suggested: CRANE
 *   Enter feedback: 00120
 *   Suggested: SLOTH
 *   Enter feedback: 22222
 *   ✅ Solved in 2 guesses!
 */

#include "feedback.h"
#include "solver.h"
#include <iostream>
#include <iomanip>
#include <string>
#include <vector>
#include <algorithm>
#include <limits>

// -----------------------------------------------------------------------
// Terminal helpers
// -----------------------------------------------------------------------
void clear_screen() {
    std::cout << "\033[2J\033[H";  // ANSI clear screen
}

void print_banner() {
    std::cout << "\n";
    std::cout << "  +====================================================+\n";
    std::cout << "  |     WORDLE SOLVER  --  Entropy Edition             |\n";
    std::cout << "  |     Powered by Shannon Information Theory          |\n";
    std::cout << "  +====================================================+\n\n";
}

void print_help() {
    std::cout << "  Feedback guide:\n";
    std::cout << "    2 -> Green  (correct letter, correct position)\n";
    std::cout << "    1 -> Yellow (correct letter, wrong position)\n";
    std::cout << "    0 -> Gray   (letter not in word)\n\n";
    std::cout << "  Enter feedback as 5 digits e.g.: 22010\n";
    std::cout << "  Commands: 'list' to show candidates | 'quit' to exit\n\n";
}

bool validate_feedback(const std::string& s) {
    if (s.size() != 5) return false;
    for (char c : s) if (c != '0' && c != '1' && c != '2') return false;
    return true;
}

// -----------------------------------------------------------------------
// Interactive game loop
// -----------------------------------------------------------------------
void run_cli(const std::vector<std::string>& answers) {
    print_banner();
    print_help();

    bool play_again = true;

    while (play_again) {
        std::vector<std::string> candidates = answers;
        bool solved = false;

        for (int attempt = 1; attempt <= 6 && !solved; attempt++) {
            std::cout << "\n  -- Turn " << attempt << " "
                      << std::string(40, '-') << "\n";
            std::cout << "  Remaining candidates: " << candidates.size() << "\n";

            // Show possible answers if small enough
            if (candidates.size() <= 10) {
                std::cout << "  Possible answers: ";
                for (size_t i = 0; i < candidates.size(); i++) {
                    if (i > 0) std::cout << ", ";
                    std::cout << candidates[i];
                }
                std::cout << "\n";
            }

            // --- Pick guess ---
            std::string guess;
            double entropy_bits = 0.0;

            if (attempt == 1) {
                guess = BEST_FIRST_GUESS;
                std::cout << "\n  Suggested guess: " << guess
                          << "  (precomputed best opener)\n";
            } else if (candidates.size() == 1) {
                guess = candidates[0];
                std::cout << "\n  Only one candidate left!\n";
                std::cout << "  Suggested guess: " << guess << "\n";
            } else {
                auto [g, h] = best_guess(candidates);
                guess       = g;
                entropy_bits = h;
                std::cout << "\n  Suggested guess: " << guess
                          << "  (H = " << std::fixed << std::setprecision(3)
                          << entropy_bits << " bits)\n";
            }

            // --- Get feedback from user ---
            std::string feedback;
            while (true) {
                std::cout << "\n  Enter feedback (or 'list'/'quit'): ";
                std::cin >> feedback;

                if (!std::cin.good()) {
                    std::cout << "\n\nExiting solver. Good luck!\n";
                    return;
                }

                // Convert to lowercase for robustness
                std::transform(feedback.begin(), feedback.end(),
                               feedback.begin(), ::tolower);

                if (feedback == "quit") {
                    std::cout << "\nExiting. Good luck!\n";
                    return;
                }

                if (feedback == "list") {
                    std::cout << "\n  Candidates (" << candidates.size() << "):\n  ";
                    for (size_t i = 0; i < candidates.size(); i++) {
                        std::cout << candidates[i];
                        if (i + 1 < candidates.size()) std::cout << "  ";
                        if ((i + 1) % 8 == 0) std::cout << "\n  ";
                    }
                    std::cout << "\n";
                    continue;
                }

                if (validate_feedback(feedback)) break;
                std::cout << "  Invalid feedback -- enter exactly 5 digits using only 0, 1, 2\n";
            }

            // Display what was entered
            std::cout << "  " << guess << " -> " << pattern_to_emoji(feedback) << "\n";

            // --- Check solved ---
            if (feedback == "22222") {
                std::cout << "\n  +-----------------------------------+\n";
                std::cout << "  |  Solved in " << attempt << " guess"
                          << (attempt > 1 ? "es" : "") << "!              |\n";
                std::cout << "  +-----------------------------------+\n";
                solved = true;
                break;
            }

            // --- Filter candidates ---
            candidates = filter_candidates(candidates, guess, feedback);

            if (candidates.empty()) {
                std::cout << "\n  No valid candidates remain!\n";
                std::cout << "  The answer may not be in our word list,\n";
                std::cout << "  or you entered feedback incorrectly.\n";
                break;
            }
        }

        if (!solved) {
            std::cout << "\n  Could not solve within 6 guesses.\n";
            if (!candidates.empty()) {
                std::cout << "  Remaining candidates: ";
                for (size_t i = 0; i < std::min(candidates.size(), size_t(10)); i++) {
                    std::cout << candidates[i] << " ";
                }
                std::cout << "\n";
            }
        }

        // Play again?
        std::string again;
        std::cout << "\n  Play again? (y/n): ";
        std::cin >> again;
        play_again = (again == "y" || again == "Y");

        if (play_again) std::cout << "\n";
    }

    std::cout << "\nThanks for using Wordle Solver!\n\n";
}

// -----------------------------------------------------------------------
// Main
// -----------------------------------------------------------------------
int main() {
    std::string answers_path = "data/answers.txt";

    std::vector<std::string> answers;
    try {
        answers = load_words(answers_path);
    } catch (const std::exception& e) {
        std::cerr << "Error loading word list: " << e.what() << "\n";
        std::cerr << "Run from the project root: ./wordle_cli\n";
        return 1;
    }

    std::cout << "Loaded " << answers.size() << " answer words.\n";
    run_cli(answers);
    return 0;
}
