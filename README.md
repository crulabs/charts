# CruLabs Helm Charts

Helm charts for the CruLabs cluster.

## Charts

| Name           | Description                          |
|----------------|--------------------------------------|
| [cnpg-cluster](./cnpg-cluster)   | CloudNativePG cluster wrapper        |
| [tenant](./tenant)       | Manages Flux CD tenants              |
| [tenant-access](./tenant-access)       | Manages cross-tenant and user RBAC bindings              |

## Registry

Charts are published as OCI artifacts to `oci://ghcr.io/crulabs/charts/<chart>`, e.g. `oci://ghcr.io/crulabs/charts/cnpg-cluster`.

> `oci://ghcr.io/crulabs/helm/...` is the old location and only holds outdated versions.

## Releasing

A chart is released when its `version` in `Chart.yaml` changes on `main`:

1. Make your changes to the chart.
2. Bump `version` in `<chart>/Chart.yaml` ([SemVer](https://semver.org): patch for fixes and image updates, minor for new features, major for breaking changes).
3. Add an entry to the chart's changelog.
4. Merge to `main`.

The [release workflow](.github/workflows/release.yaml) then lints, packages and pushes every chart whose version is not released yet and creates the git tag `<chart>-<version>`. Do not create release tags by hand.

Released versions are never overwritten. A version that already has a git tag is skipped, so every change needs a new version.

Renovate updates images in the charts but does not bump the chart version. To release such an update, bump the version as described above.

## Scope

These Helm charts are purpose-built for the CruLabs Kubernetes cluster.
They are not official upstream charts and are not intended for generic use without adaptation.

## Attribution

Some templates in this repository are derived from upstream Helm charts.
Original projects retain their respective copyrights and licenses.
