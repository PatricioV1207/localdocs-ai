# Screenshot Guide

The SVG files in this directory reserve stable README image paths until final
PNG captures are approved.

When release screenshots are ready, add PNG files using the same base names and
update the two image links in `README.md`:

- `app-overview`: initial app state after processing `sample_docs/`.
- `qa-with-sources`: the sample TF-IDF answer with its source citation visible.

Capture rules:

- Use only the repository's synthetic sample documents.
- Keep the browser near 1440 x 900 and crop consistently.
- Hide API keys, local paths, browser profiles, and personal notifications.
- Keep the local extractive mode caption visible.
- Verify the screenshot against the current release before committing it.
