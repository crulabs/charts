# CruLabs Helm Charts

Helm charts for the CruLabs cluster.

## Charts

| Name           | Description                          |
|----------------|--------------------------------------|
| [cnpg-cluster](./cnpg-cluster)   | CloudNativePG cluster wrapper        |
| [tenant](./tenant)       | Manages Flux CD tenants              |
| [tenant-access](./tenant-access)       | Manages cross-tenant and user RBAC bindings              |
| [vexr](./vexr)         | Prioritizes Trivy vulnerability reports (P1-P4) and alerts via Prometheus |

## Registry

Charts are published as OCI artifacts to `oci://ghcr.io/crulabs/charts/<chart>`, e.g. `oci://ghcr.io/crulabs/charts/cnpg-cluster`.

> `oci://ghcr.io/crulabs/helm/...` is the old location and only holds outdated versions.

## Releasing

Charts are released through **release pull requests**. Tags and GitHub releases are created by the workflows, never by hand.

### How it works

1. **Merge changes to `main`** without touching `version`: your own pull requests and Renovate updates alike. Use [Conventional Commits](https://www.conventionalcommits.org) (`feat:`, `fix:`, `chore:`, `docs:`, ...); the version and the changelog are derived from them.
2. **A release pull request `release/<chart>` opens** for every chart with unreleased changes, titled `chore(<chart>): release <version>`. It is rebuilt from `main` on every push, so it always shows what the next release of the chart contains:
   - `version` in `Chart.yaml`, bumped from the commit types ([SemVer](https://semver.org)): breaking changes (`feat!:`) bump the major version (the minor version before 1.0.0), `feat` the minor version, everything else the patch version.
   - the section `## [<version>]` in `CHANGELOG.md` with the commits since the previous release that touch the chart, grouped by commit type.
3. **Adjust it if needed** by committing to the release branch. Two edits are kept when it is rebuilt:
   - a higher `version` in `Chart.yaml`, e.g. to release a major version
   - notes such as upgrade hints above `<!-- generated:start -->` or below `<!-- generated:end -->`; everything between the markers is overwritten
4. **Merge the release pull request when you want to release.** The chart is published to `oci://ghcr.io/crulabs/charts/<chart>`, tagged as `<chart>-<version>` and gets a GitHub release with the changelog section as release notes. The next change to the chart opens a new release pull request.

### Workflows

| Workflow | Runs on | What it does |
|---|---|---|
| [lint](.github/workflows/lint.yaml) | every pull request | [chart-testing](https://github.com/helm/chart-testing) on the changed charts: `helm lint`, yamllint, `Chart.yaml` schema |
| [release](.github/workflows/release.yaml) | every push to `main` | **release:** lints, packages and pushes every chart whose version has no tag yet, then creates the tag and the GitHub release. **release-pr:** creates, updates or closes the release pull request of every chart |

Released versions are never overwritten: a version that already has a tag is skipped. A release without a changelog section fails before anything is pushed.

The release pull requests are created with the secret `RELEASE_TOKEN` if it is set (GitHub App or fine-grained token with *contents* and *pull requests* write access), otherwise with `GITHUB_TOKEN`. With `GITHUB_TOKEN`, the lint check does not run on them, and *Settings → Actions → General → Allow GitHub Actions to create and approve pull requests* must be enabled.

Consumers' Renovate finds this repository via `home`/`sources` in `Chart.yaml` and shows the release notes in its update pull requests.

### Checking locally

```sh
ct lint --config .github/ct/ct.yaml                # same check as the lint workflow
python3 .github/scripts/release_pr.py <chart> /tmp/body.md   # what the release pull request would change (edits the working tree)
```

## Scope

These Helm charts are purpose-built for the CruLabs Kubernetes cluster.
They are not official upstream charts and are not intended for generic use without adaptation.

## Attribution

Some templates in this repository are derived from upstream Helm charts.
Original projects retain their respective copyrights and licenses.
