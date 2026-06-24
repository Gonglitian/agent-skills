#!/bin/bash
# detect-gateway.sh — Run BEFORE connecting VPN to capture original gateway
# Outputs gateway IP and interface for use in fix scripts

ORIG_GW=$(ip route | grep "^default" | head -1 | awk '{print $3}')
ORIG_DEV=$(ip route | grep "^default" | head -1 | awk '{print $5}')

echo "Original Gateway: $ORIG_GW"
echo "Original Interface: $ORIG_DEV"
echo ""
echo "Use these values in your fix-route script:"
echo "  ORIG_GW=\"$ORIG_GW\""
echo "  ORIG_DEV=\"$ORIG_DEV\""
