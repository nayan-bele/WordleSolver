#!/bin/bash
# setup_github.sh — Initialize git and push to GitHub as nayan-bele
# Run this ONCE after creating the repo on GitHub.
#
# Usage: ./setup_github.sh

set -e

USERNAME="nayan-bele"
REPO_NAME="wordle-solver"
REMOTE="https://github.com/$USERNAME/$REPO_NAME.git"

echo "🟩 Wordle Solver — GitHub Setup for @$USERNAME"
echo "================================================"

# Init git if not already done
if [ ! -d ".git" ]; then
    git init
    echo "✅ Git initialized"
fi

# Stage all files
git add .
git status --short

echo ""
echo "Creating initial commit..."
git commit -m "feat: Wordle solver with Shannon entropy (C++17)

Core:
- feedback.cpp: Two-pass duplicate-letter algorithm
- solver.cpp: V1 brute-force + V2 entropy-optimal solvers
- benchmark.cpp: Full benchmark against 2315 answers
- cli.cpp: Interactive Wordle assistant

Results (C++, ~1.6s total):
- V2 avg: 3.5538 guesses, 99.48% within 6
- V1 avg: 3.9421 guesses, 98.10% within 6

Tests: 16/16 unit tests passing"

git branch -M main
git remote remove origin 2>/dev/null || true
git remote add origin "$REMOTE"

echo ""
echo "📌 Steps to finish:"
echo ""
echo "  1. Create the repo on GitHub (if not done yet):"
echo "     https://github.com/new"
echo "     Name:        $REPO_NAME"
echo "     Description: Wordle solver using Shannon entropy (C++17) — 3.55 avg guesses"
echo "     Visibility:  Public"
echo "     ⚠️  Do NOT initialize with README/gitignore — we already have them"
echo ""
echo "  2. Push:"
echo "     git push -u origin main"
echo ""
echo "  3. Add GitHub topics after pushing:"
echo "     cpp  cplusplus  wordle  information-theory  shannon-entropy  algorithm"
echo ""
echo "✅ Local git setup done! Now run: git push -u origin main"
