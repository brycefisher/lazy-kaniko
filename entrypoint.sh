#!/bin/sh -eu

# Required Environment Variables:
#
# - DOCKERFILE - path to a Dockerfile within this container. [Ex: /Dockerfile]
# - CONTEXT - path to the docker build context (a directory). [Ex: /workspace]
# - TARGET_IMAGE - name of the docker image (with registry) but without a tag [Ex: localhost:5000/myimage]
#
# Optional Environment Variables for Docker Registry Auth:
#
#  - REGISTRY_USER - username for the registry in question
#  - REGISTRY_HOST - how to reach the registry; should also be the same as the front of TARGET_IMAGE environment variable
#  - REGISTRY_PASSWORD - password for REGISTRY_USER
#  - REGISTRY_INSECURE - use HTTP instead of HTTPS (for testing)

function build_image() {
  local dockerfile="$1"
  local context="$2"
  local target_image_tag="$3"

  echo "Need to build docker container"
  if [[ -n "${REGISTRY_INSECURE:-}" ]]; then
    set -x
    kaniko \
      --dockerfile "$dockerfile" \
      --context "dir://$context" \
      --insecure --insecure-pull \
      --destination "$target_image_tag"
   else
    set -x
    kaniko \
      --dockerfile "$dockerfile" \
      --context "dir://$context" \
      --destination "$target_image_tag"
  fi
}

function calculate_checksum_tag() {
  local dockerfile="$1"
  local context="$2"
  FULL_CHECKSUM="$(docker-source-checksum -f ${dockerfile} ${context})"
  echo "sha-${FULL_CHECKSUM:0:8}"
}

function setup_docker_auth() {
  if [[ -n "${REGISTRY_USER:-}" ]]; then
    mkdir -p $HOME/.docker

    protocol="https"
    if [[ -n "${REGISTRY_INSECURE}" ]]; then
      protocol="http"
    fi
    registry="${protocol}://${REGISTRY_HOST:-index.docker.io}"
    echo "{\"auths\":{\"$registry\":{\"auth\":\"$(printf "%s:%s" "${REGISTRY_USER}" "${REGISTRY_PASSWORD}" | base64 | tr -d '\n')\"}}}" >  $HOME/.docker/config.json
  fi
}

function main() {
  echo "------- LAZY KANIKO --------"

  echo "Found Dockerfile: '${DOCKERFILE}'"
  ls -lah ${DOCKERFILE}

  echo "Found Build Context: '${CONTEXT}'"
  ls -lah ${CONTEXT}

  TAG="$(calculate_checksum_tag $DOCKERFILE $CONTEXT)"
  echo "Calculated image checksum as tag: ${TAG}"

  TARGET_IMAGE_TAG="$TARGET_IMAGE:$TAG"
  if [[ -n "$REGISTRY_HOST" ]]; then
    TARGET_IMAGE_TAG="${REGISTRY_HOST}/${TARGET_IMAGE_TAG}"
  fi
  echo "Full target image + tag: ${TARGET_IMAGE_TAG}"

  setup_docker_auth

  # Determine full url to registry
  protocol="https"
  if [[ -n "${REGISTRY_INSECURE}" ]]; then
    protocol="http"
  fi
  registry="${protocol}://${REGISTRY_HOST:-index.docker.io}"

  # Check for the hash as a tag in the registry
  (reggie --registry="${registry}" --target_image="${TARGET_IMAGE}" | grep "$TAG" && echo 'Skipping build') \
    || build_image "$DOCKERFILE" "$CONTEXT" "${TARGET_IMAGE_TAG}"
}

main
