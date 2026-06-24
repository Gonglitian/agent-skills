---
name: vpn-split-tunnel
description: Restore connectivity to non-VPN hosts after Cisco Secure Client (AnyConnect) full tunnel takes over. Three platform fixes. (1) macOS — replace Cisco client with openconnect + vpn-slice for client-side split tunnel; Tailscale + VPN coexist natively. (2) LINUX ROUTING — static `ip route` entries for hosts reachable via original gateway (HPCC public-IP). (3) LINUX IPTABLES — Cisco's `ciscovpn` chain ends with `DROP 0.0.0.0/0`; add `RETURN` rules to whitelist tailscale0. Use PROACTIVELY when user says "连了VPN就连不上", "VPN split tunnel", "tailscale 不通", "ssh tasl 超时但 tailscale ping 通", "openconnect with tailscale", "macOS VPN Tailscale 同时用", or has both VPN-protected and non-VPN/Tailscale hosts to access simultaneously.
---

# VPN Split Tunnel

When Cisco Secure Client (AnyConnect) connects in **full tunnel mode**, it routes ALL traffic through the VPN, breaking connectivity to non-VPN hosts. This skill provides platform-specific fixes.

## Quick Decision: Which Fix?

| Platform | Symptom | Go to |
|----------|---------|-------|
| **macOS** | Tailscale + VPN can't coexist | [macOS: openconnect + vpn-slice](#macos-openconnect--vpn-slice) |
| **Linux** | HPCC unreachable after VPN (routing) | [Case 1: Routing Fix](#case-1-routing-fix) |
| **Linux** | Tailscale ping works but SSH times out (iptables) | [Case 2: Tailscale + iptables](#case-2-tailscale--iptables) |

---

## macOS: openconnect + vpn-slice

**Replace Cisco Secure Client entirely.** `openconnect` is an open-source Cisco AnyConnect client; `vpn-slice` lets you explicitly declare which subnets go through the VPN. Everything else — including Tailscale's `100.x` — stays on the local network.

### Why Cisco Secure Client fails on macOS

Cisco installs a **Socket Filter Extension** (`com.cisco.anyconnect.macos.acsockext`) that intercepts ALL sockets at the kernel level. Even when IP routing is correct (Tailscale `100.64/10` → utun), the socket filter drops non-VPN traffic. There is no `iptables` on macOS — the socket filter is a black box.

### Setup (one-time)

```bash
brew install openconnect vpn-slice
```

### Connect

```bash
sudo openconnect vpn.ucr.edu \
  --protocol=anyconnect \
  -u <NetID> \
  -s 'vpn-slice <subnet1> <subnet2> ...'
```

Prompts: sudo password → UCR password → Duo (type `1` + Enter for push).

**UCR pre-configured** (BCC + HPCC):

```bash
sudo openconnect vpn.ucr.edu --protocol=anyconnect -u lgong024 \
  -s 'vpn-slice 169.235.0.0/16 138.23.0.0/16'
```

vpn-slice subnets:
- `169.235.0.0/16` — BCC (`bcc.engr.ucr.edu` → `169.235.18.40`) + VPN server
- `138.23.0.0/16` — HPCC (`cluster.hpcc.ucr.edu` → `138.23.51.7`)

### What happens

| Traffic | Route |
|---------|-------|
| `169.235.x.x` (BCC) | → VPN tunnel |
| `138.23.x.x` (HPCC) | → VPN tunnel |
| `100.x.x.x` (Tailscale) | → local Tailscale utun ✅ |
| Everything else | → local network ✅ |

### Verify

```bash
# VPN hosts
ssh ucr-bcc hostname     # → bcc
ssh hpcc hostname        # → skylark

# Tailscale peers — simultaneously reachable
ssh tasl-labserver hostname
ssh glt-ubuntu hostname
```

### Disconnect

```bash
sudo pkill openconnect
```

### Alias (add to `~/.zshrc`)

```bash
alias ucrvpn='sudo openconnect vpn.ucr.edu --protocol=anyconnect -u lgong024 -s "vpn-slice 169.235.0.0/16 138.23.0.0/16"'
```

### Script

See `scripts/macos-connect.sh`.

---

## Case 1: Routing Fix (Linux)

When HPCC (public IP) becomes unreachable after VPN — the full-tunnel default route steals traffic away from the physical gateway.

### Problem

```
Before VPN:  HPCC (138.23.x.x) ✓   BCC (169.235.x.x) ✗
After  VPN:  HPCC (138.23.x.x) ✗   BCC (169.235.x.x) ✓  ← full tunnel breaks HPCC
With fix:    HPCC (138.23.x.x) ✓   BCC (169.235.x.x) ✓  ← both reachable
```

### How It Works

1. User connects VPN normally via Cisco Secure Client
2. A script adds a host/subnet route for non-VPN targets via the **original default gateway** (before VPN hijacked it)
3. Explicit host routes take priority over the VPN's default route

### Setup Flow

#### Step 1: Gather Network Info (Before VPN)

```bash
ORIG_GW=$(ip route | grep "^default" | awk '{print $3}')
ORIG_DEV=$(ip route | grep "^default" | awk '{print $5}')
echo "Gateway: $ORIG_GW  Interface: $ORIG_DEV"
```

#### Step 2: Identify Target IPs

```bash
host cluster.hpcc.ucr.edu   # → 138.23.51.7
```

#### Step 3: Create and run the fix script

See `scripts/fix-hpcc-route.sh`.

### Pre-configured: UCR BCC + HPCC

| Cluster | Host | IP | VPN needed |
|---------|------|----|------------|
| BCC | bcc.engr.ucr.edu | 169.235.18.40 | Yes |
| HPCC | cluster.hpcc.ucr.edu | 138.23.51.7 | No |

Default gateway on lab workstation: `10.187.76.1` via `enp11s0`.

---

## Case 2: Tailscale + iptables (Linux)

This is **not** a routing problem. Routing is fine. Cisco's iptables firewall is dropping the packets.

### Symptoms

- `tailscale ping <peer>` works (reports "via DERP(...)")
- `ssh <tailscale-host>` and OS `ping <tailscale-ip>` time out
- `ip route get <tailscale-ip>` shows correct route via `tailscale0`
- VPN is connected via Cisco Secure Client (full-tunnel)

### Root cause

Cisco installs four chains: `ciscovpninitial`, `ciscovpn`, `ciscovpnfw`, `ciscovpnfinal`.
The `ciscovpn` chain has a **catch-all DROP at the end**:

```
sudo iptables -L ciscovpn -n -v | tail -1
# 53965 22M DROP all 0.0.0.0/0 → 0.0.0.0/0
```

The chain only RETURNs (whitelists) traffic on `enp11s0`/`lo`/docker bridges. Anything on `tailscale0` falls through to DROP.

### Diagnosis

```bash
ip route get 100.79.185.50              # should show "dev tailscale0"
tailscale ping -c 2 100.79.185.50       # should pong via DERP
ssh -o ConnectTimeout=5 <tailscale-host> true  # times out
sudo iptables -L ciscovpn -n -v | tail -1     # ends with DROP, counter grows
```

### Fix

Insert two RETURN rules at the **top** of `ciscovpn` chain:

```bash
sudo iptables -I ciscovpn -i tailscale0 -j RETURN
sudo iptables -I ciscovpn -o tailscale0 -j RETURN
```

Verify:

```bash
sudo iptables -L ciscovpn -n -v --line-numbers | head -5
# 1   0   0  RETURN  all  --  tailscale0  *           0.0.0.0/0  0.0.0.0/0
# 2   0   0  RETURN  all  --  *           tailscale0  0.0.0.0/0  0.0.0.0/0
ssh tasl-labserver hostname    # should now work
```

**Use `scripts/fix-tailscale-vpn.sh`** — idempotent, safe to re-run.

### Why routing-only fixes don't help

`ip route add <tailscale-cidr> dev tailscale0` doesn't help — routing is already correct (Tailscale's table 52 handles it). Packets leave via `tailscale0` but hit Cisco's DROP. Routing fixes won't reach the iptables layer.

### Why fwmark routing fix is wrong

Don't redirect wireguard underlay (fwmark `0x80000`) to the physical interface — in lab networks without public-internet routes, this breaks DERP entirely. Verify first:

```bash
ping -c 2 -I enp11s0 8.8.8.8     # if this fails → no internet via physical
ping -c 2 -I cscotun0 8.8.8.8    # this should succeed
```

If physical fails and VPN succeeds → use the iptables fix. Wireguard underlay stays on VPN; only `tailscale0` application traffic gets whitelisted.

---

## Troubleshooting

### Route add fails with "RTNETLINK: File exists"
The route is already present. Safe to ignore.

### Still can't reach a public-IP host after adding routes (Linux)
Check `ciscovpn` chain DROP counter:

```bash
sudo iptables -L ciscovpn -n -v | tail -1
```

If counter grows on connection attempt, add RETURN by destination IP:

```bash
sudo iptables -I ciscovpn -d <TARGET_IP> -j RETURN
sudo iptables -I ciscovpn -s <TARGET_IP> -j RETURN
```

### Gateway changed after reboot/reconnect
Re-detect before creating the script:

```bash
ip route | grep "^default"
```

---

## Adapting to Other Setups

| Platform | Approach |
|----------|----------|
| macOS | `openconnect` + `vpn-slice` — list all subnets that need VPN. Everything else goes direct. |
| Linux (public-IP targets) | Add `/32` host routes via original physical gateway. |
| Linux (Tailscale) | Whitelist `tailscale0` in Cisco's iptables chain. |

The key insight across all platforms: **make the VPN explicit about what it owns**, rather than letting it take everything.
