# WEB-techempower-run-3

## System under load
A single-node analytical query engine reading a columnar dataset larger than the host's RAM, run
by the TechEmpower harness on 16 cores and 64 GB.

## Episodes
Episode 1 records the sustained scan rate at the stated working-set size. Episode 2 records the
authors' narrative account of memory pressure beyond it, which they did not measure.

## Method and configuration
The harness pins the dataset, the node shape and the query set, and publishes all three beside
each result — which is why episode 1 carries `configuration_stated: true` and episode 2 does not.

## Transferability
Measured on comparable single-node hardware. This project has not stated its working-set size, so
the band it was measured at cannot yet be compared to the project's own.
