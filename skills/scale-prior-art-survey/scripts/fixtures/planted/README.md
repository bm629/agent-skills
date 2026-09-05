# Planted fixtures

Each carries EXACTLY ONE defect, and **each gates at exit 0** — a planted defect the validator
catches tests the VALIDATOR, not the reviewer. The rule each plant fires is named in its header,
and every one differs from its clean base in exactly its plant, compared structurally rather than
by eye.

They exist because a fixture that is wrong in two ways proves nothing about either: the second
defect can mask the first, and a check that fires cannot say which one it saw.
