# tenant

![Version: 0.3.0](https://img.shields.io/badge/Version-0.3.0-informational?style=flat-square) ![Type: application](https://img.shields.io/badge/Type-application-informational?style=flat-square)

This Helm Chart manages Flux CD tenants in a Kubernetes cluster. Instead of copying namespace, RBAC, quota and network policy manifests for every team, a single HelmRelease per tenant is enough.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Parameters](#parameters)
- [Changelog](#changelog)

## Features

- Creates a **Namespace** per tenant
- Configures **RBAC** (ServiceAccount + RoleBinding)
- Sets **ResourceQuotas** per tenant
- Applies a configurable **CiliumNetworkPolicy**
- Bootstraps **Flux CD** source and Kustomization for the tenant's Git repository

## Installation

The OCIRepository is deployed once globally, each tenant gets its own HelmRelease:

```yaml
# tenants/_helmrepository.yaml
apiVersion: source.toolkit.fluxcd.io/v1
kind: OCIRepository
metadata:
  name: tenant
  namespace: flux-system
spec:
  interval: 24h
  url: oci://ghcr.io/crulabs/helm/tenant
  layerSelector:
    mediaType: "application/vnd.cncf.helm.chart.content.v1.tar+gzip"
    operation: copy
  ref:
    tag: "0.3.0"
```

```yaml
# tenants/team-alpha/helmrelease.yaml
apiVersion: helm.toolkit.fluxcd.io/v2
kind: HelmRelease
metadata:
  name: tenant-team-alpha
  namespace: flux-system
spec:
  interval: 10m
  chartRef:
    kind: OCIRepository
    name: tenant
    namespace: flux-system
  values:
    namespace: team-alpha
    team: team-alpha
    ResourceQuota:
      requests:
        cpu: "4"
        memory: "8Gi"
        storage: "50Gi"
      limits:
        cpu: "8"
        memory: "16Gi"
      pods: "20"
    networkPolicy:
      endpointSelector: {}
      ingress:
        - fromNamespace:
            k8s:io.kubernetes.pod.namespace: gateway-system
      egress: []
    repository:
      kind: GitRepository
      url: https://github.com/my-org/team-alpha
      branch: main
      path: ./deploy
      interval: 10m
```

Adding a new tenant means creating a folder with a HelmRelease, committing it — Flux takes care of the rest.

## Parameters

| Parameter | Description | Default |
|---|---|---|
| `namespace` | Tenant namespace name | `""` |
| `team` | Team label (toolkit.fluxcd.io/tenant) | `""` |
| `ResourceQuota.requests.cpu` | CPU requests quota | `"4"` |
| `ResourceQuota.requests.memory` | Memory requests quota | `"8Gi"` |
| `ResourceQuota.requests.storage` | Storage requests quota | `"50Gi"` |
| `ResourceQuota.limits.cpu` | CPU limits quota | `"8"` |
| `ResourceQuota.limits.memory` | Memory limits quota | `"16Gi"` |
| `ResourceQuota.pods` | Max pods | `"20"` |
| `networkPolicy.endpointSelector` | Label selector for affected pods (empty = all pods) | `{}` |
| `networkPolicy.ingress` | List of ingress rules (fromNamespace labels) | `[]` |
| `networkPolicy.egress` | List of egress rules (toNamespace labels) | `[]` |
| `repository.kind` | Flux source kind (GitRepository, OCIRepository) | `GitRepository` |
| `repository.url` | Git repository URL | `""` |
| `repository.branch` | Git branch | `main` |
| `repository.path` | Kustomization path in repo | `""` |
| `repository.interval` | Sync interval | `"10m"` |


## Changelog
### 0.3.0
- **fix:** added `allow-intra-namespace` CiliumNetworkPolicy to permit pod-to-pod communication within the tenant namespace

### 0.2.1
 - Sync intervall for repository is nur configurable in values.yaml through `repository.interval`

### 0.2.0
- **feat**: Optional `secretRef` for private Git repositories in Flux GitRepository
- **feat**: Optional `extraSubjects` to bind additional ServiceAccounts to the tenant RoleBinding

### 0.1.0
- Initial release
- Namespace, RBAC, ResourceQuota, CiliumNetworkPolicy, Flux source and Kustomization per tenant
- Configurable CiliumNetworkPolicy with endpointSelector, ingress and egress rules
- Default-deny policy — all traffic blocked unless explicitly allowed
