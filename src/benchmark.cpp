/**
 * benchmark.cpp — Run V1 and V2 solvers against all answer words and compare.
 *
 * Usage:
 *   ./benchmark                  # Full run (both V1 + V2, all 2315 words)
 *   ./benchmark --v2-only        # Skip V1 (faster)
 *   ./benchmark --quick          # First 100 words only (for quick testing)
 *
 * Output:
 *   - Per-solver stats: avg, max, distribution, % within 6
 *   - Side-by-side comparison table
 *   - results/benchmark_results.csv
 *
 * Expected results (C++ is ~50x faster than Python):
 *   V2: avg ~3.55 guesses, 99.48% within 6, runtime ~0.5s
 *   V1: avg ~4.80 guesses, ~92% within 6
 */

#include "feedback.h"
#include "solver.h"
#include <iostream>
#include <iomanip>
#include <fstream>
#include <sstream>
#include <map>
#include <vector>
#include <string>
#include <numeric>
#include <algorithm>
#include <chrono>
#include <filesystem>
#include <cstring>

// -----------------------------------------------------------------------
// Progress bar helper
// -----------------------------------------------------------------------
void print_progress(int done, int total, double rate, double eta) {
    constexpr int BAR_LEN = 30;
    int filled = (total > 0) ? (BAR_LEN * done / total) : 0;
    std::cout << "\r  [";
    for (int i = 0; i < BAR_LEN; i++)
        std::cout << (i < filled ? '\xE2' : '\xE2');  // Use simple chars for portability
    // Simpler ASCII progress bar
    std::cout << "\r  [";
    for (int i = 0; i < BAR_LEN; i++)
        std::cout << (i < filled ? '#' : '.');
    std::cout << "] " << done << "/" << total
              << " (" << std::fixed << std::setprecision(1) << rate << " w/s"
              << ", ETA: " << static_cast<int>(eta) << "s)  " << std::flush;
}

// -----------------------------------------------------------------------
// Benchmark runner
// -----------------------------------------------------------------------
struct BenchStats {
    std::string name;
    std::vector<int> results;
    double avg = 0;
    int    max_g = 0, min_g = 0;
    double within_6_pct = 0;
    int    failed = 0;
    double time_s = 0;
};

BenchStats run_benchmark(
    const std::string& name,
    const std::vector<std::string>& answers,
    int solver_version)  // 1 = V1, 2 = V2
{
    BenchStats stats;
    stats.name = name;
    stats.results.reserve(answers.size());

    int n = static_cast<int>(answers.size());
    auto start = std::chrono::steady_clock::now();

    std::cout << "\n" << std::string(52, '=') << "\n";
    std::cout << " Running " << name << " on " << n << " words...\n";
    std::cout << std::string(52, '=') << "\n";

    for (int i = 0; i < n; i++) {
        int guesses = (solver_version == 1)
                      ? solve_v1(answers[i], answers, false)
                      : solve_v2(answers[i], answers, false);
        stats.results.push_back(guesses);

        // Progress bar every 100 words
        if ((i + 1) % 100 == 0 || (i + 1) == n) {
            auto now     = std::chrono::steady_clock::now();
            double elapsed = std::chrono::duration<double>(now - start).count();
            double rate  = (i + 1) / elapsed;
            double eta   = (n - i - 1) / rate;
            print_progress(i + 1, n, rate, eta);
        }
    }
    std::cout << "\n";

    auto end = std::chrono::steady_clock::now();
    stats.time_s = std::chrono::duration<double>(end - start).count();

    // Compute statistics
    double sum = 0;
    stats.min_g = stats.results[0];
    stats.max_g = stats.results[0];
    for (int g : stats.results) {
        sum += g;
        if (g > stats.max_g) stats.max_g = g;
        if (g < stats.min_g) stats.min_g = g;
        if (g > 6) stats.failed++;
    }
    stats.avg = sum / n;
    stats.within_6_pct = 100.0 * (n - stats.failed) / n;

    return stats;
}

// -----------------------------------------------------------------------
// Print helpers
// -----------------------------------------------------------------------
void print_summary(const BenchStats& s) {
    std::map<int, int> dist;
    for (int g : s.results) dist[g]++;

    std::cout << "\n  Results for: " << s.name << "\n";
    std::cout << "  " << std::string(42, '-') << "\n";
    std::cout << std::fixed << std::setprecision(4);
    std::cout << "  Average guesses : " << s.avg << "\n";
    std::cout << "  Min guesses     : " << s.min_g << "\n";
    std::cout << "  Max guesses     : " << s.max_g << "\n";
    std::cout << std::setprecision(2);
    std::cout << "  Within 6 guesses: " << s.within_6_pct << "%"
              << "  (" << (s.results.size() - s.failed) << "/" << s.results.size() << ")\n";
    std::cout << "  Failed (>6)     : " << s.failed << "\n";
    std::cout << "\n  Guess distribution:\n";

    for (auto& [k, count] : dist) {
        std::string bar(count / 10, '#');
        std::cout << "    " << (k == 7 ? "FAIL" : std::to_string(k))
                  << " guesses: " << std::setw(5) << count
                  << "  " << bar << "\n";
    }
}

