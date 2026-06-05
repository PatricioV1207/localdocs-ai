# Security Policy

LocalDocs AI is designed to be local-first, but contributors and users should still handle documents, exports, and API keys carefully.

## Supported Versions

Security fixes are considered for the current development version in this repository.

## Reporting a Vulnerability

Please do not post sensitive security details, private documents, or API keys in public issues.

If GitHub private vulnerability reporting is enabled for this repository, use that path. Otherwise, open a public issue with a minimal description and ask for a private follow-up path before sharing details.

Useful information to include safely:

- A short description of the affected area.
- Whether the issue affects local files, exports, document parsing, or optional OpenAI usage.
- Steps to reproduce using non-sensitive sample data.

## Secret Handling

- Do not commit `.env` files or API keys.
- Do not include private document contents in bug reports.
- Review generated Markdown and TSV exports before sharing them.
