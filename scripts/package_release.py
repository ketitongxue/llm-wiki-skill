#!/usr/bin/env python3
"""Build the reproducible LLM Wiki Skill release archive."""

from argparse import ArgumentParser
from hashlib import sha256
from pathlib import Path, PurePosixPath
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo


ARCHIVE_ROOT = "llm-wiki"
FIXED_TIMESTAMP = (1980, 1, 1, 0, 0, 0)
FILE_MODE = 0o100644
ALLOWLIST = tuple(sorted((
    "CHANGELOG.md",
    "LICENSE",
    "README.md",
    "SKILL.md",
    "VERSION",
    "references/agent-compatibility.md",
    "references/ingest-workflow.md",
    "references/lint-checklist.md",
    "references/publishing-example.md",
    "scripts/init_wiki.py",
    "scripts/validate.py",
    "templates/SCHEMA.md",
    "templates/index.md",
    "templates/log.md",
    "templates/purpose.md",
)))


def _version(root: Path) -> str:
    version = (root / "VERSION").read_text(encoding="utf-8").strip()
    if not version or any(character not in "0123456789." for character in version):
        raise ValueError("VERSION must contain a dotted numeric version")
    return version


def _source_files(root: Path) -> list[tuple[str, Path]]:
    sources = []
    for relative in ALLOWLIST:
        archive_path = PurePosixPath(ARCHIVE_ROOT, relative)
        if archive_path.is_absolute() or ".." in archive_path.parts:
            raise ValueError(f"unsafe archive path: {archive_path}")
        source = root / relative
        if not source.is_file() or source.is_symlink():
            raise ValueError(f"missing or unsafe release file: {relative}")
        sources.append((archive_path.as_posix(), source))
    archive_names = [name for name, _ in sources]
    if archive_names != sorted(set(archive_names)):
        raise ValueError("release allowlist must produce sorted unique entries")
    return sources


def build(root: Path, output_dir: Path) -> tuple[Path, Path]:
    """Build a deterministic ZIP and SHA256SUMS file from the public allowlist."""
    root = Path(root).resolve()
    output_dir = Path(output_dir)
    version = _version(root)
    output_dir.mkdir(parents=True, exist_ok=True)
    archive = output_dir / f"llm-wiki-skill-v{version}.zip"
    checksum = output_dir / "SHA256SUMS.txt"

    with ZipFile(archive, "w", compression=ZIP_DEFLATED, compresslevel=9) as bundle:
        for archive_name, source in _source_files(root):
            info = ZipInfo(archive_name, date_time=FIXED_TIMESTAMP)
            info.compress_type = ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = FILE_MODE << 16
            bundle.writestr(
                info,
                source.read_bytes(),
                compress_type=ZIP_DEFLATED,
                compresslevel=9,
            )

    digest = sha256(archive.read_bytes()).hexdigest()
    checksum.write_text(
        f"{digest}  {archive.name}\n",
        encoding="utf-8",
        newline="\n",
    )
    return archive, checksum


def main() -> int:
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--output-dir", type=Path, default=Path("dist"))
    args = parser.parse_args()
    archive, checksum = build(args.root, args.output_dir)
    print(archive)
    print(checksum)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
