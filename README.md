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

Create an empty directory and ask the Agent:

> Initialize an LLM Wiki in this directory using the bundled templates. Help me define its purpose and schema before ingesting sources.

Then try:

> Ingest this source into the wiki. Preserve provenance, reinforce existing mechanism pages, update reciprocal links, and lint the result.

## Documentation

- [Skill instructions](SKILL.md)
- [Ingest workflow](references/ingest-workflow.md)
- [Lint checklist](references/lint-checklist.md)
- [Publishing example](references/publishing-example.md)
- [Agent compatibility](references/agent-compatibility.md)

## License

MIT. See [LICENSE](LICENSE).
