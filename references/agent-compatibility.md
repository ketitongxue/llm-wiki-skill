# Agent Compatibility

## Native skill discovery

An Agent that discovers directories containing `SKILL.md` can install this repository under its documented skill root. Codex commonly uses `~/.codex/skills/llm-wiki/SKILL.md` for a user installation.

## Manual instruction loading

If an Agent does not discover skills automatically but can read local files, load `SKILL.md` as project instructions and make the repository available as read-only supporting context.

## Method-only use

A chat model without filesystem tools can explain the method but cannot claim to initialize files, validate links, or publish changes.

## Permission boundary

The Skill never expands host permissions. Reading, writing, shell execution, browser access, network access, repository operations, and publication still require the host Agent's capabilities and the user's authorization.
