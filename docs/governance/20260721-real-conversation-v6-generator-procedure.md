# VEIL v6 blind frame-generation procedure

v6 is a new evaluation design after the preserved v5 no-frame result. It does
not rerun or repair v5.

The generator receives only fresh frozen runtime input and
`veil_decision_frames.py`. Before emitting a payload, it must examine each
source sentence for an explicit definition, adoption, rename, conflict,
required property, allowed-use limit, prohibition, or state-transition rule.
For every such independent primary lexical target, it emits one exact-evidence
frame and then has its critic classify every emitted frame. It must not emit an
empty payload merely because terminology is unfamiliar or mixed-language. An
empty payload is valid only after the generator explicitly determines that no
such decision appears in the supplied source text.

This is a generation-procedure clarification, not a local phrase rule: local
VEIL still validates exact evidence and remains the sole outcome policy and
write authority.
