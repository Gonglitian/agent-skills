---
name: vpn-split-tunnel
description: Restore and KEEP UCR VPN connectivity. Bundles four fixes. (1) ROUTING fix — static routes for non-VPN hosts via the original gateway (HPCC public-IP case). (2) IPTABLES fix (Linux) — Cisco's `ciscovpn` chain ends with `DROP 0.0.0.0/0`, dropping `tailscale0` traffic; add `RETURN` rules. (3) macOS PERSISTENT auto-reconnect manager — the UCR server drops idle sessions ("Idle Timeout", b0); a keepalive (live SSH stream over the tunnel) + foreground-openconnect-held-by-expect + auto-reconnect watchdog keeps it up, with Keychain auto-login + Duo push + sudoers NOPASSWD so no typing is needed. (4) Tailscale/VPN route-hijack — after a VPN drop, Tailscale's overlapping 169.235 subnet routes steal the BCC route (HPCC still works → easy to misdiagnose). Use PROACTIVELY when user says "连了VPN就连不上", "VPN split tunnel", "tailscale 不通", "VPN 老掉线/只能连一会儿就断", "idle timeout", "VPN 自动重连/持久化/自动登录", "ssh tasl 超时但 tailscale ping 通", "ciscovpn chain dropping", "claude monitor 连不上 ssh", or has both VPN-protected and non-VPN/Tailscale hosts to access simultaneously.
---

# VPN Split Tunnel

When Cisco Secure Client (AnyConnect) connects in **full tunnel mode**, it routes ALL traffic through the VPN, breaking connectivity to hosts that don't need VPN. This skill fixes that by adding static routes for non-VPN hosts via the original gateway.

## Problem

```
Before VPN:  HPCC (138.23.x.x) ✓   BCC (169.235.x.x) ✗
After  VPN:  HPCC (138.23.x.x) ✗   BCC (169.235.x.x) ✓  ← full tunnel breaks HPCC
With fix:    HPCC (138.23.x.x) ✓   BCC (169.235.x.x) ✓  ← both reachable
```

## How It Works

1. User connects VPN normally via Cisco Secure Client
2. A script adds a host/subnet route for non-VPN targets via the **original default gateway** (before VPN hijacked it)
3. Traffic to VPN-protected hosts goes through the tunnel; everything else goes direct

## Setup Flow

### Step 1: Gather Network Info (Before VPN)

Run these commands **before** connecting VPN to capture the original gateway:

```bash
# Record original default gateway and interface
ORIG_GW=$(ip route | grep "^default" | awk '{print $3}')
ORIG_DEV=$(ip route | grep "^default" | awk '{print $5}')
echo "Gateway: $ORIG_GW  Interface: $ORIG_DEV"
```

### Step 2: Identify Target IPs

Resolve all hosts that need to remain reachable outside VPN:

```bash
host <hostname>
# e.g., host cluster.hpcc.ucr.edu → 138.23.51.7
```

### Step 3: Create the Fix Script

Generate `~/fix-route.sh` with the gathered info:

```bash
#!/bin/bash
# Run AFTER connecting Cisco Secure Client VPN
# Adds direct routes for non-VPN hosts, bypassing the tunnel

TARGETS=("138.23.51.7")  # Add more IPs as needed
ORIG_GW="<detected-gateway>"
ORIG_DEV="<detected-interface>"

for ip in "${TARGETS[@]}"; do
    echo "Adding route for $ip via $ORIG_GW dev $ORIG_DEV ..."
    sudo ip route add "$ip/32" via "$ORIG_GW" dev "$ORIG_DEV" 2>/dev/null || \
        echo "  Route already exists or failed"
done

echo "Verifying connectivity..."
for ip in "${TARGETS[@]}"; do
    ping -c 1 -W 3 "$ip" > /dev/null 2>&1 && \
        echo "  $ip ✓" || echo "  $ip ✗"
done
```

### Step 4: Usage

```bash
# 1. Connect VPN via Cisco Secure Client (GUI or CLI)
# 2. Run the fix script
~/fix-route.sh
# 3. Both clusters are now reachable
```

## Pre-configured: UCR BCC + HPCC

For the TASL lab's common setup (UCR campus):

| Cluster | Host | IP | VPN needed |
|---------|------|----|------------|
| BCC | bcc.engr.ucr.edu | 169.235.18.40 | Yes (vpn.ucr.edu/bcoe) |
| HPCC | cluster.hpcc.ucr.edu | 138.23.51.7 | No |

