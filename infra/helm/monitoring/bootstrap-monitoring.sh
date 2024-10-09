#! /bin/bash
set -e
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update

helm install prometheus prometheus-community/prometheus -n monitoring --create-namespace \
    --set server.global.scrape_interval=20s
helm install grafana grafana/grafana -n monitoring \
    --set persistence.storageClassName=microk8s-hostpath
helm upgrade --install loki grafana/loki-stack -n monitoring \
    --set fluent-bit.enabled=false,promtail.enabled=true,grafana.enabled=false,loki.image.tag=2.9.3



