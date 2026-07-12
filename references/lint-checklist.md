# Lint Checklist

Run the repository validator before committing or releasing public changes:

```bash
python3 scripts/validate.py
```

For an initialized knowledge base, apply the same checks to its authorized root. The bundled validator is intentionally repository-focused; an Agent may add domain-specific checks from the local `SCHEMA.md`, but must not weaken the safety checks below.

## Structure

- Required orientation files exist.
- Templates contain only the declared DOMAIN placeholder (written as two opening braces, `DOMAIN`, and two closing braces), and initialized files contain no unresolved placeholders.
- Raw / Wiki / Schema responsibilities are not mixed.
- Wiki pages follow the frontmatter and naming contract.

## Links and navigation

- Relative links resolve.
- Markdown links do not use absolute filesystem paths or escape the authorized root.
- New durable pages appear in an index or hub.
- Reciprocal links express a meaningful relationship.
- No unintended orphan pages remain.

## Maintenance

- Log entries are newest first.
- Existing concepts were reinforced before synonyms were created.
- Conflicting sourced claims remain visible.

## Safety

- No credentials, cookies, private keys, or secret values are present.
- No private paths or unrelated personal data are exposed.
- No symlinks redirect validation or publication outside the authorized root.
- Publication excludes Raw material unless the user explicitly approved it.

## Files

- Text is UTF-8 with LF line endings.
- Only `.git/`, `dist/`, and `__pycache__/` are excluded by the public repository validator; similarly named directories are still checked.
