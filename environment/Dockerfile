FROM public.ecr.aws/docker/library/python:3.13-slim-bookworm@sha256:01f42367a0a94ad4bc17111776fd66e3500c1d87c15bbd6055b7371d39c124fb

ENV DEBIAN_FRONTEND=noninteractive

# Least-volatile layers first: fix the working directory before the apt and
# dependency layers so a change to those never invalidates the WORKDIR layer.
WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        tmux \
        asciinema \
        golang-go \
    && rm -rf /var/lib/apt/lists/*

# /app/data/party_records.json ships TRUNCATED exactly as the failed migration
# left it; the pre-migration extract and the change journal beside it are the
# recovery sources the engine has to be rebuilt from. All values are synthetic.
COPY app/ /app/
RUN cp /app/workflow/link_parties.go /app/workflow/.link_parties.original.go \
    && chmod a-w /app/workflow/.link_parties.original.go
