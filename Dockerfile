FROM alpine:3.13.1 AS builder

RUN apk add --no-cache curl

RUN curl -vsSLo /tmp/docker-image-tag.tar.gz https://github.com/stefanwalther/docker-image-tag/releases/download/v0.1.10/docker-image-tag_0.1.10_Linux_x86_64.tar.gz

WORKDIR /tmp

RUN tar xvfz /tmp/docker-image-tag.tar.gz

FROM gcr.io/kaniko-project/executor:debug

COPY --from=builder /tmp/docker-image-tag /bin/docker-image-tag

ENTRYPOINT /busybox/sh
