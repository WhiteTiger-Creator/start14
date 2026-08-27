#!/bin/bash
set -uo pipefail

# The reward channel is closed to everything but root BEFORE any agent code runs.
# The submitted program is executed under uid 65534 further down, so the directory
# it would have to reach is made unreadable and unwritable here rather than being
# left to whatever mode the surrounding harness happens to give it.
mkdir -p /logs/verifier
chmod 700 /logs/verifier
echo 0 > /logs/verifier/reward.txt
chmod 600 /logs/verifier/reward.txt

TEST_DIR="${TEST_DIR:-/tests}"

python -m pytest -o cache_dir=/tmp/pytest_cache \
  --ctrf /logs/verifier/ctrf.json "$TEST_DIR/test_outputs.py" -rA
rc=$?

# Stop anything the graded program left behind before the reward is computed:
# a child still running as the unprivileged candidate could otherwise be writing
# while the result is decided.
pkill -KILL -u 65534 >/dev/null 2>&1 || true
pkill -KILL -P $$ >/dev/null 2>&1 || true
wait >/dev/null 2>&1 || true

if [ "$rc" -eq 0 ]; then
  echo 1 > /logs/verifier/reward.txt
else
  echo 0 > /logs/verifier/reward.txt
fi
