#!/bin/sh
set -e
if [ -t 0 ]; then
  exec uv run python -m inspector "$@"
fi
exec tail -f /dev/null
