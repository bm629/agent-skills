---
schema_version: 1
meta:
  item_id: logrotate
  as_of: '2026-08-05'
  revision: 1
outcome: extracted
product:
  id: logrotate
  name: logrotate
  url: https://github.com/logrotate/logrotate
  tier: direct
  overlapping_capabilities:
    - log-rotation
  category: system log management
  positioning: >
    The project describes itself as designed to ease administration of systems that generate
    large numbers of log files, rotating, compressing and mailing them on a schedule.
  source_authority: first-party
  lifecycle:
    status: live
  pricing:
    model: free
    as_of: '2026-08-05'
  capability_tags:
    - log-rotation
notes:
  - Packaged by every major distribution; adoption signal deferred to a registry angle.
---

## Positioning

The project positions itself as the standard administrative tool for rotating, compressing and
mailing system log files on a schedule.

## Evidence

From the project README at the cited URL: "logrotate is designed to ease administration of
systems that generate large numbers of log files."

## Overlap

Everyone in the ops space knows this tool, so it is plainly a direct competitor for anything
touching logs.
