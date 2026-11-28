# Changelog

## [0.5.1]

<!-- generated:start -->
### Documentation

- move tenant and tenant-access changelogs to CHANGELOG.md
- fix registry path and document release process

### Chores

- add home and sources to chart metadata
<!-- generated:end -->

## [0.5.0]

- **feat:** Pod Security Admission labels on the tenant namespace via `podSecurity` (default: enforce `baseline`, warn/audit `restricted`). Running pods are not affected. New pods that violate `baseline` are rejected.

## [0.4.0]

- **feat:** added decryption block

## [0.3.1]

- **fix:** render networkpolicy only if ingress or egress is configured

## [0.3.0]

- **fix:** added `allow-intra-namespace` CiliumNetworkPolicy to permit pod-to-pod communication within the tenant namespace

## [0.2.1]

 - Sync intervall for repository is nur configurable in values.yaml through `repository.interval`

## [0.2.0]

- **feat**: Optional `secretRef` for private Git repositories in Flux GitRepository
- **feat**: Optional `extraSubjects` to bind additional ServiceAccounts to the tenant RoleBinding

## [0.1.0]

- Initial release
- Namespace, RBAC, ResourceQuota, CiliumNetworkPolicy, Flux source and Kustomization per tenant
- Configurable CiliumNetworkPolicy with endpointSelector, ingress and egress rules
- Default-deny policy — all traffic blocked unless explicitly allowed
