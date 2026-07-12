---
name: llm-wiki
description: Build, ingest, query, lint, and maintain a local LLM Wiki knowledge base using Raw, Wiki, and Schema layers.
license: MIT
---

# LLM Wiki

Use this skill when a user wants to initialize, ingest into, query, lint, or maintain a file-based knowledge base. Keep every operation inside the knowledge-base root authorized by the user.

## Operating model

- **Raw** preserves source material and provenance.
- **Wiki** contains durable mechanism pages, concepts, entities, and hubs.
- **Schema** defines structure, naming, metadata, and maintenance rules.

Prefer a connected explanation that can be reused across sources over a recap tied to one source. Treat `purpose.md`, `SCHEMA.md`, `index.md`, and `log.md` as the orientation surface.

## Orient before editing

1. Confirm the knowledge-base root and requested operation.
2. Read `purpose.md`, `SCHEMA.md`, `index.md`, and the newest entries in `log.md`.
3. Inspect nearby hubs and pages before creating a new page.
4. Preserve local conventions unless the user explicitly changes them.

## Initialize

1. Copy [the purpose template](templates/purpose.md), [schema template](templates/SCHEMA.md), [index template](templates/index.md), and [log template](templates/log.md) into an empty knowledge-base root.
2. Create `raw/`, `wiki/`, and `schema/` directories if the schema calls for them.
3. Replace the example scope and taxonomy with user-approved values.
4. Run the lint checklist before reporting completion.

## Ingest

Follow [the ingest workflow](references/ingest-workflow.md).

1. Capture source content or a stable source record in Raw.
2. Identify claims, mechanisms, entities, constraints, and unresolved questions.
3. Update an existing mechanism page or hub when the concept already exists.
4. Create a new page only when it has a distinct reusable identity.
5. Add meaningful reciprocal links; do not create links merely to increase link count.
6. Update the index and prepend a concise log entry.
7. Resolve contradictions by preserving both sourced claims and stating the current synthesis.

## Query

1. Begin with the index and relevant hubs.
2. Traverse links into the smallest set of pages that supports the answer.
3. Distinguish stored knowledge from inference.
4. Cite page paths and identify missing or conflicting knowledge.
5. Do not silently modify the wiki during a read-only query.

## Lint

Use [the lint checklist](references/lint-checklist.md) to check metadata, links, index coverage, log order, orphan pages, encoding, and sensitive information. Fix only issues within the user's requested scope.

## Maintain

1. Prefer incremental edits to rewrites.
2. Preserve source provenance when merging claims.
3. Keep hubs navigational and mechanism pages focused.
4. Record structural changes in `log.md`.
5. Re-run lint after changes.

## References

- [Agent compatibility](references/agent-compatibility.md): read before installation or when tool permissions are uncertain.
- [Ingest workflow](references/ingest-workflow.md): read for source-to-wiki work.
- [Lint checklist](references/lint-checklist.md): read before declaring writes complete.
- [Publishing example](references/publishing-example.md): read only when the user requests publication.
- [Purpose template](templates/purpose.md)
- [Schema template](templates/SCHEMA.md)
- [Index template](templates/index.md)
- [Log template](templates/log.md)

## Boundaries

- Ask before expanding the authorized filesystem or publication scope.
- Network access, dependency installation, repository creation, pushing, and publishing remain subject to the host Agent's permissions and user confirmation.
- Do not expose raw sources, credentials, private paths, or personal configuration.
- A publication workflow is optional; the knowledge base remains useful without a website or remote service.
