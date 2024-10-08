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

provider "kubernetes" {
  config_path    = "/home/k8admin/.kube/config"
  config_context = "microk8s"
}

provider "helm" {
  kubernetes {
    config_path    = "/home/k8admin/.kube/config"
    config_context = "microk8s"
  }
}

resource "kubernetes_namespace" "app_namespace" {
  metadata {
    name = var.app.namespace
  }
}

# module "tls" {
#   source = "./modules/tls"
#   email = var.tls.email
#   private_key_secret_ref = var.tls.private_key_secret_ref
#   providers = {
#     kubernetes = kubernetes
#     helm = helm
#   }
# }

module "app" {
  source = "./modules/app"
  namespace = var.app.namespace
  app_name = var.app.app_name
  domain = "dev2.qmra.org"
  secret_key = var.app.secret_key
  storage = {
    static_root = var.app.storage.static_root
    sqlite_path = var.app.storage.sqlite_path
  }
  providers = {
    kubernetes = kubernetes
    helm = helm
  }
}

# module "monitoring" {
#   source = "./modules/monitoring"
#   providers = {
#     kubernetes = kubernetes
#     helm = helm
#   }
# }