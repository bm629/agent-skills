# Angle a1m — mobile control standards

**Precondition:** the product ships a mobile client, **or the scope does not say**. Silence
routes this angle to run, per the absent-input policy — an unstated mobile posture is not a
negative answer, and treating it as one drops an entire control family invisibly.

**Mechanism.** The same corpus walk as the general control angle, against the mobile-specific
verification standard, its weakness enumeration, and its testing guide.

**Sources:** `owasp-masvs`, `owasp-maswe`, `owasp-mastg`.

**Applicable group types:** `control`, `weakness`.

**Cap:** 40 items. **Ordering signal:** category relevance to a surface the map names.

## Query strategy

1. Walk the mobile standard's categories — storage, cryptography, authentication, network
   communication, platform interaction, code quality, resilience — selecting those matching a
   group's canonical term or an expansion.
2. Take the requirements in each selected category, version-pinned as `control-requirement`
   candidates.
3. Cross-reference the mobile weakness enumeration for the weakness classes those requirements
   defend against, and record those against `weakness` groups.
4. The testing guide supplies test procedures rather than requirements; use it to sharpen a
   requirement's relevance line, not as a candidate source.

## Unique coverage

Mobile-client controls that the general verification standard does not carry — platform
interaction, local storage on an untrusted device, and client-side resilience. A product with a
mobile client whose survey skipped this angle has no coverage of the device half of its attack
surface, and nothing downstream would reveal the omission.

## Failure modes specific to this angle

- **Routing to not-run on silence.** The commonest and most damaging. If the scope does not say
  whether a mobile client exists, this angle runs and the map records the assumption. Only an
  explicit "no mobile client" is a not-run cause.
- **Treating mobile controls as a subset of the general standard.** They are not; the overlap is
  partial and the mobile-specific categories have no general-standard equivalent.

## Sanitization

As for the general control angle: fetched documents pass through a
**content-sanitization guardrail** before use, with the result recorded per source.

## Fallbacks

The project repositories, then a prior pinned release. Where the weakness enumeration is
unavailable, the verification standard's own weakness references carry enough to proceed —
record the degradation as a `partial` cell rather than working around it silently.
