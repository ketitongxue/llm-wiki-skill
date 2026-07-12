# Schema

## Layers

- `raw/`: immutable or append-only source captures with provenance.
- `wiki/`: durable concepts, mechanisms, entities, and hubs.
- `schema/`: optional taxonomies and structured definitions used by the wiki.

## Page contract

Every Wiki page uses this frontmatter:

```yaml
---
title: Example mechanism
type: mechanism
status: active
tags:
  - example
sources:
  - ../raw/example-source.md
---
```

Allowed `type` values: `hub`, `mechanism`, `concept`, and `entity`.

## Naming and linking

- Use descriptive lowercase file names separated by hyphens.
- Use relative Markdown links.
- Add reciprocal links when both pages help readers navigate the relationship.
- Prefer updating an existing page over creating a synonym.

## Maintenance

- Keep `index.md` complete and navigational.
- Keep `log.md` newest first.
- Preserve conflicting sourced claims and document the current synthesis.
