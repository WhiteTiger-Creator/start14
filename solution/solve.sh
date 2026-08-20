#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export GOCACHE=/tmp/gocache GO111MODULE=off GOPATH=/tmp/gopath

# --- Step 1: rebuild the authoritative party master (#MDM-3170) -------------
# The migration left /app/data/party_records.json holding a truncated prefix.
# Replay the change journal onto the pre-migration extract and write the result
# back to that path; nothing the engine emits is correct until this is done.

go run "${SCRIPT_DIR}/recover_parties.go"

# --- Step 2: restore the linkage engine and produce the match artifacts -----

cp "${SCRIPT_DIR}/link_parties_fixed.go" /app/workflow/link_parties.go
go run /app/workflow/link_parties.go --output-dir /app/output
