---
name: Web Research
description: Mandatory live research - verify versions, URLs, dates, CVEs, and host status on the web every run, from primary sources with exact status codes, never from memory or one snippet. Use before any claim about the outside world.
---

# Web Research

Adapted from sandbase multi-source-search and the repo's live-discovery rule.

## Live first

- Websearch before acting on any external fact: upstream version, release
  date, artifact URL, checksum, advisory, or host status.
- Prefer primary sources: upstream release APIs, Fedora/COPR docs, NVD/GHSA,
  OSV, project repositories. Blogs and snippets are leads, not authority.
- Re-discover environment facts every run (stable Fedora, EOL dates,
  chroots, tool versions). Never hardcode them from memory or AGENTS.md.
- Quote the exact status/URL when claiming a host is blocked. A 403 on one
  asset path does not mean the project is unavailable; try the API/archive
  endpoints and mirrors first.

## Honesty

- Cross-check catalogs (Repology, official dist-git, Terra) but keep this
  repo's own evidence authoritative for what it ships.
- If a search returns nothing, say so. Absence of a result is not proof of
  clean, and a stale cached answer is not a live check.
- Record the date and source beside every external fact you put in the relay.
