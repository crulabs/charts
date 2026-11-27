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
3. Open a pull request. The [changelog workflow](.github/workflows/changelog.yaml) adds the section `## [<version>]` to `<chart>/CHANGELOG.md` and commits it to your branch. It lists the commits since the previous release that touch the chart, grouped by [Conventional Commits](https://www.conventionalcommits.org) type. Pull before you push again.
4. Optionally add notes such as upgrade hints to the section, above the `<!-- generated:start -->` marker. They are kept when the list is regenerated on the next push; everything between the markers is overwritten.
5. Merge to `main`.

The changelog section becomes the release notes; a release without one fails.

The [release workflow](.github/workflows/release.yaml) then lints, packages and pushes every chart whose version is not released yet, creates the git tag `<chart>-<version>` and a GitHub release with the changelog section as release notes. Do not create release tags or releases by hand.

Renovate in consuming repositories finds this repository via `home`/`sources` in `Chart.yaml` and shows the release notes in its update PRs.

Released versions are never overwritten. A version that already has a git tag is skipped, so every change needs a new version.

Renovate updates images in the charts but does not bump the chart version. To release such an update, bump the version as described above.

## Scope

These Helm charts are purpose-built for the CruLabs Kubernetes cluster.
They are not official upstream charts and are not intended for generic use without adaptation.

## Attribution

Some templates in this repository are derived from upstream Helm charts.
Original projects retain their respective copyrights and licenses.
