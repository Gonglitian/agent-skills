#!/bin/bash
# macos-connect.sh — Connect to UCR VPN with client-side split tunnel
# Replaces Cisco Secure Client. Tailscale + VPN coexist natively.
#
# Prerequisites (one-time):
#   brew install openconnect vpn-slice
#
# Usage:
#   ./macos-connect.sh [netid]
#   ./macos-connect.sh lgong024
#
# Prompts: sudo password, UCR password, Duo (type 1 + Enter for push)

set -euo pipefail

# ── Config ──────────────────────────────────────────────────────────────────
NETID="${1:-lgong024}"
VPN_SERVER="vpn.ucr.edu"
VPN_SUBNETS="169.235.0.0/16 138.23.0.0/16"   # BCC + HPCC; add more as needed

# ── Preflight ───────────────────────────────────────────────────────────────
if ! command -v openconnect &>/dev/null; then
    echo "ERROR: openconnect not found. Install: brew install openconnect vpn-slice"
    exit 1
fi
if ! command -v vpn-slice &>/dev/null; then
    echo "ERROR: vpn-slice not found. Install: brew install vpn-slice"
    exit 1
fi
if pgrep -q openconnect; then
    echo "openconnect already running (PID $(pgrep openconnect))."
    echo "To reconnect: sudo pkill openconnect && $0 $NETID"
    exit 1
fi

echo "Connecting to $VPN_SERVER as $NETID ..."
echo "VPN-only subnets: $VPN_SUBNETS"
echo "(Tailscale 100.x and everything else → local network)"
echo ""

sudo openconnect "$VPN_SERVER" \
    --protocol=anyconnect \
    -u "$NETID" \
    -s "vpn-slice $VPN_SUBNETS"
