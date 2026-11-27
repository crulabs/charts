# Changelog

## [0.1.5]

- **security:** updated kubeconfig generator image to `alpine/k8s:1.37.2`

## [0.1.4]

- configure API server in values.yaml via `apiServer`

## [0.1.3]

- **fix:** `namespace` field in `tenant-users-config` ConfigMap was empty because it referenced `Values.namespace` which no longer exists, now replaced with `Release.Namespace`

## [0.1.2]

- **fix:** replaced `registry.k8s.io/kubectl` distroless image with `alpine/k8s:1.35.0` in the kubeconfig generator hook job

## [0.1.1]

- **fix:** use `/bin/sh` instead of `/bin/bash` in kubeconfig generator script

## [0.1.0]

- Initial release
- Central namespace (the release namespace) for all ServiceAccounts
- Token Secrets per user (kubernetes.io/service-account-token)
- RoleBindings per team namespace, filtered by user team membership
- Post-install/post-upgrade hook Job generating kubeconfig Secrets per user
