#  Wordle Solver 

> **An information-theoretic Wordle solver that picks the optimal guess at every step by maximizing expected information gain (Shannon entropy). Built in C++17 — runs the full 2,315-word benchmark in under 2 seconds.**

---

##  Benchmark Results

| Solver | Avg Guesses | Max | Solved ≤ 6 | Failed | Runtime |
|--------|-------------|-----|------------|--------|---------|
| **V2 — Entropy Optimal** | **3.5538** | 7 | **99.48% (2303/2315)** | 12 | ~1.4s |
| V1 — Brute Force Baseline | 3.9421 | 7 | 98.10% (2271/2315) | 44 | ~0.2s |

> Benchmarked across all **2,315** possible Wordle answers.
>
> **V2 Guess distribution:**
> - 2 guesses: 141 words
> - 3 guesses: 1028 words *(most common)*
> - 4 guesses: 925 words
> - 5 guesses: 172 words
> - 6 guesses: 36 words
> - Failed: 12 words

---

##  How It Works

Wordle gives per-letter feedback:
- 🟩 **Green** — correct letter, correct position
- 🟨 **Yellow** — correct letter, wrong position
- ⬜ **Gray** — letter not in word

For any guess there are **3⁵ = 243** possible feedback patterns. The key insight:

**The best guess is the one that most evenly splits the remaining candidates across those 243 buckets.**

### Shannon Entropy Formula

For guess $g$ against candidate pool $C$:

$$H(g) = -\sum_{k} p_k \cdot \log_2(p_k), \quad p_k = \frac{|\text{bucket}_k|}{|C|}$$

At each step we pick $\arg\max_g\ H(g)$ — the guess that maximizes expected information gain.

---

## 🗂️ Project Structure

```
wordle-solver/
├── data/
│   ├── answers.txt          # 2315 official Wordle answers
│   └── guesses.txt          # 14854 allowed guesses
├── src/
│   ├── feedback.h / .cpp    
│   ├── solver.h  / .cpp     # V1 (brute-force) + V2 (entropy)
│   ├── benchmark.cpp        
│   └── cli.cpp              
├── tests/
│   └── test_feedback.cpp    
├── results/
│   └── benchmark_results.csv
├── CMakeLists.txt
├── Makefile
└── README.md
```

---

##  Quick Start

```bash
git clone https://github.com/nayan-bele/WordleSolver.git
cd WordleSolver
make
```

That's it — builds everything in ~2 seconds. Then run:

```bash
./benchmark       # Full benchmark: V1 vs V2 on all 2315 words
./wordle_cli      # Play Wordle with solver assistance
make test         # Run all 16 unit tests
```

### Use as a Real Wordle Assistant

```bash
./wordle_cli
```

---

##  Interactive CLI Demo

```
  ====================================================
      WORDLE SOLVER  --  Entropy Edition             
      Powered by Shannon Information Theory          
  ====================================================

  -- Turn 1 ----------------------------------------
  Remaining candidates: 2315
  Suggested guess: crane  (precomputed best opener)

  Enter feedback (or 'list'/'quit'): 00120

  -- Turn 2 ----------------------------------------
  Remaining candidates: 47
  Suggested guess: lints  (H = 4.891 bits)

  Enter feedback: 02010

  -- Turn 3 ----------------------------------------
  Remaining candidates: 3
  Possible answers: shirt, birth, third
  Suggested guess: shirt  (H = 1.585 bits)

  Enter feedback: 22222

  -----------------------------------
    Solved in 3 guesses!             
  -----------------------------------
```

---

##  Duplicate Letters

The feedback function uses a **two-pass algorithm** to match Wordle's exact rules:

**Pass 1** — Mark all exact position matches as 🟩 Green. Consume from pool.  
**Pass 2** — For remaining positions, check if the letter is in the pool → 🟨 Yellow (consume). Otherwise → ⬜ Gray.

**Example:** `guess="SPEED"`, `answer="CREEP"`

| Pos | Guess | Answer | Result | Reason |
|-----|-------|--------|--------|--------|
| 0 | S | C | ⬜ | S not in answer |
| 1 | P | R | 🟨 | P in answer (pos 4), yellow |
| 2 | E | E | 🟩 | Exact match |
| 3 | E | E | 🟩 | Exact match |
| 4 | D | P | ⬜ | D not in answer |

Result: `01220` → `⬜🟨🟩🟩⬜`

---

##  Unit Tests

```bash
make test
```

```
=========================================
  Wordle Solver — Feedback Engine Tests
=========================================

[Basic Cases]
  PASS  perfect match 'hello'
  PASS  all gray 'abcde'→'fghij'
  PASS  all yellow 'abcde'→'bcdea'

[Duplicate Letters in Guess]
  PASS  aabbb→aaccc (aa both green)
  PASS  aaaaa→bbbba

[Duplicate Letters in Answer]
  PASS  crane→creep
  PASS  eerie→geese
  ...

=========================================
  Results: 16/16 passed  ALL TESTS PASSED ✓
=========================================
```

---

