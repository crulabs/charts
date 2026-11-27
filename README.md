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

A chart is released when its `version` in `Chart.yaml` changes on `main`. Tags and GitHub releases are created by the workflows, never by hand.

### Step by step

1. **Branch and change the chart.** Use [Conventional Commits](https://www.conventionalcommits.org) (`feat:`, `fix:`, `chore:`, `docs:`, ...); the changelog is generated from them.
2. **Bump `version`** in `<chart>/Chart.yaml` ([SemVer](https://semver.org)):
   - patch: fixes and image updates
   - minor: new features
   - major: breaking changes
3. **Open a pull request.** Two checks run:
   - **lint**: lints the changed charts and fails if a changed chart has no new version.
   - **changelog**: adds the section `## [<version>]` to `<chart>/CHANGELOG.md` and commits it to your branch. **Run `git pull` before you push again.**
4. **Review the changelog section** in the pull request. Add notes such as upgrade hints above the `<!-- generated:start -->` marker; they are kept on every regeneration. Everything between the markers is overwritten.
5. **Merge to `main`.** The chart is published to `oci://ghcr.io/crulabs/charts/<chart>`, tagged as `<chart>-<version>` and gets a GitHub release with the changelog section as release notes.

### Releasing Renovate updates

Renovate updates images in the charts but does not bump chart versions, so its pull requests do not release anything. Merge them, then release as described above: the changelog lists the updates under *Dependencies*.

### Workflows

| Workflow | Runs on | What it does |
|---|---|---|
| [lint](.github/workflows/lint.yaml) | every pull request | [chart-testing](https://github.com/helm/chart-testing) on the changed charts: `helm lint`, yamllint, `Chart.yaml` schema and version bump (the version check is skipped for Renovate) |
| [changelog](.github/workflows/changelog.yaml) | pull requests that bump a `Chart.yaml` version (not from bots) | Generates the changelog section from the commits since the previous release that touch the chart, including commits merged to `main` in the meantime, grouped by commit type |
| [release](.github/workflows/release.yaml) | push to `main` that changes a `Chart.yaml` | Lints, packages and pushes every chart whose version has no tag yet, then creates the tag and the GitHub release |

Released versions are never overwritten: a version that already has a tag is skipped. A release without a changelog section fails before anything is pushed.

Consumers' Renovate finds this repository via `home`/`sources` in `Chart.yaml` and shows the release notes in its update pull requests.

### Checking locally

```sh
ct lint --config .github/ct/ct.yaml                # same check as the lint workflow
python3 .github/scripts/changelog.py <chart> <version> origin/main   # preview the changelog section
```

## Scope

These Helm charts are purpose-built for the CruLabs Kubernetes cluster.
They are not official upstream charts and are not intended for generic use without adaptation.

## Attribution

Some templates in this repository are derived from upstream Helm charts.
Original projects retain their respective copyrights and licenses.
