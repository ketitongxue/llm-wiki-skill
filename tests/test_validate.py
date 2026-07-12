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
            token = "{" * 2 + "SECRET" + "}" * 2
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

    def test_requires_exact_public_skill_frontmatter_fields(self):
        variants = [
            "---\nname: other\ndescription: public\nlicense: MIT\n---\n# Skill\n",
            "---\nname: llm-wiki\ndescription: \nlicense: MIT\n---\n# Skill\n",
            "---\nname: llm-wiki\ndescription: public\nlicense: GPL\n---\n# Skill\n",
        ]
        for content in variants:
            with self.subTest(content=content), TemporaryDirectory() as temporary:
                root = Path(temporary)
                self._copy_minimal_repository(root)
                (root / "SKILL.md").write_text(content, encoding="utf-8")
                self.assertIn("frontmatter", "\n".join(validate_repository(root)))

    def test_reports_assignment_secrets_and_multiple_private_key_headers_without_echoing_values(self):
        assignments = [
            ("api_key", "sk-test-secret"),
            ("token", "token-test-secret"),
            ("client_secret", "client-secret-value"),
        ]
        headers = ["RSA PRIVATE KEY", "EC PRIVATE KEY", "OPENSSH PRIVATE KEY"]
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            self._copy_minimal_repository(root)
            lines = [f'{name} = "{value}"' for name, value in assignments]
            lines.extend("-----BEGIN " + header + "-----" for header in headers)
            (root / "settings.toml").write_text("\n".join(lines) + "\n", encoding="utf-8")
            errors = validate_repository(root)
            rendered = "\n".join(errors)
            self.assertGreaterEqual(sum("possible credential assignment" in error for error in errors), 3)
            self.assertGreaterEqual(sum("private key material" in error for error in errors), 3)
            for _, value in assignments:
                self.assertNotIn(value, rendered)

    def test_scans_shell_toml_ini_and_cfg_text_for_encoding_line_endings_and_secrets(self):
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            self._copy_minimal_repository(root)
            samples = {}
            for filename, name, value, newline in [
                ("deploy.sh", "token", "shell-secret-value", "\n"),
                ("settings.toml", "api_key", "sk-test-secret", "\n"),
                ("app.ini", "secret", "ini-secret-value", "\r\n"),
                ("tool.cfg", "password", "cfg-secret-value", "\n"),
            ]:
                samples[filename] = f'{name} = "{value}"{newline}'.encode()
            for name, raw in samples.items():
                (root / name).write_bytes(raw)
            rendered = "\n".join(validate_repository(root))
            for name in samples:
                self.assertIn(name, rendered)
            self.assertIn("CRLF", rendered)

    def test_only_templates_may_contain_the_exact_domain_placeholder(self):
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            self._copy_minimal_repository(root)
            exact = "{" * 2 + "DOMAIN" + "}" * 2
            (root / "README.md").write_text(f"# Public\n{exact}\n", encoding="utf-8")
            spaced = "{" * 2 + " domain " + "}" * 2
            (root / "templates/index.md").write_text(f"# {spaced}\n", encoding="utf-8")
            errors = "\n".join(validate_repository(root))
            self.assertIn("README.md", errors)
            self.assertIn("templates/index.md", errors)
            self.assertIn("template token", errors)

    def test_allows_only_the_standard_github_token_expression_in_release_workflow(self):
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            self._copy_minimal_repository(root)
            workflow = root / ".github/workflows/release.yml"
            workflow.parent.mkdir(parents=True)
            expression = "$" + "{" * 2 + " github.token " + "}" * 2
            workflow.write_text(f"env:\n  GH_TOKEN: {expression}\n", encoding="utf-8")
            self.assertEqual(validate_repository(root), [])

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
                bad = "/" + "Users/private " + "{" * 2 + "BAD" + "}" * 2
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
                content = "# " + "{" * 2 + "DOMAIN" + "}" * 2 + "\n"
            else:
                content = "# Public\n"
            destination.write_text(content, encoding="utf-8", newline="\n")


if __name__ == "__main__":
    unittest.main()
