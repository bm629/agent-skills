# Scope: logscan

A local command-line tool that reads application log files and writes summary reports. It runs on
one machine, reads from disk, writes to disk, and exits. No network, no service, no tenancy.

It reads those files with an embedded columnar engine — **duckdb** today, with **polars**
evaluated and rejected on memory grounds — so those two are the components any capacity question
about this tool is really about.

The datasets it reads are LARGE — routinely tens of gigabytes per run, sometimes more than the
host's RAM — which is the one dimension that makes this project's scale interesting at all.

## Declared classification

Every leaf a survey verdict may be decided on is declared here. A verdict that turns on a value
this block does not carry is a verdict resting on an inference, and the map must record it as an
assumption instead.

```yaml
archetype:
  primary: cli-tool
  secondary: []
domain:
  audience: internal
business:
  platform:
    type: none
integrations:
  expected: false
  complexity: none
data_ml:
  ml_involvement: none
regulatory:
  applies: false
scale:
  concurrency: moderate
  real_time: none
  availability_target: "99"
  geo_distribution: single-region
  data_volume: large
```

`scale.throughput`, `scale.consistency`, `scale.burst_traffic`, `scale.latency_sensitive`,
`scale.stateful` and `security.authz_complexity` are OPTIONAL and are deliberately not set: the
tool is a single-process batch reader and none of them has a value that would mean anything.
