# Architecture — GitOps Delivery Platform

```
 Developer
    | git push (app code / Helm values)
    v
+--------------------+        build/test/scan        +------------------+
|  GitHub Actions CI | ----------------------------> |  Container Reg.  |
|  test -> build ->  |        push image             |  (GHCR / ECR)    |
|  Trivy scan ->push |                                +------------------+
+----------+---------+
           | bump image tag in config repo (git commit)
           v
+--------------------+   watches/syncs    +-----------------------------+
|   Config Repo      | <----------------- |   ArgoCD (in-cluster)       |
|  (Helm values)     |  pull-based CD     |   auto-sync + self-heal     |
+--------------------+                    +--------------+--------------+
                                                         | applies manifests
                                                         v
+----------------------------------------------------------------------+
|                       AWS EKS (Terraform-provisioned)                |
|  namespaces: demo-dev / demo-staging / demo-prod                     |
|  Deployment + Service + Ingress(NGINX+cert-manager) + HPA + PDB      |
|  Sealed Secrets (no plaintext secrets in git)                        |
|  Pod identity via IRSA (no static AWS keys)                          |
+-----------------------------+----------------------------------------+
                              | scraped by
                              v
        Prometheus + Grafana + Loki  (kube-prometheus-stack + Loki)
```

## Design decisions
- **Pull-based GitOps (ArgoCD)** over push-based CD: Git is the single source of
  truth, drift self-heals, rollback = `git revert`.
- **CI builds & scans; CD is owned by ArgoCD.** The pipeline never `kubectl apply`s
  to prod directly — it only updates the desired state in git.
- **IRSA** gives pods short-lived AWS credentials via OIDC; no long-lived keys.
- **Sealed Secrets** so the config repo can hold encrypted secrets safely.
- **Immutable image tags** (`sha-<commit>`) make every deploy traceable.
