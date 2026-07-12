from pathlib import Path
import re
import unittest


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
