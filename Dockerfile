FROM golang:1.17.6-alpine3.15 AS BUILDER

WORKDIR /go/src/app

COPY reggie.go reggie.go

COPY go.mod go.mod

RUN go get -d -v ./... && go build reggie.go

FROM alpine:3.15.0

RUN apk add --no-cache curl && \
    curl -sSLo - https://github.com/dpc/docker-source-checksum/releases/download/v0.2.0/docker-source-checksum-v0.2.0-x86_64-unknown-linux-musl.tar.gz  \
    | tar xvfz - \
    && mv docker-source-checksum-v0.2.0-x86_64-unknown-linux-musl/docker-source-checksum /bin/

COPY --from=gcr.io/kaniko-project/executor:debug /kaniko/executor /bin/kaniko

COPY --from=BUILDER /go/src/app/reggie /bin/

COPY entrypoint.sh /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
