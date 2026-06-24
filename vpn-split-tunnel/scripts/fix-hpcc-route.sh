#!/bin/bash
# fix-hpcc-route.sh — Run AFTER connecting Cisco Secure Client VPN
# Adds a direct route for HPCC so it bypasses the VPN tunnel
#
# Usage: ~/fix-hpcc-route.sh
# Requires: sudo, Cisco Secure Client VPN already connected

HPCC_IP="138.23.51.7"
ORIG_GW="10.187.76.1"
ORIG_DEV="enp11s0"

echo "Adding route for HPCC ($HPCC_IP) via $ORIG_GW dev $ORIG_DEV ..."
sudo ip route add "$HPCC_IP/32" via "$ORIG_GW" dev "$ORIG_DEV" 2>/dev/null

if [ $? -eq 0 ]; then
    echo "Route added successfully."
else
    echo "Route may already exist (safe to ignore)."
fi

echo "Testing connectivity..."
ping -c 2 -W 3 "$HPCC_IP"
