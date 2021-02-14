FROM alpine:3.12

RUN apk add --no-cache curl git

RUN cd /usr/bin/ && \
    curl -sSLo - https://github.com/stefanwalther/docker-image-tag/releases/download/v0.1.10/docker-image-tag_0.1.10_Linux_x86_64.tar.gz \
    | tar xvfz -

COPY --from=gcr.io/kaniko-project/executor:debug /kaniko/executor /usr/bin/kaniko
