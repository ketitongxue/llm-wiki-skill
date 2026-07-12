from pathlib import Path
from tempfile import TemporaryDirectory
import subprocess
import sys
import unittest
from unittest.mock import patch

from scripts import init_wiki
from scripts.init_wiki import initialize


class InitializeWikiTests(unittest.TestCase):
    def test_initializes_an_empty_destination_from_templates(self):
        with TemporaryDirectory() as temporary:
            destination = Path(temporary) / "knowledge"
            initialize(destination, "distributed systems")

            expected_files = {"SCHEMA.md", "purpose.md", "index.md", "log.md"}
            self.assertEqual(
                {path.name for path in destination.iterdir() if path.is_file()},
                expected_files,
            )
            expected_directories = {
                "raw/articles", "raw/papers", "raw/transcripts", "raw/assets",
                "wiki/entities", "wiki/concepts", "wiki/comparisons", "wiki/queries",
            }
            self.assertTrue(all((destination / path).is_dir() for path in expected_directories))
            for filename in expected_files:
                text = (destination / filename).read_text(encoding="utf-8")
                self.assertNotIn("{" * 2, text)
            self.assertIn("distributed systems", (destination / "purpose.md").read_text(encoding="utf-8"))

    def test_rejects_non_empty_destination_without_changing_it(self):
        with TemporaryDirectory() as temporary:
            destination = Path(temporary)
            marker = destination / "keep.txt"
            marker.write_text("keep", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "empty"):
                initialize(destination, "systems")
            self.assertEqual(marker.read_text(encoding="utf-8"), "keep")

    def test_rejects_empty_domain(self):
        with TemporaryDirectory() as temporary:
            with self.assertRaisesRegex(ValueError, "domain"):
                initialize(Path(temporary) / "wiki", "   ")

    def test_rejects_any_undeclared_template_token_before_writing(self):
        variants = ["OTHER", "domain", " domain "]
        for value in variants:
            with self.subTest(value=value), TemporaryDirectory() as temporary:
                root = Path(temporary) / "package"
                templates = root / "templates"
                templates.mkdir(parents=True)
                domain_token = "{" * 2 + "DOMAIN" + "}" * 2
                for name in init_wiki.TEMPLATE_NAMES:
                    (templates / name).write_text(f"# {domain_token}\n", encoding="utf-8")
                unresolved = "{" * 2 + value + "}" * 2
                (templates / "index.md").write_text(f"# {unresolved}\n", encoding="utf-8")
                destination = Path(temporary) / "wiki"
                with patch.object(init_wiki, "ROOT", root):
                    with self.assertRaisesRegex(ValueError, "template token"):
                        initialize(destination, "systems")
                self.assertFalse(destination.exists())

    def test_cli_requires_path_and_domain_and_initializes(self):
        script = Path(__file__).resolve().parents[1] / "scripts/init_wiki.py"
        missing = subprocess.run(
            [sys.executable, str(script)], capture_output=True, text=True, check=False
        )
        self.assertNotEqual(missing.returncode, 0)
        self.assertIn("--path", missing.stderr)
        with TemporaryDirectory() as temporary:
            destination = Path(temporary) / "wiki"
            result = subprocess.run(
                [sys.executable, str(script), "--path", str(destination), "--domain", "systems"],
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((destination / "SCHEMA.md").is_file())


if __name__ == "__main__":
    unittest.main()
