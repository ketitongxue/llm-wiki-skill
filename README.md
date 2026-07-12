# LLM Wiki Skill

LLM Wiki Skill is a public, file-based workflow for building a knowledge base that grows through reusable mechanism pages, hubs, explicit provenance, and consistent maintenance.

## Capabilities

- Initialize a Raw / Wiki / Schema knowledge base.
- Ingest sources into connected, reusable knowledge.
- Query through indexes, hubs, and links.
- Lint structure, metadata, links, privacy, and maintenance records.
- Maintain existing concepts while preserving conflicts and provenance.

## Install for Codex

Clone or download a release, then place the `llm-wiki` directory inside the Agent's skill root so that `llm-wiki/SKILL.md` is present. For Codex, the commonly used user skill root is `~/.codex/skills/`.

Read [Agent compatibility](references/agent-compatibility.md) before using another Agent. Installation never grants filesystem, shell, browser, or network permission.

## Start a wiki

Initialize an empty or not-yet-created directory with the standard-library CLI:

```bash
python3 scripts/init_wiki.py --path ./my-wiki --domain "distributed systems"
```

The initializer creates `SCHEMA.md`, `purpose.md`, `index.md`, and `log.md`, plus the Raw and Wiki subdirectories. It refuses to overwrite a non-empty directory and fails if a bundled template contains an undeclared placeholder.

You can also ask the Agent:

> Initialize an LLM Wiki in this directory using the bundled templates. Help me define its purpose and schema before ingesting sources.

Then try:

> Ingest this source into the wiki. Preserve provenance, reinforce existing mechanism pages, update reciprocal links, and lint the result.

## Documentation

- [Skill instructions](SKILL.md)
- [Ingest workflow](references/ingest-workflow.md)
- [Lint checklist](references/lint-checklist.md)
- [Publishing example](references/publishing-example.md)
- [Agent compatibility](references/agent-compatibility.md)

## Inspiration and attribution

This project is inspired by Andrej Karpathy's [LLM Wiki pattern](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f): compile source material into a persistent, structured wiki that can be maintained and reused by an Agent. This repository is an independent implementation of that idea, with its own public instructions, templates, compatibility boundaries, and validation contract.

## Development

The repository tests use only the Python standard library. Run the complete verification suite from the repository root:

```bash
python3 -m unittest discover -s tests -v
python3 scripts/validate.py
```

The suite and validator verify the public file contract, version metadata, Skill frontmatter, UTF-8/LF encoding, relative Markdown links, symlinks, undeclared template placeholders, and private or credential-like markers. The validator skips only `.git/`, `dist/`, and `__pycache__/` directories.

## Build a release

Build the deterministic ZIP and checksum manifest from the explicit public allowlist:

```bash
python3 scripts/package_release.py --output-dir dist
```

For version 1.0.0 this creates `dist/llm-wiki-skill-v1.0.0.zip` and `dist/SHA256SUMS.txt`. The archive always installs as a single `llm-wiki/` directory, uses normalized metadata, and excludes development files.

Verify a downloaded release from the directory containing both files:

```bash
shasum -a 256 -c SHA256SUMS.txt
```

Release tags must match `v$(cat VERSION)`. The release workflow runs the full test and validation suites, builds twice, compares both artifacts, and publishes only the ZIP and checksum manifest.

## License

MIT. See [LICENSE](LICENSE).
