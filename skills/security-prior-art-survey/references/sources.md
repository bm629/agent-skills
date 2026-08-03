# Research provenance

Method research behind this skill, conducted 2026-08-02 and 2026-08-03 across two retrieval
waves — discovery channels and corpora first, then record formats and standards — each passed
through a content-sanitization guardrail before use. Findings are paraphrased throughout the
skill; no source text is reproduced. Editions and dates are pinned where a claim depends on
them, because several are time-sensitive and will need re-checking.

## Corpora and channels, and what each contributes

| Source | Role in the method | Access | Pinned as of |
|---|---|---|---|
| CWE (MITRE) | weakness vocabulary; entry point to the traversal angle | versioned corpus download, plus a public REST API at `cwe-api.mitre.org` requiring no credentials | 4.20 current; 4.19.1 shipped January 2026 |
| CAPEC (MITRE) | attack-pattern categories and mechanisms; its Likelihood Of Attack field is an ordering signal | versioned XML corpus download | 3.9, effectively static for a long period |
| MITRE ATT&CK | adversary techniques; the far end of the CWE→CAPEC→ATT&CK mapping chain | published corpus | 2026 |
| OWASP ASVS | control requirements at a target rigour level | published standard, CSV among its formats | 5.0.0, May 2025 |
| OWASP Top 10 | risk categories | published list | 2025 edition, released November 2025 — adds Software Supply Chain Failures and Mishandling of Exceptional Conditions, folds SSRF into Broken Access Control |
| OWASP API Security Top 10 | API-specific risk categories | published list | 2023 edition, still current |
| OWASP MASVS / MASWE / MASTG | mobile-client control requirements | published standards | 2026 |
| CVE / NVD | vulnerability records; **corroboration only, not primary** | rate-limited API | enrichment policy narrowed April 2026 |
| OSV (`osv.dev`) | package-level primary; queries by package version or commit | public API; aggregates GitHub Security Advisories, PyPA, RustSec and others under the OSV schema | 2026 |
| GitHub Advisory Database | advisory records in OSV format | public git repository | 2026 |
| CISA KEV | confirmed exploitation in the wild | published catalog | rolling |
| EPSS (FIRST) | probability of exploitation within a 30-day forward window | published scores | rolling |
| Exploit-DB, Metasploit modules, Nuclei templates | public proof-of-concept availability | public archives and repositories | rolling |
| CSAF 2.0 / VEX | first-party vendor advisories, including "not affected" statements | vendor feeds — Microsoft's MSRC CSAF endpoint, AWS security bulletins by RSS, Google Cloud and GKE bulletins | CSAF 2.0 became ISO/IEC 20153 in May 2025 |
| VERIS Community Database | publicly reported incidents in a common schema; base rates and real outcomes | public git repository, one JSON record per incident | 10,000+ records |
| HackerOne Hacktivity and researcher write-ups | feature-level reproduction detail | browse only — **no documented programmatic access**, which is why this is the most fragile channel | 2026 |

## Findings that became rules

**NVD is not a reliable primary.** In April 2026 NIST moved every unenriched CVE published
before March 2026 into a "not scheduled" state and restricted ongoing enrichment to software
used by the US federal government, software designated critical under Executive Order 14028, and
CISA KEV entries, after CVE submissions rose 263% between 2020 and 2025. A record can therefore
exist while its severity and affected-version metadata never arrive. Hence: OSV primary,
NVD corroborating, and a record flagged modified-after-enrichment treated as incomplete.

**Exploitation evidence supersedes exploitation probability.** Published guidance from FIRST and
CISA is that severity scoring sets a floor, EPSS percentile ranks within it, and evidence of
actual exploitation overrides EPSS because EPSS is computed before threat intelligence arrives.
EPSS being an explicit 30-day forward window is why every such signal carries a read date.

**Corpus cadences diverge.** CWE shipping several releases within a year against CAPEC's long
static stretches, plus rolling sources with no release concept at all, produced the stamping rule
and the `release: rolling` allowance.

**Embargo is not absence.** Google publishes cloud and GKE bulletins that say only "security
update" until an embargo lifts, then amend them with the detail — the basis for the
`embargoed-placeholder` cell status.

**Supply-chain attacks are a distinct family no advisory database indexes.** Resolution-order
confusion (named and demonstrated in 2021), name-similarity squatting, and maintainer account
compromise, each with published incidents — a malicious package in a major ML project's nightly
build living on a public index for five days in December 2022; a 2023 campaign registering 900
typosquats across 40 popular packages; a 2021 maintainer compromise affecting a package with
over seven million weekly downloads.

**Record-format conventions were borrowed, not invented.** The OSV schema supplied the
database-qualified identifier form, the integer schema version, RFC3339 UTC timestamps, and the
distinction between an alias for the same item and a pointer to a neighbouring one. Systematic
search-reporting practice (PRISMA-S) supplied the coverage-cell shape: queries as executed,
source, date, and result count, with recorded zeros as proof the search ran.

## Prior-art sweep for an existing skill

A registry sweep across six query variations found nothing covering this gap. Candidates above
the review threshold fell into four groups — code and configuration auditors, guidance
checklists, offensive and penetration-testing skills, and threat-modelling skills that model an
existing system — and every one assumes an artifact already exists, while this survey runs before
any code is written. The strongest adjacent candidate, a supply-chain risk auditor, audits a
dependency tree rather than surveying documented threats. Decision: forge, using those candidates
as source material.
