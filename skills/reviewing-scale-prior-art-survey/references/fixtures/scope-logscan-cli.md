# Scope: logscan

A local command-line tool that reads application log files and writes summary reports. It runs on
one machine, reads from disk, writes to disk, and exits. No network, no service, no tenancy.

It reads those files with an embedded columnar engine — **duckdb** today, with **polars**
evaluated and rejected on memory grounds — so those two are the components any capacity question
about this tool is really about.

The datasets it reads are LARGE — routinely tens of gigabytes per run, sometimes more than the
host's RAM — which is the one dimension that makes this project's scale interesting at all.

Declared classification, `scale` block:

- concurrency: moderate
- real_time: none
- availability_target: "99"
- geo_distribution: single-region
- data_volume: large
