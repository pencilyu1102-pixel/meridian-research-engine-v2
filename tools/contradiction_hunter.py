"""Find vague or contradictory phrasing in research drafts."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Sequence


BANNED_PHRASES = (
    "长期看好，短期波动",
    "建议投资者谨慎",
    "一方面",
    "另一方面",
    "估值合理，但需关注风险",
    "跌到某整数点位就加仓",
    "涨到某整数点位就减仓",
)


def find_banned_phrases(text: str) -> list[str]:
    """Return banned vague phrases found in text."""

    return [phrase for phrase in BANNED_PHRASES if phrase in text]


def render_findings(findings: Sequence[str]) -> str:
    """Render contradiction findings as Markdown."""

    if not findings:
        return "No banned vague phrases found."
    lines = ["# Contradiction Hunter Findings", ""]
    lines.extend(f"- {phrase}" for phrase in findings)
    return "\n".join(lines)


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Find banned vague phrases in a Markdown report.")
    parser.add_argument("path", help="Path to Markdown file")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_arg_parser().parse_args(argv)
    text = Path(args.path).read_text(encoding="utf-8")
    print(render_findings(find_banned_phrases(text)))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
