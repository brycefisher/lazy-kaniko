#!/bin/sh

# Required Environment Variables:
#
# - DOCKERFILE - path to a Dockerfile within this container. [Ex: /Dockerfile]
# - CONTEXT - path to the docker build context (a directory). [Ex: /workspace]
# - TARGET_IMAGE - name of the docker image (with registry) but without a tag [Ex: localhost:5000/myimage]

# TODO - registry authentication for push/pull....

function build_image() {
  local dockerfile="$1"
  local context="$2"

  echo "Need to build docker container"
  set -x
  kaniko \
    --dockerfile "$dockerfile" \
    --context "dir://$context" \
    --no-push
}

function calculate_checksum_tag() {
  local dockerfile="$1"
  local context="$2"
  FULL_CHECKSUM="$(docker-source-checksum -f ${dockerfile} ${context})"
  echo "sha-${FULL_CHECKSUM:0:8}"
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
  echo "Full target image + tag: ${TARGET_IMAGE_TAG}"

  (docker-image-tag list "$TARGET_IMAGE" | grep "$TAG") || build_image "$DOCKERFILE" "$CONTEXT"
}

main
