<!-- AUTO-GENERATED from canonical source: way-of-working.md — DO NOT EDIT -->
<!-- To update, edit the canonical source and run: python scripts/docs/generate-router-files.py -->

### Mandatory publication protocol (blocking)

Blocking execution sequence:

1. Publish the review as a Pull Request comment.
2. Return the published PR comment URL.
3. When remediation commits are pushed, publish a follow-up PR comment.
4. Return the follow-up PR comment URL.

A review is blocking until the PR comment URL is returned to the user.

- A follow-up PR comment is required after remediation commits.
<!-- markdownlint-disable-next-line MD013 -->
- This follow-up must be published automatically as part of the remediation workflow (do not wait for a separate user prompt).

- The review MUST be published as a Pull Request comment.
- A review is not complete until the Pull Request comment is posted and the URL is returned.
- **Follow-up verification (hard rule).** When commits address review findings, the agent MUST post a follow-up Pull
  Request comment confirming which findings are resolved, which remain open, and which introduced new concerns. A review
  cycle is not closed until this follow-up comment is posted.
