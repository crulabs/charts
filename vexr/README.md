# vexr

![Version: 0.1.2](https://img.shields.io/badge/Version-0.1.2-informational?style=flat-square) ![Type: application](https://img.shields.io/badge/Type-application-informational?style=flat-square) ![AppVersion: 0.1.1](https://img.shields.io/badge/AppVersion-0.1.1-informational?style=flat-square)

This Helm chart deploys [vexr](https://github.com/sfotiadis/vexr), a controller that prioritizes the
VulnerabilityReports of the Trivy Operator into P1 (act now) to P4 (backlog) using CISA KEV, EPSS,
CVE.org records, network exposure (Gateway API, Ingress, Services, Cilium policies) and Hubble flows.
The result is exported as Prometheus metrics with alerts and as `VulnerabilityAssessment` resources.

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Parameters](#parameters)
- [Usage](#usage)
- [Changelog](./CHANGELOG.md)

## Features

- Deploys vexr with a ServiceAccount and a ClusterRole (read-only, except for its own `VulnerabilityAssessment` resources)
- Installs the `VulnerabilityAssessment` CRD (kept on uninstall, updated on upgrade)
- Renders the vexr configuration from `config`, reloaded by vexr without a restart
- Creates a **ServiceMonitor** and a **PrometheusRule** with P1/P2 alerts and operational alerts
- Renders OpenVEX documents from `vexDocuments` into ConfigMaps picked up by vexr
- Optional **CiliumNetworkPolicy** limiting egress to the API server, DNS, the feed FQDNs and Hubble Relay
- Compliant with the Pod Security `restricted` level

## Prerequisites

- Trivy Operator (VulnerabilityReports)
- Prometheus Operator (for `serviceMonitor` and `prometheusRule`)
- Egress to `www.cisa.gov`, `epss.cyentia.com`, `epss.empiricalsecurity.com`, `cveawg.mitre.org` and `api.osv.dev`

## Installation

```yaml
# vexr/ocirepository.yaml
apiVersion: source.toolkit.fluxcd.io/v1
kind: OCIRepository
metadata:
  name: vexr
  namespace: flux-system
spec:
  interval: 24h
  url: oci://ghcr.io/crulabs/charts/vexr
  layerSelector:
    mediaType: "application/vnd.cncf.helm.chart.content.v1.tar+gzip"
    operation: copy
  ref:
    tag: "0.1.x"
```

```yaml
# vexr/helmrelease.yaml
apiVersion: helm.toolkit.fluxcd.io/v2
kind: HelmRelease
metadata:
  name: vexr
  namespace: flux-system
spec:
  interval: 10m
  targetNamespace: vexr
  install:
    createNamespace: true
  chartRef:
    kind: OCIRepository
    name: vexr
    namespace: flux-system
  values:
    config:
      hubble:
        enabled: true
      exposure:
        gateways:
          private:
            - infra/internal
    ciliumNetworkPolicy:
      enabled: true
```

## Parameters

| Parameter | Description | Default |
|---|---|---|
| `image.repository` | Image repository | `ghcr.io/sfotiadis/vexr` |
| `image.tag` | Image tag | `0.1.1` |
| `image.digest` | Image digest, takes precedence over the tag | `""` |
| `image.pullPolicy` | Image pull policy | `IfNotPresent` |
| `imagePullSecrets` | Image pull secrets | `[]` |
| `replicaCount` | Number of replicas, more than one enables leader election | `1` |
| `leaderElection.enabled` | Enable leader election with a single replica | `false` |
| `logLevel` | Log level (`debug`, `info`, `error`) | `info` |
| `extraArgs` | Additional command line arguments | `[]` |
| `extraEnv` | Additional environment variables, e.g. `HTTPS_PROXY` | `[]` |
| `config` | vexr configuration, see [config.example.yaml](https://github.com/sfotiadis/vexr/blob/main/docs/config.example.yaml) | CVE cache file only |
| `restartOnConfigChange` | Restart the pod on configuration changes (only needed for `feeds` and `hubble`) | `false` |
| `cveCache.sizeLimit` | Size limit of the emptyDir holding the CVE.org lookup cache | `64Mi` |
| `vexDocuments` | OpenVEX documents (JSON string or YAML object) by name | `{}` |
| `crds.install` | Install the `VulnerabilityAssessment` CRD | `true` |
| `serviceAccount.create` | Create a ServiceAccount | `true` |
| `serviceAccount.name` | ServiceAccount name | release name |
| `serviceAccount.annotations` | ServiceAccount annotations | `{}` |
| `rbac.create` | Create the ClusterRole and ClusterRoleBinding | `true` |
| `podAnnotations`, `podLabels` | Additional pod metadata | `{}` |
| `podSecurityContext`, `securityContext` | Security contexts | restricted, non-root, read-only root filesystem |
| `resources` | Resources | `50m`/`256Mi` requests, `1Gi` memory limit |
| `priorityClassName`, `nodeSelector`, `tolerations`, `affinity` | Scheduling | empty |
| `service.port` | Metrics service port | `8080` |
| `serviceMonitor.enabled` | Create a ServiceMonitor | `true` |
| `serviceMonitor.honorLabels` | Keep the `namespace` and `container` labels of the metrics (the affected workload) instead of the scrape target's | `true` |
| `serviceMonitor.interval`, `serviceMonitor.scrapeTimeout` | Scrape settings | `60s`, `30s` |
| `serviceMonitor.labels`, `serviceMonitor.metricRelabelings` | Additional labels, metric relabelings | empty |
| `prometheusRule.enabled` | Create a PrometheusRule | `true` |
| `prometheusRule.labels` | Labels of the PrometheusRule (e.g. for the rule selector) | `{}` |
| `prometheusRule.alertLabels` | Labels added to every alert | `{}` |
| `prometheusRule.keepFiringFor` | `keep_firing_for` of the finding alerts | `30m` |
| `prometheusRule.p1.*` | `enabled`, `severity`, `for` of the P1 alert | `true`, `critical`, `0m` |
| `prometheusRule.p2.*` | `enabled`, `severity`, `for` of the P2 alert | `true`, `warning`, `1h` |
| `prometheusRule.p3Backlog.*` | `enabled`, `severity`, `for` of the per-workload P3 alert | `false`, `info`, `24h` |
| `prometheusRule.operational.*` | `enabled`, `severity` of the operational alerts | `true`, `warning` |
| `prometheusRule.additionalRules` | Additional rules in the findings group | `[]` |
| `ciliumNetworkPolicy.enabled` | Create a CiliumNetworkPolicy | `false` |
| `ciliumNetworkPolicy.metricsFrom` | Endpoints allowed to scrape metrics | namespace `monitoring` |
| `ciliumNetworkPolicy.fqdns` | Allowed feed FQDNs (HTTPS) | KEV, EPSS, CVE.org, OSV |
| `ciliumNetworkPolicy.hubbleRelay.*` | Hubble Relay namespace, labels and port | `kube-system`, `k8s-app: hubble-relay`, `4245` |
| `ciliumNetworkPolicy.extraEgress` | Additional egress rules | `[]` |

## Usage

```sh
# prioritized findings per workload
kubectl get vas -A
kubectl get vas -A -l vexr.io/highest=P1
kubectl get vas -n shop replicaset-web-7d9f-nginx -o yaml

# mark a namespace as critical (one priority step more urgent) or as low
kubectl label namespace shop vexr.io/criticality=high
```

Alerts, metrics and the options to silence findings (Alertmanager silences, OpenVEX, exceptions)
are described in [alerting.md](https://github.com/sfotiadis/vexr/blob/main/docs/alerting.md).

The CRD (`files/crd.yaml`) and the ClusterRole rules (`files/clusterrole.yaml`) are generated in the
vexr repository (`make manifests`) and must be copied when they change.
