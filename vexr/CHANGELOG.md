# Changelog

## [0.1.1]

- **fix:** the ServiceMonitor sets `honorLabels: true` (`serviceMonitor.honorLabels`). Before, Prometheus
  replaced the `namespace` and `container` labels of the findings with those of vexr itself
  (`exported_namespace`), so alerts showed the wrong namespace and could not be grouped by it.

## [0.1.0]

- Initial release
- Deployment, ServiceAccount, ClusterRole and the `VulnerabilityAssessment` CRD
- vexr configuration via `config`, OpenVEX documents via `vexDocuments`
- ServiceMonitor and PrometheusRule with P1/P2 alerts, optional P3 backlog and operational alerts
  (including unscanned workloads and unexpected internet traffic)
- Optional CiliumNetworkPolicy

<!-- generated:start -->
### Features

- add vexr chart
<!-- generated:end -->