The default gateway on the lab workstation is typically `10.187.76.1` via `enp11s0`.

**Ready-to-use script** (see `scripts/fix-hpcc-route.sh`):

```bash
~/fix-hpcc-route.sh
```

## Case 2: Tailscale stops working after Cisco VPN connects

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
The chain only RETURNs (whitelists) traffic on `enp11s0`/`lo`/docker bridges. Anything going out on `tailscale0` falls through to DROP. The packet counter on the DROP rule grows every time you try to ssh — that's the proof.

### Diagnosis: did you hit this case?

```bash
# Confirm OS routing is correct
ip route get 100.79.185.50      # should show "dev tailscale0"

# Confirm Tailscale itself is functional
tailscale ping -c 2 100.79.185.50    # should pong via DERP

# Confirm OS-level ssh fails
ssh -o ConnectTimeout=5 <tailscale-host> true   # times out

# Look at the killer rule
sudo iptables -L ciscovpn -n -v | tail -1   # ends with DROP
# Try ssh, then check counter again — it grows
```

If routing is correct + tailscale ping works + OS ssh fails + DROP counter grows → **this case**.

### Fix

Insert two RETURN rules at the **top** of `ciscovpn` chain (`-I` defaults to position 1) to whitelist Tailscale traffic before the catch-all DROP fires:

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

**Use the bundled `scripts/fix-tailscale-vpn.sh`** — it dedupes prior runs and is idempotent.

### Why a routing-only fix doesn't help here

