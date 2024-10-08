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

variable "namespace" {
  type =  string
}
variable "app_name" {
  type =  string
}
variable "domain" {
  type =  string
}
variable "secret_key" {
  type =  string
}
variable "storage" {
  type =  object({
        static_root = string
        static_pv_capacity = optional(string, "1Gi")
        sqlite_path = string
        sqlite_pv_capacity = optional(string, "10Gi")
  })
}
variable "helm_chart" {
  type =  string
  default = "../helm/qmra"
}
variable "helm_values_file" {
  type =  string
  default = "../helm/qmra/values.yaml"
}



resource "kubernetes_persistent_volume" "app-static-files-pv" {
  metadata {
    name = "${var.app_name}-static-files-pv"
  }
  spec {
    capacity = {
      storage = var.storage.static_pv_capacity
    }
    access_modes = ["ReadWriteMany"]
    persistent_volume_source {
      host_path {
        path = var.storage.static_root
        type = "DirectoryOrCreate"
      }
    }
    storage_class_name = "microk8s-hostpath"
  }
}

resource "kubernetes_persistent_volume_claim" "app-static-files-pvc" {
  metadata {
    name = "${var.app_name}-static-files-pvc"
    namespace = var.namespace
  }
  spec {
    access_modes = ["ReadWriteMany"]
    resources {
      requests = {
        storage = var.storage.static_pv_capacity
      }
    }
    storage_class_name = "microk8s-hostpath"
    volume_name = "${kubernetes_persistent_volume.app-static-files-pv.metadata.0.name}"
  }
}

resource "kubernetes_persistent_volume" "app-sqlite-file-pv" {
  metadata {
    name = "${var.app_name}-sqlite-file-pv"
  }
  spec {
    capacity = {
      storage = var.storage.sqlite_pv_capacity
    }
    access_modes = ["ReadWriteMany"]
    persistent_volume_source {
      host_path {
        path = var.storage.sqlite_path
        type = "FileOrCreate"
      }
    }
    storage_class_name = "microk8s-hostpath"
  }
}


resource "kubernetes_persistent_volume_claim" "app-sqlite-file-pvc" {
  metadata {
    name = "${var.app_name}-sqlite-file-pvc"
    namespace = var.namespace
  }
  spec {
    access_modes = ["ReadWriteMany"]
    resources {
      requests = {
        storage = var.storage.sqlite_pv_capacity
      }
    }
    storage_class_name = "microk8s-hostpath"
    volume_name = "${kubernetes_persistent_volume.app-sqlite-file-pv.metadata.0.name}"
  }
}

resource "kubernetes_config_map" "app-configmap" {
  metadata {
    name = "${var.app_name}-configmap"
    namespace = var.namespace
  }

  data = {
    DEBUG = "true"
    ALLOWED_HOSTS = "localhost,127.0.0.1,${var.domain}"
    DB_PATH = var.storage.sqlite_path
    STATIC_ROOT = var.storage.static_root
  }
}

resource "kubernetes_secret" "app-secret-key" {
  metadata {
    name = "${var.app_name}-secret-key-secret"
    namespace = var.namespace
  }

  data = {
    "secret-key" = var.secret_key
    # "secret-key" = "${file("${path.module}/.docker/config.json")}"
  }

  type = "Opaque"
}

# release has deployment, service & ingress
resource "helm_release" "app-helm-release" {
    name = var.app_name
    namespace = var.namespace
    create_namespace = false
    chart = var.helm_chart
    values = [
        "${file(var.helm_values_file)}"
    ]
    depends_on = [
         kubernetes_config_map.app-configmap, 
         kubernetes_persistent_volume_claim.app-sqlite-file-pvc,
         kubernetes_persistent_volume_claim.app-static-files-pvc,
         kubernetes_secret.app-secret-key
         ]
}


# resource "kubernetes_ingress_v1" "ahoy_ingress" {
#   metadata {
#     name = "ahoy-ingress"
#   }

#   spec {
#     default_backend {
#       service {
#         name = "ahoy-hello-world"
#         port {
#           number = 80
#         }
#       }
#     }
#     ingress_class_name = "nginx"
#     rule {
#       host = "dev2.qmra.org"
#       http {
#         path {
#           backend {
#             service {
#               name = "ahoy-hello-world"
#               port {
#                 number = 80
#               }
#             }
#           }

#           path = "/"
#         }
#       }
#     }

#     tls {
#       secret_name = "dev2-tls"
#     }
#   }
# }