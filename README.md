<p align="center">
  <h1 align="center">commitgen</h1>
</p>

<p align="center">
  <strong>AI-powered commit messages. Stage your changes, run commitgen, done.</strong>
</p>

<p align="center">
  <a href="https://github.com/Pavankumardhruv/commitgen/blob/main/LICENSE"><img src="https://img.shields.io/github/license/Pavankumardhruv/commitgen?style=flat-square" alt="License"></a>
  <img src="https://img.shields.io/badge/python-3.10%2B-blue?style=flat-square&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/LLM-Claude%20%7C%20Ollama-orange?style=flat-square" alt="LLM">
</p>

---

commitgen analyzes your staged `git diff` and generates a clear, conventional commit message - then lets you accept, edit, or cancel.

Works with **Claude API** (default) for high-quality output, or **Ollama** for fully offline, local generation.

## Demo

```bash
$ git add src/auth.py src/middleware.py
$ commitgen

Analyzing 2 staged file(s)...

  • src/auth.py
  • src/middleware.py

╭─ Suggested commit message ─────────────────────────────╮
│                                                         │
│  Add JWT auth middleware with refresh token rotation     │
│                                                         │
│  Extract token validation into middleware so all         │
│  protected routes share the same auth logic. Refresh     │
│  tokens rotate on each use to limit replay window.      │
│                                                         │
╰─────────────────────────────────────────────────────────╯

Actions:
  y - commit with this message
  e - edit in $EDITOR then commit
  n - cancel

→ y

Committed.
```

## Install

```bash
pip install git+https://github.com/Pavankumardhruv/commitgen.git
```

Or clone and install locally:

```bash
git clone https://github.com/Pavankumardhruv/commitgen.git
cd commitgen
pip install -e .
```

## Usage

```bash
# Stage your changes, then:
commitgen              # Generate and choose interactively
commitgen -c           # Generate and commit immediately (no prompt)
commitgen --local      # Use Ollama instead of Claude API

# Git hook (auto-generate on every commit)
commitgen hook         # Install prepare-commit-msg hook
commitgen unhook       # Remove it
```

## How It Works

```
  git diff --cached
        │
        ▼
  ┌──────────────┐
  │ Diff Parser   │  Extract files, stats, and raw diff
  └──────┬───────┘
         │
  ┌──────▼───────┐
  │ Prompt Engine │  Build context-aware prompt with commit conventions
  └──────┬───────┘
         │
  ┌──────▼───────┐
  │ LLM Backend  │  Claude API (default) or Ollama (--local)
  └──────┬───────┘
         │
         ▼
  Commit message → accept / edit / cancel
```

**What makes the messages good:**

- Imperative mood ("Add", "Fix", "Update" - not "Added", "Fixes")
- Subject line under 72 characters
- Body explains **why**, not what (the diff already shows what)
- Skips trivial details (formatting, line numbers)
- Conventional prefixes when appropriate

## Configuration

### Claude API (default)

```bash
export ANTHROPIC_API_KEY=your-key-here
```

### Ollama (fully offline)

```bash
brew install ollama
ollama pull qwen2.5:3b
commitgen --local
```

## Architecture

```
commitgen/
├── cli.py        # Entry point, interactive flow
├── diff.py       # Git diff extraction and truncation
├── prompt.py     # System prompt and user prompt templates
├── generate.py   # Claude and Ollama LLM backends
└── hook.py       # Git hook installer/uninstaller
```

## Why not just write commit messages manually?

You should understand your changes - commitgen doesn't replace that. It replaces the 30 seconds you spend rewording "updated stuff" into something your future self will thank you for. It's a writing assistant, not a thinking replacement.

## License

MIT License - see [LICENSE](LICENSE) for details.
