FROM golang:1.17.5-alpine3.14 AS builder
WORKDIR /go/src/app
COPY reggie.go reggie.go
COPY go.mod go.mod
RUN go get -d -v ./...
RUN go build reggie.go && ls -lah

FROM alpine:3.15

RUN apk add --no-cache curl

RUN cd /usr/bin/ && \
    curl -sSLo - https://github.com/stefanwalther/docker-image-tag/releases/download/v0.1.10/docker-image-tag_0.1.10_Linux_x86_64.tar.gz \ | tar xvfz -

RUN curl -sSLo - https://github.com/dpc/docker-source-checksum/releases/download/v0.2.0/docker-source-checksum-v0.2.0-x86_64-unknown-linux-musl.tar.gz  \
    | tar xvfz - \
    && mv docker-source-checksum-v0.2.0-x86_64-unknown-linux-musl/docker-source-checksum /usr/bin/ \
    && rm -rf docker-source-checksum-v0.2.0-x86_64-unknown-linux-musl/

COPY --from=gcr.io/kaniko-project/executor:debug /kaniko/executor /usr/bin/kaniko
COPY --from=BUILDER /go/src/app/reggie /usr/bin/reggie

COPY entrypoint.sh /entrypoint.sh

ENTRYPOINT /entrypoint.sh
