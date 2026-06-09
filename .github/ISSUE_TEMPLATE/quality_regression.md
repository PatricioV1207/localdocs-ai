---
name: Quality regression
about: Report a grounded-answer, summary, source, or study-output regression
title: "[Quality]: "
labels: quality
assignees: ""
---

## Output area

- [ ] Cited Q&A
- [ ] Summary
- [ ] Study question
- [ ] Flashcard
- [ ] Source selection or cleaning

## What went wrong?

Describe the unsupported, noisy, malformed, or missing output.

## Safe reproduction

Provide the smallest synthetic text that reproduces the problem. Do not paste
private document content.

## Expected behavior

What should LocalDocs AI return, reject, or cite?

## Actual behavior

Include the output and source labels, with sensitive paths removed.

## Environment

- OS:
- Python version:
- LocalDocs AI version or branch:
- OpenAI mode: disabled / enabled

## Suggested fixture

Which required terms, forbidden terms, and citation chunks should a
deterministic quality fixture assert?
