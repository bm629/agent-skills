# WEB-techempower-run-3

## System under load
A single-node analytical query engine reading a columnar dataset larger than the host's RAM, run
by the TechEmpower harness on 16 cores and 64 GB.

## Episodes
Episode 1 records the sustained scan rate at the stated working-set size. Episode 2 records the
authors' narrative account of memory pressure beyond it, which they did not measure.

## Method and configuration
The figure is the sustained rate over a ten-minute window after a two-minute warm-up, not a peak.
It was taken on a single node of 16 physical cores and 64 GB of RAM with NVMe local storage, over
a dataset pinned at 240 GB — roughly four times host memory — with the query set fixed across
every engine in the round. Scans spill to disk throughout at that ratio, so 1.2M rows/s is the
rate WITH spilling rather than one that avoids it. The harness publishes dataset, node shape and
query set beside every result, which is why episode 1 carries `configuration_stated: true`;
episode 2 is the authors' unmeasured aside and does not.

## Transferability
Measured on comparable single-node hardware, and the bands can be compared. The source ran at 240
GB against 64 GB of RAM, about four times host memory; this project declares a `data_volume` of `large`
and describes datasets of tens of gigabytes per run that sometimes exceed the host's RAM, so both
sit in the spill-dominated regime and the pattern carries. What does not carry is the exact ratio
— the project states a band, not a number, so its distance from the measured 4x is unknown — and
the concurrency band does not carry at all: the source says every figure in the round is
single-client, while this project's scope declares `moderate`.
