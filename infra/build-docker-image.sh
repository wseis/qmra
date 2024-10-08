#! /bin/bash
set -e
docker build . -t dev.qmra:local
docker save dev.qmra > dev.qmra.tar
microk8s ctr image import dev.qmra.tar
rm dev.qmra.tar