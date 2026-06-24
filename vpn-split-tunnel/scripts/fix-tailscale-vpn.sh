#!/bin/bash
# Fix Tailscale connectivity when Cisco Secure Client (full-tunnel) is up.
#
# Symptom: `tailscale ping` works but OS `ssh <tailscale-host>` times out.
# Cause:   Cisco's `ciscovpn` iptables chain ends with a catch-all DROP
#          and only RETURNs traffic on enp11s0/lo/docker. Anything on
#          tailscale0 hits the DROP, even when OS routing is correct.
# Fix:     Insert RETURN rules at the top of the ciscovpn chain
#          to whitelist all tailscale0 in/out traffic.
#
# Idempotent — safe to re-run; deduplicates prior identical rules first.
# Re-run after every VPN reconnect (Cisco recreates the chain on each connect).

set -euo pipefail

if ! sudo iptables -L ciscovpn -n >/dev/null 2>&1; then
    echo "ERROR: iptables chain 'ciscovpn' does not exist."
    echo "       Either Cisco VPN is not connected, or you are not on the right machine."
    exit 1
fi

# Cleanup any duplicate RETURN rules from previous runs
while sudo iptables -D ciscovpn -i tailscale0 -j RETURN 2>/dev/null; do :; done
while sudo iptables -D ciscovpn -o tailscale0 -j RETURN 2>/dev/null; do :; done

# Insert at top so they fire before the catch-all DROP at chain end.
sudo iptables -I ciscovpn -i tailscale0 -j RETURN
sudo iptables -I ciscovpn -o tailscale0 -j RETURN

echo "=== ciscovpn chain top ==="
sudo iptables -L ciscovpn -n -v --line-numbers | head -5

# Optional connectivity test: edit/extend this list of target hosts.
TEST_HOSTS=("tasl-labserver")
echo
echo "=== SSH probe ==="
for h in "${TEST_HOSTS[@]}"; do
    if ssh -o ConnectTimeout=5 -o BatchMode=yes "$h" "hostname" 2>&1 | head -1; then
        echo "  $h ✓"
    else
        echo "  $h ✗ (verify ~/.ssh/config or run: ssh -v $h)"
    fi
done

echo
echo "Done. Rules persist as long as Cisco's ciscovpn chain exists"
echo "(i.e. until VPN disconnects). Re-run after each VPN reconnect."
