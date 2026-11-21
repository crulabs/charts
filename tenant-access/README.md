# tenant-access

![Version: 0.1.4](https://img.shields.io/badge/Version-0.1.4-informational?style=flat-square) ![Type: application](https://img.shields.io/badge/Type-application-informational?style=flat-square)

This Helm Chart manages tenant access in a Kubernetes cluster. It creates ServiceAccounts per user, RoleBindings in the appropriate tenant namespaces based on team membership, and automatically generates kubeconfig files stored as Secrets.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Parameters](#parameters)
- [Usage](#usage)
- [Changelog](#changelog)

## Features

- Creates a **ServiceAccount** and **Token Secret** per user in a central `tenant-access` namespace
- Creates **RoleBindings** in all tenant namespaces based on team membership
- Automatically generates a **kubeconfig** per user after each install/upgrade via a post-hook Job
- Kubeconfigs are stored as **Secrets** and can be retrieved at any time
- Adding a user to a new team or adding a namespace to a team automatically updates RoleBindings on the next reconcile — no kubeconfig update needed

## Installation

```yaml
# tenant-access/ocirepository.yaml
apiVersion: source.toolkit.fluxcd.io/v1
kind: OCIRepository
metadata:
  name: tenant-access
  namespace: flux-system
spec:
  interval: 24h
  url: oci://ghcr.io/crulabs/charts/tenant-access
  layerSelector:
    mediaType: "application/vnd.cncf.helm.chart.content.v1.tar+gzip"
    operation: copy
  ref:
    tag: "0.1.x"
```

```yaml
# tenant-access/helmrelease.yaml
apiVersion: helm.toolkit.fluxcd.io/v2
kind: HelmRelease
metadata:
  name: tenant-access
  namespace: flux-system
spec:
  interval: 10m
  chartRef:
    kind: OCIRepository
    name: tenant-access
    namespace: flux-system
  values:
    apiServer: "https://k8s.example.io:6443"

    teams:
      - name: team-a
        namespaces:
          - team-a-dev
          - team-a-staging
      - name: team-b
        namespaces:
          - team-b-dev

    users:
      - name: user-a
        teams:
          - team-a
          - team-b
      - name: user-b
        teams:
          - team-a
```

## Parameters

| Parameter | Description | Default |
|---|---|---|
| `apiServer` | API server address with port | `https://k8s.example.io:6443` |
| `teams` | List of teams with their namespaces | `[]` |
| `teams[].name` | Team name | `""` |
| `teams[].namespaces` | List of namespaces this team has access to | `[]` |
| `users` | List of users | `[]` |
| `users[].name` | Username (used for ServiceAccount and Secret name) | `""` |
| `users[].teams` | List of team names this user belongs to | `[]` |

## Usage

### Retrieving a kubeconfig

After the chart is installed or upgraded, each user's kubeconfig is stored as a Secret:

```bash
kubectl get secret user-a-kubeconfig -n tenant-access \
  -o jsonpath='{.data.kubeconfig}' | base64 -d > ~/.kube/config
```

### Using the kubeconfig

The kubeconfig contains a single context without a default namespace. Always specify the namespace explicitly:

```bash
kubectl -n team-a-dev get pods
kubectl -n team-b-dev get deployments
```

### Adding a new namespace to a team

Add the namespace to `teams[].namespaces` in the values and commit. Flux reconciles the chart, new RoleBindings are created automatically. No kubeconfig update needed.

### Adding a new user

Add the user to `users` in the values and commit. Flux reconciles the chart, the ServiceAccount, Token Secret and kubeconfig Secret are created automatically. The user retrieves their kubeconfig once:

```bash
kubectl get secret <username>-kubeconfig -n tenant-access \
  -o jsonpath='{.data.kubeconfig}' | base64 -d > ~/.kube/config
```

### Removing a user

Remove the user from `users` in the values and commit. Flux reconciles the chart and removes the ServiceAccount, Token Secret, kubeconfig Secret and all RoleBinding subjects for that user.

## Changelog
### 0.1.5
- **security:** updated kubeconfig generator image to `alpine/k8s:1.37.2`

### 0.1.4
- configure API server in values.yaml via `apiServer`

### 0.1.3
- **fix:** `namespace` field in `tenant-users-config` ConfigMap was empty because it referenced `Values.namespace` which no longer exists, now replaced with `Release.Namespace`

### 0.1.2
- **fix:** replaced `registry.k8s.io/kubectl` distroless image with `alpine/k8s:1.35.0` in the kubeconfig generator hook job

### 0.1.1
- **fix:** use `/bin/sh` instead of `/bin/bash` in kubeconfig generator script

### 0.1.0
- Initial release
- Central namespace (the release namespace) for all ServiceAccounts
- Token Secrets per user (kubernetes.io/service-account-token)
- RoleBindings per team namespace, filtered by user team membership
- Post-install/post-upgrade hook Job generating kubeconfig Secrets per user
