# VEIL real-conversation v2 corpus contract

v1 first-run evidence is preserved as failed but is not implementation-quality
evidence: its reviewers used `registered_terms` as a list of interesting words,
not a read-only canonical-DB fact, and allowed duplicate concept labels.

For v2:

1. Capture a read-only canonical snapshot before corpus authoring. A row may
   contain a `registered_terms` value only when that exact normalized term is
   present in that snapshot. Every other row uses `[]`.
2. A reviewer must select one natural, complete term for one concept in one
   context. A substring, identifier fragment, or duplicate concept is invalid.
3. Within a session, the same normalized term may occur only once unless the
   reviewer records a distinct source context and explains why the concepts are
   separate. Conflicting outcomes for the same concept become one `exception`.
4. Reviewer A must validate all rows against the anonymized source and the
   canonical snapshot before handing off; Reviewer B repeats both checks.
5. v2 source excerpts must be newly selected from the approved window and must
   not reuse a v1 source excerpt. The host AI must not see v2 labels before its
   freeze.

No DB write, Git change, install, sync, or remote operation is authorized.
