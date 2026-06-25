# Cloud-Native GitOps Delivery Platform
# by Vaishali Saini . https://github.com/vaishalisaini-tech

A production-shaped delivery platform where **every change flows through Git**: code is
tested, built, scanned, and pushed by CI, then deployed to **Kubernetes via GitOps
(ArgoCD)** across `dev` / `staging` / `prod` — with self-healing and one-commit rollback.

> Built to demonstrate end-to-end DevOps/Platform engineering: IaC, containers, CI/CD,
> GitOps, observability, and security best practices.

---

## Stack

| Concern | Tool |
|---|---|
| App | FastAPI (Python) |
| Container | Docker (multi-stage, non-root, healthcheck) |
| Infra as Code | Terraform (VPC, EKS, ECR, IRSA) |
| Packaging | Helm (per-environment values) |
| CI | GitHub Actions (test → build → Trivy scan → push → bump tag) |
| CD | ArgoCD (pull-based GitOps, auto-sync + self-heal) |
| Observability | Prometheus, Grafana, Loki |
| Security | Trivy scan gate, IRSA, Sealed Secrets, non-root, least-priv RBAC |
| Cloud | AWS (region: `ap-northeast-2` / Seoul) |

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for the diagram and design rationale.

---

## Repository layout

```
gitops-platform/
├── app/                  # FastAPI service + Dockerfile + tests
├── infra/terraform/      # VPC, EKS, ECR, IRSA  (Terraform)
├── charts/app/           # Helm chart + values-{dev,staging,prod}.yaml
├── argocd/               # AppProject + Application manifests (one per env)
├── observability/        # Prometheus rules, Grafana dashboard, Loki values
├── .github/workflows/    # CI pipeline
└── docs/                 # Architecture + runbook
```

---

## Run it locally (no cloud needed — good first screenshot)

```bash
# 1. Run the app
cd app
pip install -r requirements.txt
uvicorn app.src.main:app --reload --port 8000   # run from repo root, or adjust path
# visit http://localhost:8000/  and  /metrics  and  /healthz

# 2. Run the tests
python -m pytest app/tests -q

# 3. Build the container
docker build -t gitops-demo:local ./app
docker run -p 8000:8000 gitops-demo:local
```

You can demonstrate the **whole GitOps flow locally for free** using `kind`
(Kubernetes-in-Docker) + ArgoCD — no AWS bill. See the "Local Kubernetes" section below.

---

## Deploy to AWS (the full version)

> ⚠️ This creates billable AWS resources (EKS + NAT gateway). Tear down with
> `terraform destroy` when done. For a portfolio, the **local kind path is enough**
> for screenshots; do the AWS path once if you want real cloud experience.

```bash
# 1. Provision infra
cd infra/terraform
cp terraform.tfvars.example terraform.tfvars     # edit if needed
terraform init
terraform apply

# 2. Connect kubectl
$(terraform output -raw configure_kubectl)

# 3. Install platform add-ons
helm repo add argo https://argoproj.github.io/argo-helm
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add grafana https://grafana.github.io/helm-charts

kubectl create namespace argocd
helm install argocd argo/argo-cd -n argocd
kubectl create namespace monitoring
helm install kube-prometheus-stack prometheus-community/kube-prometheus-stack -n monitoring
helm install loki grafana/loki -f ../../observability/loki-values.yaml -n monitoring

# 4. Register the apps with ArgoCD (edit repoURL to your fork first!)
kubectl apply -f ../../argocd/project.yaml
kubectl apply -f ../../argocd/application-dev.yaml
```

---

## Local Kubernetes (free, recommended for the portfolio)

```bash
kind create cluster --name gitops
kubectl create namespace argocd
helm repo add argo https://argoproj.github.io/argo-helm && helm repo update
helm install argocd argo/argo-cd -n argocd

# point ArgoCD at your fork, then watch it sync:
kubectl apply -f argocd/project.yaml
kubectl apply -f argocd/application-dev.yaml
kubectl -n argocd port-forward svc/argocd-server 8080:443   # open https://localhost:8080
```

---

## Rollback demo (great interview story)

1. Push a change that bumps the image tag → ArgoCD syncs it to prod.
2. `git revert` that commit and push.
3. ArgoCD detects the drift and **automatically reverts prod** to the previous version.
   No `kubectl`, no manual steps — rollback is just a git operation.

---

## What to screenshot for your portfolio
- `pytest` passing + the app's `/metrics` endpoint
- `terraform apply` output (or `kind` cluster up)
- ArgoCD UI showing the app **Synced / Healthy**
- Grafana dashboard with request-rate / error-rate / p95 panels
- A CI run in the GitHub Actions tab (green: test → build → scan → push)

---

## License
MIT
