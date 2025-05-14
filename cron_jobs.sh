#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

LOGDIR="/var/log/minigotchi"
mkdir -p "$LOGDIR"
TIMESTAMP=$(date '+%Y-%m-%d_%H%M%S')

# Ensure environment
export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"

# Rotate logs older than 7 days
find "$LOGDIR" -type f -mtime +7 -exec rm -f {} \;

# Run a nightly scan of all visible SSIDs
(
  echo "=== Minigotchi Nightly Scan: $TIMESTAMP ==="
  /usr/bin/minigotchi scan --bssid FF:FF:FF:FF:FF:FF --channel 6 --timeout 120 \
    && echo "Scan completed successfully" \
    || echo "Scan encountered errors"
) >> "$LOGDIR/nightly_scan.log" 2>&1