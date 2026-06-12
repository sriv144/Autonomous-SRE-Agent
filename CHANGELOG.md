# Changelog

All notable changes to KubeSentient (Autonomous SRE Agent).

Format loosely based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added
- Repository scaffolding: GitHub issue templates (bug / feature) with surface + deployment dropdowns, PR template with an SRE safety checklist (human-approval gate, AlertManager payload validation, least-privilege RBAC), and this changelog. (`claude/fervent-edison-qiarsa`)
- `RESEARCH_LOG.md` — persistent memory for the auto-researcher agent.

### Notes
- See `RESEARCH_LOG.md` for scoring history and queued next-run candidates.
- Existing open `claude/*` branches contain prior, unmerged proposals (CI workflow, MIT LICENSE, Makefile, `K8S_LOCAL_MODE` env toggle, Anthropic Claude LLM provider migration, SECURITY.md).
