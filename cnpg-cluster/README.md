# cloudnative-pg

![Version: 3.0.1](https://img.shields.io/badge/Version-3.0.1-informational?style=flat-square) ![Type: application](https://img.shields.io/badge/Type-application-informational?style=flat-square)

This cloudnative-pg Helm Chart is a simple wrapper chart to deploy a [CloudNativePG](https://cloudnative-pg.io) cluster in Kubernetes.

## Table of Contents

- [Features](#features)
- [Database Types]()
- [Installation](#installation)
- [Examples](./examples/)
- [Secrets](#secrets)
- [Backups](#backups)
- [Recovery](#recovery)
- [Parameters](#parameters)
- [References](#references)
- [Changelog](./CHANGELOG.md)

## Features

- Deploys a **CloudNativePG cluster**
- PostgreSQL and TimescaleDB-HA support
- Integrated S3 Backups & Disaster Recovery via CloudNativePG Barman Cloud plugin

## Database Types

The chart supports two database types via `type`:

### PostgreSQL

Standard PostgreSQL cluster — the default:

```yaml
type: postgresql
version: 17
```

### TimescaleDB

Deploys a [TimescaleDB](https://www.timescale.com/) cluster using the `timescaledb-ha` image. The `timescaledb` extension is automatically added to `postInitApplicationSQL`:

```yaml
type: timescaledb
version: 18
```

> **Note:** major versions must match an available image in the `ImageCatalog`. 

### Currently available major versions are:

| Image      | Version |
| -- | -- |
| postgresql | 16, 17, 18 |
| timescaledb-ha | 16, 18 |


## Installation

Typically, the chart is deployed in Flux with a HelmRelease inside a namespace:

```yaml
---
apiVersion: source.toolkit.fluxcd.io/v1
kind: OCIRepository
metadata:
  name: cnpg-cluster
  namespace: <namespace>
spec:
  interval: 24h
  url: oci://ghcr.io/crulabs/helm/cnpg-cluster
  layerSelector:
    mediaType: "application/vnd.cncf.helm.chart.content.v1.tar+gzip"
    operation: copy
  ref:
    tag: "3.0.0"
---
apiVersion: helm.toolkit.fluxcd.io/v2
kind: HelmRelease
metadata:
  name: <database-cluster-name>
  namespace: <namespace>
spec:
  interval: 1h
  chartRef:
    kind: OCIRepository
    name: cnpg-cluster
  values:
    # configuration values go here
```

## Secrets

When deploying the chart, the creation of Kubernetes secrets for the **database owner** and optionally for **backups** is needed.

The **owner secret** (for `initdb.owner`) is a standard Kubernetes secret containing the database user credentials (username/password). The name of this secret can be provided via `initdb.secret.name` in `values.yaml`.

When using default values for initdb owner:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: cnpg-app-user
  namespace: <namespace>
type: kubernetes.io/basic-auth
stringData:
  username: app
  password: <app-user-password>
```

## Backups

Backups are configured via S3-compatible object storage. The chart natively integrates with **Rook/Ceph Object Storage** via an `ObjectBucketClaim` (OBC).

### Rook/Ceph Integration

Deploy an OBC in the same namespace as the cluster:


```yaml
apiVersion: objectbucket.io/v1alpha1
kind: ObjectBucketClaim
metadata:
  name: <bucket-claim-name>
  namespace: <namespace>
spec:
  bucketName: postgres-backups
  storageClassName: rook-ceph-bucket
```

Rook/Ceph provisions the bucket and creates a matching ConfigMap and Secret with the same name containing the connection details:

```
ConfigMap: <bucket-claim-name>
  BUCKET_HOST  → RGW service hostname
  BUCKET_NAME  → bucket name
  BUCKET_PORT  → RGW service port

Secret: <bucket-claim-name>
  AWS_ACCESS_KEY_ID     → bucket access key
  AWS_SECRET_ACCESS_KEY → bucket secret key
```

Reference the OBC by name in your values, the chart reads the connection details automatically:

```yaml
backup:
  enabled: true
  obc:
    name: postgres-backup
```

> **Note:** The OBC (ObjectBucketClaim) must be fully provisioned before backups are enabled. If `backup.secret.name` is left empty, the chart defaults to using the `backup.obc.name` secret for authentication credentials.

## Recovery
You can bootstrap a new cluster by restoring from an existing external backup stored in S3.
To enable cluster recovery, configure the `recovery` block:

```yaml
recovery:
  enabled: true
  serverName: "original-cluster-release-name"
  obc:
    name: <bucket-claim-name>
    endpoint: <bucket-host>
```

When `recovery.enabled` is set to `true`:

1. `bootstrap.recovery.source` is set to `origin`.

2. An `externalClusters` entry named `origin` is attached using the `barman-cloud.cloudnative-pg.io` plugin pointing to `serverName`.


## Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `type` | Database type: `postgresql` or `timescaledb` | `postgresql` |
| `version` | Major version (e.g. `17`) | `17` |
| `instances` | Number of cluster instances | `2` |
| `initdb.database` | Default database name | `""` (defaults to release name) |
| `initdb.owner` | Database owner username | `app` |
| `initdb.secret.name` | Secret containing user credentials | `cnpg-app-user` |
| `initdb.postInitSQL` | SQL statements executed as superuser in the `postgres` database after initialization | `[]` |
| `initdb.postInitApplicationSQL` | SQL statements executed as superuser in the application database after initialization | `[]` |
| `enableSuperuserAccess` | Enable superuser access | `false` |
| `superuserSecret.name` | Secret containing superuser credentials | `cnpg-superuser` |
| `storageClass` | StorageClass for PVCs | `local-path` |
| `storage.size` | Volume size | `5Gi` |
| `resources.requests.cpu` | CPU request | `250m` |
| `resources.requests.memory` | Memory request | `256Mi` |
| `resources.limits.cpu` | CPU limit | `1000m` |
| `resources.limits.memory` | Memory limit | `1Gi` |
| `backup.enabled` | Enable continuous WAL archiving and scheduled backups via Barman plugin | `false` |
| `backup.suspend` | Temporarily suspend backup schedules (e.g. for maintenance) | `false` |
| `backup.immediate` | Trigger a backup immediately upon operator reconciliation | `false` |
| `backup.obc.name` | Name of the ObjectBucketClaim for backups | `""` |
| `backup.obc.endpoint` | Endpoint URL for the S3 object store | `http://rook-ceph-rgw-objectstore.rook-ceph.svc:80` |
| `backup.secret.name` | Secret containing `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` | `""` (defaults to OBC name) |
| `backup.schedule` | Cron schedule for physical backups | `0 0 0 * * *` |
| `backup.retentionPolicy` | Backup retention policy | `30d` |
| `recovery.enabled` | Enable bootstrapping the cluster from an external backup | `false` |
| `recovery.serverName` | Name of the original server/cluster in the backup | `""` |
| `recovery.obc.name` | Name of the ObjectBucketClaim holding the backup to recover from | `""` |
| `recovery.obc.endpoint` | Endpoint URL for the recovery S3 object store | `http://rook-ceph-rgw-objectstore.rook-ceph.svc:80` |
| `recovery.secret.name` | Secret containing recovery S3 credentials | `""` (defaults to OBC name) |
| `affinity.enablePodAntiAffinity` | Spread instances across nodes | `true` |
| `affinity.topologyKey` | Topology key for pod anti-affinity | `kubernetes.io/hostname` |
| `monitoring.enabled` | Enable monitoring configuration | `true` |
| `monitoring.podMonitor.enabled` | Create a `PodMonitor` resource for Prometheus Operator scraping | `true` |


## References

- [CloudNativePG Documentation](https://cloudnative-pg.io/documentation/)
- [CloudNativePG Barman Cloud Plugin](https://cloudnative-pg.io/plugin-barman-cloud/docs/intro/)
- [Rook/Ceph Object Storage](https://rook.io/docs/rook/latest/Storage-Configuration/Object-Storage-RGW/object-storage/)
