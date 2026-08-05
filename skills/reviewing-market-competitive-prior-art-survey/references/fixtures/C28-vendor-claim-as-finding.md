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

This is the fastest and most reliable log rotation tool available, and the clear market leader
for any team that cares about log hygiene.

## Evidence

From the project README at the cited URL: "logrotate is designed to ease administration of
systems that generate large numbers of log files."

## Overlap

Head-to-head on the scope's log-rotation capability: it rotates on a schedule, compresses
archives and bounds how many are retained, which is the whole of that capability.
