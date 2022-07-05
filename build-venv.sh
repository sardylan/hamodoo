#!/bin/bash

IMAGE_NAME="sardylan/hamodoo-venv"
GIT_SHA_SHORT="$(git rev-parse --short HEAD)"

docker \
  image build \
  -f Dockerfile-venv \
  --target=odoo \
  --tag "${IMAGE_NAME}:${GIT_SHA_SHORT}" \
  .
