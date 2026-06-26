#!/bin/bash
# setup_github.sh — Initialize git repo and prepare for GitHub push
# Run this ONCE after you've created your GitHub repository.
# 
# Usage:
#   chmod +x setup_github.sh
#   ./setup_github.sh YOUR_GITHUB_USERNAME

set -e

USERNAME=${1:-"YOUR_GITHUB_USERNAME"}
REPO_NAME="wordle-solver"

echo "🟩 Wordle Solver — GitHub Setup"
echo "================================"
echo "GitHub username: $USERNAME"
echo "Repository name: $REPO_NAME"
echo ""

# Initialize git if not already done
if [ ! -d ".git" ]; then
    echo "Initializing git repository..."
    git init
    echo "✅ Git initialized"
else
    echo "✅ Git already initialized"
fi

# Set up .gitignore
echo ""
echo "Staging files..."
git add .
git status

echo ""
echo "Creating initial commit..."
git commit -m "feat: initial Wordle solver implementation

- feedback.py: Core feedback engine with correct duplicate-letter handling
- solver_v1.py: Brute-force filter solver (baseline)
- solver_v2.py: Shannon entropy-based optimal solver
- benchmark.py: Full benchmark against all 2314 answer words
- cli.py: Interactive Wordle assistant CLI
- tests/: 17 unit tests covering all edge cases"

echo ""
echo "Setting up main branch..."
git branch -M main

echo ""
echo "📌 Next steps:"
echo "  1. Create a new repo on GitHub: https://github.com/new"
echo "     Name: $REPO_NAME"
echo "     Description: 'Wordle solver using Shannon entropy for optimal guess selection'"
echo "     Visibility: Public"
echo "     Do NOT initialize with README (we already have one)"
echo ""
echo "  2. Then run:"
echo "     git remote add origin https://github.com/$USERNAME/$REPO_NAME.git"
echo "     git push -u origin main"
echo ""
echo "  3. After pushing, add GitHub topics:"
echo "     python, wordle, information-theory, shannon-entropy, word-game, nlp"
echo ""
echo "✅ Local git setup complete!"
