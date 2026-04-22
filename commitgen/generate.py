import os

from commitgen.prompt import SYSTEM_PROMPT, build_prompt
from commitgen.diff import DiffSummary, truncate_diff


def generate_message(diff: DiffSummary, backend: str = "claude") -> str:
    truncated = truncate_diff(diff.raw_diff)
    prompt = build_prompt(truncated, diff.stats, diff.staged_files)

    if backend == "ollama":
        return _generate_ollama(prompt)
    return _generate_claude(prompt)


def _generate_claude(prompt: str) -> str:
    import anthropic

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError(
            "ANTHROPIC_API_KEY not set. Export it or use --local for Ollama.\n"
            "  export ANTHROPIC_API_KEY=your-key-here"
        )

    client = anthropic.Anthropic(api_key=api_key)
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=256,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text.strip()


def _generate_ollama(prompt: str) -> str:
    try:
        import httpx
    except ImportError:
        raise RuntimeError(
            "httpx is required for Ollama support.\n"
            "  pip install commitgen[ollama]"
        )

    response = httpx.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "qwen2.5:3b",
            "system": SYSTEM_PROMPT,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.3},
        },
        timeout=30.0,
    )

    if response.status_code != 200:
        raise RuntimeError(
            "Ollama not running or model not found.\n"
            "  brew install ollama && ollama pull qwen2.5:3b"
        )

    return response.json()["response"].strip()
