from pathlib import Path
from tempfile import TemporaryDirectory
import os
import subprocess
import sys
import unittest

from scripts.validate import validate_repository


ROOT = Path(__file__).resolve().parents[1]


class ValidateRepositoryTests(unittest.TestCase):
    def test_current_repository_is_valid(self):
        self.assertEqual(validate_repository(ROOT), [])

    def test_reports_missing_required_file(self):
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            errors = validate_repository(root)
            self.assertIn("missing required file: SKILL.md", errors)

    def test_reports_private_markers_credentials_crlf_and_unknown_tokens(self):
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            self._copy_minimal_repository(root)
            private_path = "/" + "Users/alice/wiki"
            domain = "juzxai" + "lab.com"
            repository = "my-vitepress" + "-notes"
            credential = "ghp_" + "abcdefghijklmnopqrstuvwxyz123456"
            token = "{{" + "SECRET" + "}}"
            private_key = "-----BEGIN " + "PRIVATE KEY-----"
            content = f"# Docs\r\n{private_path}\r\nC:\\Users\\alice\\wiki\r\n{domain} {repository} {credential} {token}\r\n{private_key}\r\n"
            (root / "README.md").write_bytes(content.encode("utf-8"))
            errors = "\n".join(validate_repository(root))
            for expected in ["CRLF", "/" + "Users/", "Windows user path", domain,
                             repository, "credential", "private key", token]:
                self.assertIn(expected, errors)

    def test_reports_absolute_or_broken_markdown_links_and_bad_frontmatter(self):
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            self._copy_minimal_repository(root)
            (root / "SKILL.md").write_text(
                "# no frontmatter\n[absolute](/private.md)\n[broken](missing.md)\n",
                encoding="utf-8",
            )
            errors = "\n".join(validate_repository(root))
            self.assertIn("frontmatter", errors)
            self.assertIn("absolute Markdown link", errors)
            self.assertIn("broken relative Markdown link", errors)

    def test_reports_symlinks_but_ignores_exact_generated_directories(self):
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            self._copy_minimal_repository(root)
            target = root / "README.md"
            try:
                os.symlink(target, root / "linked.md")
            except (OSError, NotImplementedError):
                self.skipTest("symlinks unavailable")
            for ignored in [".git", "dist", "__pycache__"]:
                folder = root / ignored
                folder.mkdir()
                bad = "/" + "Users/private " + "{{" + "BAD" + "}}"
                (folder / "bad.md").write_text(bad, encoding="utf-8")
            errors = validate_repository(root)
            self.assertEqual(sum("symlink" in error for error in errors), 1)
            self.assertFalse(any("bad.md" in error for error in errors))

    def test_cli_returns_zero_for_valid_repository_and_nonzero_for_invalid(self):
        script = ROOT / "scripts/validate.py"
        valid = subprocess.run(
            [sys.executable, str(script), str(ROOT)], capture_output=True, text=True, check=False
        )
        self.assertEqual(valid.returncode, 0, valid.stdout + valid.stderr)
        with TemporaryDirectory() as temporary:
            invalid = subprocess.run(
                [sys.executable, str(script), temporary], capture_output=True, text=True, check=False
            )
        self.assertNotEqual(invalid.returncode, 0)
        self.assertIn("missing required file", invalid.stdout)

    def _copy_minimal_repository(self, root: Path):
        required = [
            "SKILL.md", "README.md", "LICENSE", "CHANGELOG.md", "VERSION",
            "templates/SCHEMA.md", "templates/purpose.md", "templates/index.md", "templates/log.md",
            "references/agent-compatibility.md", "references/ingest-workflow.md",
            "references/lint-checklist.md", "references/publishing-example.md",
        ]
        for relative in required:
            destination = root / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            if relative == "SKILL.md":
                content = "---\nname: llm-wiki\ndescription: test\nlicense: MIT\n---\n# Skill\n"
            elif relative.startswith("templates/"):
                content = "# {{" + "DOMAIN" + "}}\n"
            else:
                content = "# Public\n"
            destination.write_text(content, encoding="utf-8", newline="\n")


if __name__ == "__main__":
    unittest.main()
