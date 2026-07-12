from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
import re
import subprocess
import sys
import unittest
from zipfile import ZipFile

from scripts.package_release import build
from scripts.validate import validate_repository


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_ARCHIVE_FILES = {
    "llm-wiki/CHANGELOG.md",
    "llm-wiki/LICENSE",
    "llm-wiki/README.md",
    "llm-wiki/SKILL.md",
    "llm-wiki/VERSION",
    "llm-wiki/references/agent-compatibility.md",
    "llm-wiki/references/ingest-workflow.md",
    "llm-wiki/references/lint-checklist.md",
    "llm-wiki/references/publishing-example.md",
    "llm-wiki/scripts/init_wiki.py",
    "llm-wiki/scripts/validate.py",
    "llm-wiki/templates/SCHEMA.md",
    "llm-wiki/templates/index.md",
    "llm-wiki/templates/log.md",
    "llm-wiki/templates/purpose.md",
}


class PackageReleaseTests(unittest.TestCase):
    def test_two_builds_are_byte_for_byte_reproducible(self):
        with TemporaryDirectory() as temporary:
            first_zip, first_checksum = build(ROOT, Path(temporary) / "first")
            second_zip, second_checksum = build(ROOT, Path(temporary) / "second")

            self.assertEqual(first_zip.read_bytes(), second_zip.read_bytes())
            self.assertEqual(first_checksum.read_bytes(), second_checksum.read_bytes())
            digest = sha256(first_zip.read_bytes()).hexdigest()
            self.assertEqual(
                first_checksum.read_text(encoding="utf-8"),
                f"{digest}  llm-wiki-skill-v1.0.0.zip\n",
            )

    def test_archive_has_only_safe_normalized_allowlisted_entries(self):
        with TemporaryDirectory() as temporary:
            archive, _ = build(ROOT, Path(temporary))
            with ZipFile(archive) as bundle:
                names = bundle.namelist()
                self.assertEqual(names, sorted(EXPECTED_ARCHIVE_FILES))
                self.assertEqual(len(names), len(set(names)))
                for info in bundle.infolist():
                    path = Path(info.filename)
                    self.assertFalse(path.is_absolute())
                    self.assertNotIn("..", path.parts)
                    self.assertEqual(path.parts[0], "llm-wiki")
                    self.assertEqual(info.date_time, (1980, 1, 1, 0, 0, 0))
                    self.assertEqual(info.external_attr >> 16, 0o100644)

    def test_archive_installs_at_codex_skill_path_and_validates(self):
        with TemporaryDirectory() as temporary:
            temporary_path = Path(temporary)
            archive, _ = build(ROOT, temporary_path / "build")
            skill_root = temporary_path / ".codex" / "skills"
            skill_root.mkdir(parents=True)
            with ZipFile(archive) as bundle:
                bundle.extractall(skill_root)
            installed = skill_root / "llm-wiki"
            self.assertTrue((installed / "SKILL.md").is_file())
            self.assertEqual(validate_repository(installed), [])

    def test_cli_writes_named_release_files(self):
        with TemporaryDirectory() as temporary:
            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "package_release.py"),
                    "--root",
                    str(ROOT),
                    "--output-dir",
                    temporary,
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertTrue((Path(temporary) / "llm-wiki-skill-v1.0.0.zip").is_file())
            self.assertTrue((Path(temporary) / "SHA256SUMS.txt").is_file())

    def test_ci_workflow_uses_official_pinned_actions_and_validation_commands(self):
        workflow = (ROOT / ".github/workflows/test.yml").read_text(encoding="utf-8")
        self.assertIn("pull_request:", workflow)
        self.assertIn("main", workflow)
        self.assertIn("actions/checkout@v4", workflow)
        self.assertIn("actions/setup-python@v5", workflow)
        self.assertIn("python-version: '3.12'", workflow)
        self.assertIn("python3 -m unittest discover -s tests -v", workflow)
        self.assertIn("python3 scripts/validate.py", workflow)
        uses = re.findall(r"uses:\s*(\S+)", workflow)
        self.assertEqual(uses, ["actions/checkout@v4", "actions/setup-python@v5"])

    def test_release_workflow_builds_twice_and_publishes_exact_release_assets(self):
        workflow = (ROOT / ".github/workflows/release.yml").read_text(encoding="utf-8")
        for expected in [
            "tags:",
            "- 'v*'",
            "contents: write",
            "actions/checkout@v4",
            "actions/setup-python@v5",
            "python-version: '3.12'",
            'test "v$(cat VERSION)" = "$GITHUB_REF_NAME"',
            "python3 -m unittest discover -s tests -v",
            "python3 scripts/validate.py",
            "python3 scripts/package_release.py --output-dir dist/first",
            "python3 scripts/package_release.py --output-dir dist/second",
            "cmp dist/first/llm-wiki-skill-$GITHUB_REF_NAME.zip dist/second/llm-wiki-skill-$GITHUB_REF_NAME.zip",
            "cmp dist/first/SHA256SUMS.txt dist/second/SHA256SUMS.txt",
            "gh release create",
            "dist/first/llm-wiki-skill-$GITHUB_REF_NAME.zip",
            "dist/first/SHA256SUMS.txt",
            "GH_TOKEN:",
        ]:
            self.assertIn(expected, workflow)
        uses = re.findall(r"uses:\s*(\S+)", workflow)
        self.assertEqual(uses, ["actions/checkout@v4", "actions/setup-python@v5"])

    def test_readme_documents_reproducible_release_build_and_checksum(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("## Build a release", readme)
        self.assertIn("python3 scripts/package_release.py --output-dir dist", readme)
        self.assertIn("llm-wiki-skill-v1.0.0.zip", readme)
        self.assertIn("SHA256SUMS.txt", readme)
        self.assertIn("shasum -a 256 -c SHA256SUMS.txt", readme)


if __name__ == "__main__":
    unittest.main()
