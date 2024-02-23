#!/usr/bin/env bash
set -e

IMAGE_NAME="password-manager-api"
DOCKER_REPO_NAME="wojtek9502"

COMMIT_TAG=$(git rev-parse --short HEAD)
IMAGE_LATEST_TAG="${DOCKER_REPO_NAME}/${IMAGE_NAME}:latest"
IMAGE_COMMIT_TAG="${DOCKER_REPO_NAME}/${IMAGE_NAME}:${COMMIT_TAG}"

export DOCKER_BUILDKIT=1
docker build --progress=plain . -t "${IMAGE_LATEST_TAG}" -t "${IMAGE_COMMIT_TAG}"
docker push "${IMAGE_LATEST_TAG}"
docker push "${IMAGE_COMMIT_TAG}"