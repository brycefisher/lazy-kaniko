#!/bin/sh

# Required Environment Variables:
#
# - DOCKERFILE - path to a Dockerfile within this container. [Ex: /Dockerfile]
# - CONTEXT - path to the docker build context (a directory). [Ex: /workspace]
# - TARGET_IMAGE - name of the docker image (with registry) but without a tag [Ex: localhost:5000/myimage]

# TODO - registry authentication for push/pull....

FULL_CHECKSUM="$(docker-source-checksum -f ${DOCKERFILE} ${CONTEXT})"
TAG="sha-${FULL_CHECKSUM:0:8}"
TARGET_IMAGE_TAG="$TARGET_IMAGE:$TAG"

(docker-image-tag list "$TARGET_IMAGE" | grep "$TAG") || echo "Need to build docker container"
