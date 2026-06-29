#!/usr/bin/env bash
# Persistent UCR VPN. openconnect runs in the FOREGROUND held by expect (no
# --background, so no proctitle/pgrep detection problems). expect auto-fills the
# VPN password (macOS Keychain 'ucrvpn-pw') and selects Duo option "1"; you just
# approve the push on your phone. A background keepalive (live SSH stream to HPCC)
# defeats the server idle-timeout. Requires sudoers NOPASSWD for openconnect/pkill.
#
# RUN IN A FRESH TERMINAL:  ucrvpn   /   ucrvpn-stop      Log: ~/.ucrvpn.log
set -u
VPN=vpn.ucr.edu
VUSER=lgong024
SLICE="vpn-slice 169.235.0.0/16 138.23.0.0/16"
OPENCONNECT=/opt/homebrew/bin/openconnect
KA_HOST=hpcc
KA_PING=138.23.51.7
PW_SERVICE=ucrvpn-pw
LOG="$HOME/.ucrvpn.log"
log(){ echo "[ucrvpn $(date '+%m-%d %H:%M:%S')] $*" | tee -a "$LOG"; }

if [[ "${1:-}" == "stop" ]]; then
  pkill -f ucrvpn-ka 2>/dev/null
  sudo /usr/bin/pkill -f openconnect 2>/dev/null
  log "stopped (vpn + keepalive killed)"; exit 0
fi
cleanup(){ log "shutting down"; pkill -f ucrvpn-ka 2>/dev/null;
           sudo /usr/bin/pkill -f openconnect 2>/dev/null; exit 0; }
trap cleanup INT TERM

# Foreground connect under expect. Exit codes: 2=auth/login failed (don't hammer),
# 3=timeout/no-connect, 0=was connected then dropped (normal -> reconnect).
connect_vpn(){
/usr/bin/expect <<EXP
log_user 1
set sent 0
set pw [exec security find-generic-password -w -s $PW_SERVICE]
spawn sudo $OPENCONNECT $VPN --protocol=anyconnect -u $VUSER -s "$SLICE"
set timeout 150
expect {
  -re {[Ll]ogin failed}        { exit 2 }
  -re {[Pp]assword:}           { if {\$sent==0} { send "\$pw\r"; set sent 1 }; exp_continue }
  -re {Passcode or option}     { send "1\r"; exp_continue }
  -re {Configured as|CSTP connected|Established DTLS} { }
  timeout                      { exit 3 }
  eof                          { exit 3 }
}
set timeout -1
expect eof
exit 0
EXP
}

log "starting persistent VPN manager (fresh terminal; keep open)"
sudo /usr/bin/pkill -f openconnect 2>/dev/null && log "cleared stale openconnect" || true
sleep 1

# STRONG keepalive: live SSH session to HPCC emitting real traffic every 8s.
( exec -a ucrvpn-ka bash -c '
  while true; do
    ssh -o ConnectTimeout=10 -o ServerAliveInterval=8 -o ServerAliveCountMax=1000 \
        -o BatchMode=yes '"$KA_HOST"' "while true; do printf .; sleep 8; done" >/dev/null 2>&1
    ping -c2 -t3 '"$KA_PING"' >/dev/null 2>&1
    sleep 5
  done' ) &
log "keepalive started (ssh->$KA_HOST stream + ping fallback)"

fails=0
while true; do
  log ">>> connecting (auto-typing password; APPROVE THE DUO PUSH ON YOUR PHONE) <<<"
  connect_vpn; rc=$?
  case $rc in
    0) log "VPN dropped after being connected; reconnecting"; fails=0 ;;
    2) fails=$((fails+1)); log "LOGIN FAILED ($fails/3) — wrong VPN password? Check Keychain 'ucrvpn-pw'";;
    *) fails=$((fails+1)); log "connect timeout/issue (rc=$rc) ($fails/3)";;
  esac
  if (( fails >= 3 )); then
    log "!!! 3 failures — STOPPING to avoid NetID lockout. Fix pw: security add-generic-password -U -a $VUSER -s $PW_SERVICE -w 'PW' ; then rerun ucrvpn"
    cleanup
  fi
  sleep 3
done
