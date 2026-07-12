from pathlib import Path
import re
import unittest
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    "SKILL.md",
    "README.md",
    "LICENSE",
    "CHANGELOG.md",
    "VERSION",
    "templates/SCHEMA.md",
    "templates/purpose.md",
    "templates/index.md",
    "templates/log.md",
    "references/agent-compatibility.md",
    "references/ingest-workflow.md",
    "references/lint-checklist.md",
    "references/publishing-example.md",
]

FORBIDDEN_TEXT = [
    "/Users/",
    "keti",
    "juzxailab.com",
    "my-vitepress-notes",
    "Hermes",
    "Cloudflare",
]

IGNORED_PARTS = {".git", "dist", "__pycache__"}


def public_markdown_files():
    return sorted(
        path
        for path in ROOT.rglob("*.md")
        if not IGNORED_PARTS.intersection(path.relative_to(ROOT).parts)
    )


class RepositoryContractTests(unittest.TestCase):
    def test_required_files_exist(self):
        missing = [path for path in REQUIRED_FILES if not (ROOT / path).is_file()]
        self.assertEqual(missing, [])

    def test_version_is_1_0_0(self):
        self.assertEqual((ROOT / "VERSION").read_text(encoding="utf-8"), "1.0.0\n")

    def test_skill_frontmatter_has_public_metadata(self):
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        match = re.match(r"\A---\n(.*?)\n---\n", skill, re.DOTALL)
        self.assertIsNotNone(match)
        frontmatter = match.group(1)
        self.assertRegex(frontmatter, r"(?m)^name: llm-wiki$")
        self.assertRegex(frontmatter, r"(?m)^description: .+LLM Wiki.+$")
        self.assertRegex(frontmatter, r"(?m)^license: MIT$")

    def test_skill_links_point_to_existing_relative_files(self):
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        links = re.findall(r"\[[^]]+\]\(([^)]+\.md)\)", skill)
        self.assertGreaterEqual(len(links), 8)
        missing = [target for target in links if not (ROOT / target).is_file()]
        self.assertEqual(missing, [])

    def test_all_public_markdown_relative_links_exist(self):
        broken = []
        link_pattern = re.compile(r"\[[^]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
        for document in public_markdown_files():
            text = document.read_text(encoding="utf-8")
            for raw_target in link_pattern.findall(text):
                parsed = urlsplit(raw_target)
                if parsed.scheme in {"http", "https"} or raw_target.startswith("#"):
                    continue
                if parsed.scheme or raw_target.startswith("/"):
                    continue
                target = document.parent / unquote(parsed.path)
                if not target.exists():
                    broken.append(
                        f"{document.relative_to(ROOT)} -> {raw_target}"
                    )
        self.assertEqual(broken, [])

    def test_readme_attributes_the_original_pattern_and_documents_verification(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("## Inspiration and attribution", readme)
        self.assertIn(
            "https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f",
            readme,
        )
        self.assertIn("## Development", readme)
        self.assertIn("python3 -m unittest discover -s tests -v", readme)

    def test_gitignore_excludes_python_and_distribution_artifacts(self):
        gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()
        self.assertIn("__pycache__/", gitignore)
        self.assertIn("*.py[cod]", gitignore)
        self.assertIn("dist/", gitignore)

    def test_public_text_is_utf8_lf_and_contains_no_private_markers(self):
        violations = []
        for relative in REQUIRED_FILES:
            path = ROOT / relative
            raw = path.read_bytes()
            self.assertNotIn(b"\r\n", raw, relative)
            text = raw.decode("utf-8")
            for marker in FORBIDDEN_TEXT:
                if marker.lower() in text.lower():
                    violations.append(f"{relative}: {marker}")
        self.assertEqual(violations, [])


if __name__ == "__main__":
    unittest.main()
