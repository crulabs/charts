# Changelog

## [3.0.1]

- **fix**: Fixed Flux deployment issue by removing Helm hook annotations from `ImageCatalog` and `ObjectStore` resources.

## [3.0.0]

### Breaking Changes

- **Plugin-based Backup Architecture:** Migrated backups from native `spec.backup.barmanObjectStore` configuration to the `barman-cloud.cloudnative-pg.io` plugin architecture.
- **Plugin-based Backup Architecture:** Migrated backups from native `spec.backup.barmanObjectStore` configuration to the `barman-cloud.cloudnative-pg.io` plugin architecture.
- **Monitoring structure updated:** `monitoring.enablePodMonitor` has been replaced with a nested structure (`monitoring.enabled` and `monitoring.podMonitor.enabled`). Update your values accordingly.
- **`backup` values cleaned up:** Removed `backup.endpointURL`, `backup.destinationPath`, and `backup.obc.storageClassName` from `values.yaml`.
- **ScheduledBackup ownership & method:** Changed `backupOwnerReference` from `cluster` to `self` and updated backup execution to use the Barman plugin method.

### Changes

- **Added Cluster Recovery Support:** Introduced `recovery` values section to support bootstrapping clusters from external backups (`spec.bootstrap.recovery` and `spec.externalClusters`).
- **Helm Hooks for ImageCatalogs:** Added `pre-install`, `pre-upgrade`, and `pre-rollback` Helm hooks (weight `-5`) to `ImageCatalog` manifests to eliminate deployment race conditions with the cluster resource.
- **Configurable Scheduled Backups:** Added `backup.immediate` and `backup.suspend` parameters to control scheduled backup behaviors.
- **Added `backup.obc.endpoint`:** Configured explicit S3 endpoint path for OBC integration.

### Migration

```yaml
# Before (v2.x)
backup:
  enabled: true
  endpointURL: "http://..."
  destinationPath: "s3://..."

monitoring:
  enablePodMonitor: true

# After (v3.0.0)
backup:
  enabled: true
  immediate: false
  suspend: false
  obc:
    name: "<obc-name>"
    endpoint: "[http://rook-ceph-rgw-objectstore.rook-ceph.svc:80](http://rook-ceph-rgw-objectstore.rook-ceph.svc:80)"


# New: Recovery from object Store
recovery:
  enabled: false
  serverName: <old-cluster-name>

monitoring:
  enabled: true
  podMonitor:
    enabled: true
```

## [2.0.1]
- **fix:**: typo in imagecatalog

## [2.0.0]

### Breaking Changes

- **`type` value changed:** `postgres` has been renamed to `postgresql` to align with the CNPG `ImageCatalog` naming. Update your values accordingly.
- **Automatic OBC provisioning removed:** The chart no longer creates an `ObjectBucketClaim` automatically. Deploy the OBC separately and reference it via `backup.obc.name`. See the [Backups](README.md#backups) section for details.
- **`imageName` removed:** The `imageName` value is no longer supported. The chart now always uses an `ImageCatalog` reference via `type` and `version`.
- **Pooler template removed:** The PgBouncer pooler is no longer part of this chart.

### Changes

- `backup.obc.name` added — reference an existing OBC and the chart will read connection details from the provisioned ConfigMap automatically.
- `affinity.enablePodAntiAffinity` now defaults to `true`.
- `postInitApplicationSQL` block is only rendered when there are actual entries.
- `enableSuperuserAccess` block is only rendered when set to `true`.

### Migration

```yaml
# Before
type: postgres
imageName: ghcr.io/cloudnative-pg/postgresql:17.5
backup:
  enabled: true

# After
type: postgresql
version: 17
backup:
  enabled: true
  obc:
    name: <obc-name>  # deploy OBC separately first
```

## [1.1.2]
- **feat:** make resource quota configurable

## [1.1.1]

- **fix**: `postgresUID` and `postgresGID` are now dynamically set based on `.Values.type` to prevent immutability conflicts on existing PostgreSQL clusters. TimescaleDB uses UID/GID 1000, all other types fall back to 26.

## [1.1.0]
- introduce `type` switch between postgres and timescaledb
- add ImageCatalogRef support for TimescaleDB deployments
- refactor postInitApplicationSQL handling to always render a valid array
- ensure CNPG compatibility by preventing null values in SQL configuration
- add automatic TimescaleDB extension injection for timescaledb type
- add shared_preload_libraries configuration for TimescaleDB
- add examples directory reference in README
- remove outdated minimal-with-backup example
- improve test values and introduce version field for major DB selection
- ensure Helm templates are safe for server-side apply (typed validation fixes)

## [1.0.2]
- Fix malformed `printf` call in cluster template causing render error

## [1.0.1]
- Fix OBC and secret name missing `-backups` suffix, causing credential lookup to fail

## [1.0.0]
**BREAKING CHANGE**: secret keys renamed from `ACCESS_KEY_ID`/`ACCESS_SECRET_KEY` to `AWS_ACCESS_KEY_ID`/`AWS_SECRET_ACCESS_KEY`

- Add native Rook/Ceph OBC integration for automatic bucket provisioning
- Auto-resolve `destinationPath` and `endpointURL` from ObjectBucketClaim ConfigMap
- Create OBC only when no custom `destinationPath` is provided
- Default secret name to `<release-name>-backups` when not specified
- Set `backup.enabled` to `false` by default
- Remove hardcoded MinIO endpoint from default values

## [0.4.1]
- Fix for wrong value path

## [0.4.0]
- Add support for `initdb.postInitApplicationSQL` in CNPG cluster chart
- Allow execution of SQL statements for application database after cluster initialization
- README documentation for usage

## [0.3.0]
- Add support for `initdb.postInitSQL` in CNPG cluster chart
- Allow execution of SQL statements after cluster initialization
- README documentation for post-init SQL usage

## [0.2.0]
- **fix**: Set `backupOwnerReference: cluster` in ScheduledBackup to ensure old backup objects are automatically cleaned up according to the retention policy

## [0.1.0]
- Initial release