A common reflex is to add `ip route add <tailscale-cidr> dev tailscale0`. Routing is **already** correct (Tailscale's table 52 has it). The packets do leave via `tailscale0`. They just hit Cisco's iptables DROP on the way out (or replies hit it on the way in). Routing fixes won't reach the iptables layer.

### Why a fwmark routing fix is wrong here

Another reflex: assume Tailscale's underlay UDP (fwmark `0x80000`) is being routed into the VPN. Add a higher-priority `ip rule` to send marked packets out the physical interface. **This breaks DERP**: in lab/campus networks where the physical gateway has no public-internet route (only the VPN does), forcing wireguard underlay onto the physical link kills connectivity entirely. Verify first:
```bash
ping -c 2 -I enp11s0 8.8.8.8     # if this fails, your physical gateway has no internet
ping -c 2 -I cscotun0 8.8.8.8    # this should succeed
```
If physical fails and VPN succeeds, DO NOT touch routing. Use the iptables fix instead — wireguard underlay should keep going through the VPN; only the application-layer Tailscale traffic on `tailscale0` needs whitelisting.

## Case 3: macOS — VPN "只能连一会儿就断" + persistent auto-reconnect manager

On macOS the lab uses `openconnect + vpn-slice` (alias `ucrvpn`). The recurring pain is the VPN **dropping after a few minutes**, then SSH to BCC timing out. Hard-won root causes + the durable fix below.

### Root cause of the drops: server-side **Idle Timeout** (NOT DTLS)
The openconnect log shows `Received server disconnect: b0 'Idle Timeout'` → `Session terminated by server; exiting.` The UCR server kills sessions with no tunnel traffic for a few minutes. After the drop, **Tailscale's overlapping `169.235.0.0/16` subnet routes steal the BCC route** (route to `169.235.18.40` shows `gateway 100.70.248.1 / en0` instead of `utun`); HPCC (138.23) still works via Tailscale, which makes it look like "only BCC broke". Diagnose: `route -n get 169.235.18.40 | grep interface` — should be `utunNN`, not `en0`.

### The fix: a persistent manager (`~/bin/ucrvpn-persist.sh`, aliased to `ucrvpn`)
Four parts, all needed:
1. **Keepalive that sends REAL traffic** — hold a live SSH session to a VPN-side host (`ssh hpcc "while true; do printf .; sleep 8; done"`). Plain `ping` may NOT reset the server's idle timer; a real TCP/SSH stream does. This is what actually stops the idle-timeout drops.
2. **Foreground openconnect held by `expect`** — do NOT use `--background`. openconnect `--background` rewrites its proctitle (drops args), so `pgrep -f "openconnect <host>"` can't find it → a watchdog falsely thinks "connect failed", reconnects in a loop, and its failure-cap cleanup then **kills the working VPN**. Instead run openconnect in the foreground under `expect`, and `expect eof` (with `set timeout -1`) to hold it; eof = the VPN dropped → reconnect. Detection becomes implicit, no pgrep.
3. **Auto-login without typing** — `expect` pulls the VPN/NetID password from macOS **Keychain** (`security find-generic-password -w -s ucrvpn-pw`; never hardcode it in the script), auto-fills the `Password:` prompt, and auto-selects Duo option `1`. You only approve the push on your phone (2FA can't/shouldn't be automated). Keepalive means reconnects are rare → usually one push per session.
4. **sudoers NOPASSWD for openconnect** — the **Mac login/sudo password ≠ the NetID/VPN password**. Don't try to auto-type two different passwords into indistinguishable `Password:` prompts (wrong sends → lockout risk). Instead make sudo passwordless for just openconnect+pkill:
   ```
   echo 'glt ALL=(root) NOPASSWD: /opt/homebrew/bin/openconnect *, /usr/bin/pkill -f *openconnect*' \
     | sudo tee /etc/sudoers.d/ucrvpn >/dev/null && sudo chmod 440 /etc/sudoers.d/ucrvpn \
     && { sudo visudo -cf /etc/sudoers.d/ucrvpn && echo SUDOERS_OK || sudo rm -f /etc/sudoers.d/ucrvpn; }
   ```
   With NOPASSWD, the only `Password:` prompt expect sees is the VPN one → safe to auto-fill.

See the ready script at `scripts/ucrvpn-persist.sh` (template; edit user/host/openconnect-path). Store the password once: `security add-generic-password -U -a <netid> -s ucrvpn-pw -w '<password>'`.

### Footguns that cost hours (check these first)
- **zsh alias parse-time**: `source ~/.zshrc && ucrvpn` on ONE line expands `ucrvpn` using the OLD alias (aliases resolve at parse time, before `source` runs). Always run `ucrvpn` in a **fresh terminal** (or as a separate command). Confirm the right script ran by looking for `[ucrvpn ...]` log lines in `~/.ucrvpn.log`.
- **Lockout safety**: a wrong VPN password retried in a loop locks the NetID. The manager sends the password at most once per attempt, stops on `Login failed`, and hard-stops after 3 failures. Keep that cap.
- **Exact password**: trailing punctuation counts (a password ending in `.` failed silently as "Login failed" until the dot was included). Verify the stored Keychain value length matches.
- **Stale openconnect blocks reconnect**: a leftover openconnect from a prior run makes a pgrep-based watchdog think it's connected. The manager `sudo pkill -f openconnect` at startup (works via the NOPASSWD rule).

## Troubleshooting

### Route add fails with "RTNETLINK: File exists"
The route is already present. Safe to ignore.

### Still can't reach a public-IP host after adding routes (Case 1)
Check `ciscovpn` chain DROP counter — same iptables filter may be at play even for non-Tailscale hosts:
```bash
sudo iptables -L ciscovpn -n -v | tail -1
```
Try a connection, see if counter grows. If yes, add a RETURN by destination IP at the top of the chain:
```bash
sudo iptables -I ciscovpn -d <TARGET_IP> -j RETURN
sudo iptables -I ciscovpn -s <TARGET_IP> -j RETURN
```

### Gateway changed after reboot/reconnect
The original gateway may change (DHCP). Re-detect before creating the script:
```bash
ip route | grep "^default"
```

### Alternative: openconnect + vpn-slice
If you have admin access or the VPN server allows it, `openconnect` with `vpn-slice` provides a cleaner client-side split tunnel. Install:
```bash
sudo apt install -y openconnect
sudo pip3 install vpn-slice
```
Connect with split routing:
```bash
sudo openconnect vpn.ucr.edu/bcoe --protocol=anyconnect -u <user> \
  -s 'vpn-slice 169.235.0.0/16'
```
Note: This may not work with all Cisco ASA configurations (known 404 issue with older openconnect versions on some group URLs).

## Adapting to Other Setups

This pattern works for any VPN + non-VPN host combination. To adapt:

1. Replace target IPs with your non-VPN hosts
2. Detect your local gateway (`ip route | grep default`)
3. Generate the fix script with the correct values
4. Run after each VPN connection

The key insight: VPN replaces the default route, but **explicit host routes take priority** over the default route in the Linux routing table.
