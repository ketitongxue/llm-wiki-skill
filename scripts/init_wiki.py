#!/usr/bin/env python3
"""Initialize an empty LLM Wiki from the bundled public templates."""

from argparse import ArgumentParser
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_NAMES = ("SCHEMA.md", "purpose.md", "index.md", "log.md")
DIRECTORIES = (
    "raw/articles", "raw/papers", "raw/transcripts", "raw/assets",
    "wiki/entities", "wiki/concepts", "wiki/comparisons", "wiki/queries",
)
TOKEN_PATTERN = re.compile(r"\{\{[A-Z][A-Z0-9_]*\}\}")


def initialize(destination: Path, domain: str) -> None:
    destination = Path(destination)
    domain = domain.strip()
    if not domain:
        raise ValueError("domain must not be empty")
    if destination.exists() and any(destination.iterdir()):
        raise ValueError("destination must be empty")

    rendered = {}
    for name in TEMPLATE_NAMES:
        source = (ROOT / "templates" / name).read_text(encoding="utf-8")
        text = source.replace("{{DOMAIN}}", domain)
        remaining = TOKEN_PATTERN.findall(text)
        if remaining:
            raise ValueError(f"unresolved template token in {name}: {remaining[0]}")
        rendered[name] = text

    destination.mkdir(parents=True, exist_ok=True)
    for relative in DIRECTORIES:
        (destination / relative).mkdir(parents=True, exist_ok=True)
    for name, text in rendered.items():
        (destination / name).write_text(text, encoding="utf-8", newline="\n")


def main() -> int:
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--path", required=True, type=Path)
    parser.add_argument("--domain", required=True)
    args = parser.parse_args()
    try:
        initialize(args.path, args.domain)
    except (OSError, ValueError) as error:
        parser.error(str(error))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
