terraform {
  required_providers {
    kubernetes = {
      source = "opentofu/kubernetes"
      version = "2.32.0"
    }
    helm = {
      source = "opentofu/helm"
      version = "2.0.3"
    }
  }
}

# resource "helm_release" "prometheus" {
#     name = "prometheus"
#     chart = "prometheus-community/prometheus"
#     wait = false
# }

resource "helm_release" "loki-stack" {
    name = "loki-stack"
    repository = "https://grafana.github.io/helm-charts"
    chart = "loki-stack"
    wait = false
}