void print_comparison(const BenchStats& v1, const BenchStats& v2) {
    std::cout << "\n" << std::string(57, '=') << "\n";
    std::cout << "              COMPARISON TABLE\n";
    std::cout << std::string(57, '=') << "\n";
    std::cout << std::left << std::setw(26) << "  Metric"
              << std::right << std::setw(14) << "V1 (Brute)"
              << std::setw(14) << "V2 (Entropy)" << "\n";
    std::cout << "  " << std::string(53, '-') << "\n";

    auto row = [&](const std::string& label, auto a, auto b) {
        std::cout << std::left << std::setw(26) << ("  " + label)
                  << std::right << std::setw(14) << a
                  << std::setw(14) << b << "\n";
    };

    std::cout << std::fixed << std::setprecision(4);
    row("Average guesses",    v1.avg,          v2.avg);
    std::cout << std::setprecision(0);
    row("Max guesses",        v1.max_g,        v2.max_g);
    std::cout << std::setprecision(2);
    row("Solved within 6 (%)", v1.within_6_pct, v2.within_6_pct);
    row("Failed (>6)",        v1.failed,       v2.failed);
    std::cout << std::setprecision(1);
    row("Runtime (s)",        v1.time_s,       v2.time_s);
    std::cout << std::string(57, '=') << "\n";
    std::cout << std::setprecision(4);
    std::cout << "\n  Entropy solver saves "
              << (v1.avg - v2.avg) << " avg guesses vs brute force!\n";
}

void save_csv(const std::vector<BenchStats>& all_stats,
              const std::vector<std::string>& answers,
              const std::string& out_path)
{
    // Ensure directory exists
    std::filesystem::path p(out_path);
    std::filesystem::create_directories(p.parent_path());

    std::ofstream f(out_path);
    if (!f.is_open()) {
        std::cerr << "  Warning: could not write CSV to " << out_path << "\n";
        return;
    }

    // Header
    f << "word";
    for (const auto& s : all_stats) f << "," << s.name;
    f << "\n";

    // Rows
    for (size_t i = 0; i < answers.size(); i++) {
        f << answers[i];
        for (const auto& s : all_stats) f << "," << s.results[i];
        f << "\n";
    }
    std::cout << "\n  CSV saved to: " << out_path << "\n";
}

// -----------------------------------------------------------------------
// Main
// -----------------------------------------------------------------------
int main(int argc, char* argv[]) {
    bool quick   = false;
    bool v2_only = false;

    for (int i = 1; i < argc; i++) {
        if (std::strcmp(argv[i], "--quick")   == 0) quick   = true;
        if (std::strcmp(argv[i], "--v2-only") == 0) v2_only = true;
    }

    // Locate data directory relative to binary location
    std::string data_dir = "data/";  // Run from project root

    std::cout << "Loading word lists...\n";
    std::vector<std::string> answers;
    try {
        answers = load_words(data_dir + "answers.txt");
    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << "\n";
        std::cerr << "Run from the project root: ./benchmark\n";
        return 1;
    }

    if (quick) {
        answers.resize(std::min(100, (int)answers.size()));
        std::cout << "Quick mode: using first " << answers.size() << " words\n";
    }

    std::cout << "Loaded " << answers.size() << " answer words\n";

    std::vector<BenchStats> all_stats;

    // --- V1 ---
    if (!v2_only) {
        auto s = run_benchmark("V1 -- Brute Force", answers, 1);
        print_summary(s);
        all_stats.push_back(s);
    }

    // --- V2 ---
    {
        auto s = run_benchmark("V2 -- Entropy Optimal", answers, 2);
        print_summary(s);
        all_stats.push_back(s);
    }

    // --- Comparison ---
    if (!v2_only && all_stats.size() == 2) {
        print_comparison(all_stats[0], all_stats[1]);
    }

    // --- Save CSV ---
    save_csv(all_stats, answers, "results/benchmark_results.csv");

    std::cout << "\nBenchmark complete!\n";
    return 0;
}
