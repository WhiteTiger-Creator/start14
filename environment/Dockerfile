FROM public.ecr.aws/docker/library/golang:1.24-bookworm@sha256:1a6d4452c65dea36aac2e2d606b01b4a029ec90cc1ae53890540ce6173ea77ac

ENV DEBIAN_FRONTEND=noninteractive

# The task is Go-only, so the canonical Go image carries the toolchain
# rather than a Python base with golang-go bolted on.
ENV GOCACHE=/tmp/gocache \
    GOPATH=/tmp/gopath \
    GO111MODULE=off

# Least-volatile layers first: fix the working directory before the apt and
# dependency layers so a change to those never invalidates the WORKDIR layer.
WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        tmux \
        asciinema \
    && rm -rf /var/lib/apt/lists/*

# /app/data/party_records.json ships TRUNCATED exactly as the failed migration
# left it; the pre-migration extract and the change journal beside it are the
# recovery sources the engine has to be rebuilt from. All values are synthetic.
COPY app/ /app/
RUN cp /app/workflow/link_parties.go /app/workflow/.link_parties.original.go \
    && chmod a-w /app/workflow/.link_parties.original.go
