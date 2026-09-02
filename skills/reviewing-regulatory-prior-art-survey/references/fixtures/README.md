# Clean calibration artifacts

The two artifacts a correct run produces. They are the bar, and they are here so a reviewer can
calibrate against a passing example rather than inferring one from the conditions.

**Only the clean ones live here.** The PLANTED fixtures — artifacts that pass the deterministic
gate at exit 0 and are nonetheless wrong — stay in the producer package, so a blind reviewer handed
this skill cannot read the answer key.

**Read the clean artifacts as carefully as a suspect one.** Measured across two sibling builds, the
reviews found more defects in the CLEAN fixture than in the planted ones — because nothing in the
method had ever pointed a reviewer at the artifact both halves calibrate on. A defect here teaches
itself to every producer and every reviewer that reads it.
