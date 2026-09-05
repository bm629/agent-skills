# TechEmpower round 23 — database access, single-node columnar

*Staged as the SOURCE the extract record was produced from. Five of the reviewing twin's
conditions name "the SOURCE itself" as their first evidence; without it they can only ever record
"unjudgeable", and a reviewer calibrating on this set would never see them run.*

Published 2026-04-01. Harness configuration is published beside every result in this round.

## Configuration

Single node, 16 physical cores, 64 GB RAM, NVMe local storage. Dataset pinned at 240 GB — roughly
four times the host's RAM — and the query set fixed across all engines in the round. Each figure
below is the sustained rate over a ten-minute window after a two-minute warm-up, not a peak.

## Result

> The run sustained 1.2M rows/s on a single 16-core node with 64 GB of RAM.

Scans over the pinned dataset spill to disk once the working set exceeds available RAM, which for
this configuration it does throughout — the 1.2M rows/s figure is the rate *with* spilling, not a
rate that avoids it.

We did not vary concurrency: every figure in this round is single-client. Readers looking for
concurrent-client behaviour should not read these numbers as bearing on it.

## Observations not measured

Several submitters reported memory pressure growing at larger working sets than we tested. We did
not measure this and make no claim about it; it is recorded because it was raised consistently.
