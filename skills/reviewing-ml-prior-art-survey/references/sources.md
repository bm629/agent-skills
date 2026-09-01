# Sources

This skill reads no external sources. Its inputs are the artifact under review, the wave-0
vocabulary map, and the producer package's schemas, source registry and angle references.

That is deliberate. A reviewer that fetches the corpus itself starts producing its own evidence,
and then it is a second producer with no reviewer — which is the failure the two-part gate exists
to avoid.

Three of the five inputs live in the PRODUCER package, which is often not installed beside this
one. When a condition names evidence you cannot reach, say so and emit no verdict on that
condition. Deriving an angle's source list from the artifact under review is circular: an artifact
that omits a source omits it from any list you read off it.
