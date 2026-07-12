#!/usr/bin/env python3
"""Validate the public repository structure, links, encoding, and privacy."""

from argparse import ArgumentParser
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit


REQUIRED_FILES = (
    "SKILL.md", "README.md", "LICENSE", "CHANGELOG.md", "VERSION",
    "templates/SCHEMA.md", "templates/purpose.md", "templates/index.md", "templates/log.md",
    "references/agent-compatibility.md", "references/ingest-workflow.md",
    "references/lint-checklist.md", "references/publishing-example.md",
)
IGNORED_DIRECTORIES = {".git", "dist", "__pycache__"}
TOKEN = re.compile(r"\{\{[^\r\n{}]*\}\}")
LINK = re.compile(r"\[[^]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
DOMAIN_TOKEN = "{" * 2 + "DOMAIN" + "}" * 2


def _files(root: Path):
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root)
        if IGNORED_DIRECTORIES.intersection(relative.parts):
            continue
        if path.is_symlink():
            yield path
        elif path.is_file():
            yield path


def _valid_skill_frontmatter(text: str) -> bool:
    match = re.match(r"\A---\n(.*?)\n---\n", text, re.DOTALL)
    if not match:
        return False
    fields = {}
    for line in match.group(1).splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            fields[key.strip()] = value.strip()
    return (
        fields.get("name") == "llm-wiki"
        and bool(fields.get("description"))
        and fields.get("license") == "MIT"
    )


def validate_repository(root: Path) -> list[str]:
    root = Path(root)
    errors: list[str] = []
    for relative in REQUIRED_FILES:
        if not (root / relative).is_file():
            errors.append(f"missing required file: {relative}")

    for path in _files(root):
        relative = path.relative_to(root).as_posix()
        if path.is_symlink():
            errors.append(f"symlink is not allowed: {relative}")
            continue
        raw = path.read_bytes()
        if b"\x00" in raw:
            continue
        if b"\r\n" in raw:
            errors.append(f"CRLF line endings are not allowed: {relative}")
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            errors.append(f"file is not UTF-8: {relative}")
            continue

        private_markers = (
            ("/" + "Users/", "/" + "Users/"),
            ("juzxai" + "lab.com", "juzxai" + "lab.com"),
            ("my-vitepress" + "-notes", "my-vitepress" + "-notes"),
        )
        for marker, label in private_markers:
            if marker.lower() in text.lower():
                errors.append(f"private marker {label}: {relative}")
        if re.search(r"[A-Za-z]:\\Users\\[^\\\s]+", text, re.IGNORECASE):
            errors.append(f"Windows user path: {relative}")
        if re.search(r"\b(?:gh[pousr]_[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9_-]{20,}|AKIA[A-Z0-9]{16})\b", text):
            errors.append(f"possible credential: {relative}")
        assignment = re.compile(
            r"(?im)^\s*[A-Za-z0-9_.-]*(?:api[_-]?key|token|secret|password)"
            r"[A-Za-z0-9_.-]*\s*[:=]\s*(['\"])[^'\"\r\n]{8,}\1\s*(?:#.*)?$"
        )
        for _ in assignment.finditer(text):
            errors.append(f"possible credential assignment: {relative}")
        private_key_header = re.compile(
            r"-----BEGIN (?:RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----"
        )
        for _ in private_key_header.finditer(text):
            errors.append(f"private key material: {relative}")

        for token in TOKEN.findall(text):
            allowed = relative in {
                "templates/SCHEMA.md", "templates/purpose.md",
                "templates/index.md", "templates/log.md",
            } and token == DOMAIN_TOKEN
            if not allowed:
                errors.append(f"undeclared template token {token}: {relative}")

        if path.suffix.lower() == ".md":
            if relative == "SKILL.md" and not _valid_skill_frontmatter(text):
                errors.append("SKILL.md has invalid frontmatter")
            for raw_target in LINK.findall(text):
                parsed = urlsplit(raw_target)
                if parsed.scheme in {"http", "https", "mailto"} or raw_target.startswith("#"):
                    continue
                if parsed.scheme or raw_target.startswith("/"):
                    errors.append(f"absolute Markdown link in {relative}: {raw_target}")
                    continue
                target = (path.parent / unquote(parsed.path)).resolve()
                try:
                    target.relative_to(root.resolve())
                except ValueError:
                    errors.append(f"relative Markdown link escapes repository in {relative}: {raw_target}")
                    continue
                if not target.exists():
                    errors.append(f"broken relative Markdown link in {relative}: {raw_target}")
    return errors


def main() -> int:
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default=Path.cwd(), type=Path)
    args = parser.parse_args()
    errors = validate_repository(args.root)
    if errors:
        for error in errors:
            print(error)
        return 1
    print("repository validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
