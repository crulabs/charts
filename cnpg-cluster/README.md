# cloudnative-pg

![Version: 2.0.0](https://img.shields.io/badge/Version-2.0.0-informational?style=flat-square) ![Type: application](https://img.shields.io/badge/Type-application-informational?style=flat-square)

This cloudnative-pg Helm Chart is a simple wrapper chart to deploy a [CloudNativePG](https://cloudnative-pg.io) cluster in Kubernetes.

## Table of Contents

- [Features](#features)
- [Database Types]()
- [Installation](#installation)
- [Examples](./examples/)
- [Secrets](#secrets)
- [Backups](#backups)
- [Parameters](#parameters)
- [Roadmap](#roadmap)
- [References](#references)
- [Changelog](./CHANGELOG.md)

## Features

- Deploys a **CloudNativePG cluster** via Helm
- PostgreSQL and TimescaleDB-HA support
- Easy configuration through values

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
    tag: "2.0.0"
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
  name: postgres-backups
  namespace: <namespace>
spec:
  generateBucketName: postgres-backups
  storageClassName: rook-ceph-bucket
```

Rook/Ceph provisions the bucket and creates a matching ConfigMap and Secret with the same name containing the connection details:

```
ConfigMap: <release-name>-backups
  BUCKET_HOST  → RGW service hostname
  BUCKET_NAME  → auto-generated bucket name
  BUCKET_PORT  → RGW service port

Secret: <release-name>-backups
  AWS_ACCESS_KEY_ID     → bucket access key
  AWS_SECRET_ACCESS_KEY → bucket secret key
```

Reference the OBC by name in your values, the chart reads the connection details automatically:

```yaml
backup:
  enabled: true
  obc:
    name: postgres-backup
  retentionPolicy: "30d"
  schedule: "0 0 0 * * *"
```

> **Note:** The OBC (ObjectBucketClaim) must be fully provisioned before backups are enabled.

### Custom S3 Endpoint

If you want to use a different S3-compatible backend, you can override `destinationPath` and `endpointURL` manually, and provide your own credentials secret:

```yaml
backup:
  enabled: true
  destinationPath: "s3://<bucket-name>/"
  endpointURL: "https://<s3-endpoint>"
  secret:
    name: <backup-credentials-secret>
  retentionPolicy: "30d"
  schedule: "0 0 0 * * *"
```

The secret must contain the keys `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: <backup-credentials-secret>
  namespace: <namespace>
type: Opaque
stringData:
  AWS_ACCESS_KEY_ID: <access-key-id>
  AWS_SECRET_ACCESS_KEY: <access-secret-key>
```

## Parameters

| Parameter | Description | Default |
|---|---|---|
| `type` | Database type: `postgresql` or `timescaledb` | `postgresql` |
| `version` | Major version (e.g. `17`) | `17` |
| `instances` | Number of cluster instances | `2` |
| `initdb.database` | Default database name | `""` defaults to release name |
| `initdb.owner` | Database owner | `app` |
| `initdb.secret.name` | Secret containing user credentials | `cnpg-app-user` |
| `initdb.postInitSQL` | SQL statements executed as superuser in the `postgres` database after initialization | `[]` |
| `initdb.postInitApplicationSQL` | SQL statements executed as superuser in the app database after initialization | `[]` |
| `enableSuperuserAccess` | Enable superuser access | `false` |
| `superuserSecret.name` | Secret containing superuser credentials | `cnpg-superuser` |
| `storageClass` | StorageClass for PVCs | `local-path` |
| `storage.size` | Volume size | `5Gi` |
| `resources.requests.cpu` | CPU request | `250m` |
| `resources.requests.memory` | Memory request | `256Mi` |
| `resources.limits.cpu` | CPU limit | `1000m` |
| `resources.limits.memory` | Memory limit | `1Gi` |
| `backup.enabled` | Enable backups | `false` |
| `backup.obc.name` | Name of an existing OBC — connection details are resolved automatically | `""` |
| `backup.obc.storageClassName` | StorageClass used by the OBC | `rook-ceph-bucket` |
| `backup.destinationPath` | S3 destination path, used when not using an OBC | `""` |
| `backup.endpointURL` | S3 endpoint URL, used when not using an OBC | `""` |
| `backup.secret.name` | Secret containing backup credentials, defaults to OBC name | `""` |
| `backup.schedule` | Cron schedule for backups | `0 0 0 * * *` |
| `backup.retentionPolicy` | Backup retention policy | `30d` |
| `affinity.enablePodAntiAffinity` | Spread instances across nodes | `true` |
| `affinity.topologyKey` | Topology key for pod anti-affinity | `kubernetes.io/hostname` |
| `monitoring.enablePodMonitor` | Enable PodMonitor CR for Prometheus | `true` |

## Roadmap

- Restore from backup

## References

- [CloudNativePG Documentation](https://cloudnative-pg.io/documentation/)
- [Rook/Ceph Object Storage](https://rook.io/docs/rook/latest/Storage-Configuration/Object-Storage-RGW/object-storage/)
