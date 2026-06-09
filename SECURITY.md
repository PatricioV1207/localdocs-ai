# Security Policy

LocalDocs AI is designed to be local-first, but contributors and users should still handle documents, exports, and API keys carefully.

## Supported Versions

Security fixes are considered for the current release and the current
development branch.

| Version | Supported |
| --- | --- |
| 0.3.x | Yes |
| 0.2.x and earlier | No |

## Reporting a Vulnerability

Please do not post sensitive security details, private documents, or API keys in public issues.

Use GitHub's **Report a vulnerability** option in the repository Security tab
when it is available. If private vulnerability reporting is unavailable, open
a public issue containing only a request for a private contact channel. Do not
include exploit details, private document text, local paths, or secrets.

Useful information to include safely:

- A short description of the affected area.
- Whether the issue affects local files, exports, document parsing, or optional OpenAI usage.
- Steps to reproduce using non-sensitive sample data.
- The affected version or commit.
- The likely impact and whether local user interaction is required.

## Response Expectations

Maintainers will aim to acknowledge a private report within seven days. Timing
for investigation and a fix depends on severity and reproducibility. Please
allow time for a coordinated fix before public disclosure.

## Secret Handling

- Do not commit `.env` files or API keys.
- Do not include private document contents in bug reports.
- Review generated Markdown and TSV exports before sharing them.
- Treat uploaded documents as untrusted input and keep dependencies updated.
- Use a dedicated API key with appropriate limits if optional OpenAI mode is
  enabled.

## Scope Notes

LocalDocs AI runs as a local Streamlit application. It does not provide
authentication, tenant isolation, encrypted storage, or a hardened internet
service boundary. Do not expose the development server directly to untrusted
networks.
