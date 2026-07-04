#!/usr/bin/env python3
"""checkGPUStatus — SSH 到本期可连的 4 台 server 收集 GPU 情况。

- 直连机 (Tailscale): tasl-labserver / tasl-7 → 跑 nvidia-smi，报每卡 util + 空闲显存。
- Slurm 机 (需 UCR VPN): hpcc / ucr-bcc → 报 (a) 我的作业 (b) 我的账号 GPU 配额与剩余
  (c) 全节点每型号 GPU 的 空闲/总数 (d) 结合配额算"我实际能新申请多少 GPU"。

用法:
  python check_gpu.py              # 查全部 4 台
  python check_gpu.py hpcc bcc     # 只查指定 (名字模糊匹配)
  python check_gpu.py --raw        # 附带原始 ssh 输出，便于排错
"""
import re, subprocess, sys, shlex

SERVERS = [
    {"name": "HPCC",           "host": "hpcc",           "user": "lgong024",     "type": "slurm",  "note": "UCR HPCC · 需 UCR VPN (ucrvpn)"},
    {"name": "BCC",            "host": "ucr-bcc",        "user": "lgong024",     "type": "slurm",  "note": "UCR BCC · 需 UCR VPN (ucrvpn)"},
    {"name": "TASL-LabServer", "host": "tasl-labserver", "user": "vla-reasoning","type": "direct", "note": "Tailscale 直连 · 8× RTX6000 Ada 48G"},
    {"name": "TASL-7",         "host": "tasl-7",         "user": "jiachenl",     "type": "direct", "note": "Tailscale 直连 · 1× RTX4090 24G"},
]

# GPU 型号 → 单卡显存(GB)，Slurm 计算节点无法直连 nvidia-smi，仅作标称参考
VRAM = {"a100": 80, "h100": 80, "blackwell6000": 96, "ada6000": 48, "rtx6000": 48,
        "p100": 16, "k80": 12, "2080ti": 11, "a6000": 48, "null": None}

SSH = ["ssh", "-o", "ConnectTimeout=15", "-o", "BatchMode=yes",
       "-o", "StrictHostKeyChecking=accept-new"]


def run_ssh(host, remote_cmd):
    """返回 (ok, stdout, stderr)。远端命令作为单个 argv 传入，避免本地引号问题。"""
    try:
        p = subprocess.run(SSH + [host, remote_cmd], capture_output=True, text=True, timeout=45)
        return (p.returncode == 0, p.stdout, p.stderr.strip())
    except subprocess.TimeoutExpired:
        return (False, "", "ssh 超时 (>45s)")
    except Exception as e:
        return (False, "", str(e))


def gpu_count(gres):
    """从各种 GRES 串抽 (型号, 数量)。兼容:
      'gpu:blackwell6000:4(IDX:0-3)' → (blackwell6000, 4)
      'gpu:7(S:0-1)'                 → (None, 7)   # 无型号(BCC 总数)
      'gpu:(null):6(IDX:1-6)'        → (None, 6)   # 型号字面量 (null)(BCC 已用)
      'gpu:k80:0(IDX:N/A)'           → (k80, 0)
    数量 = 紧跟在最后一个冒号后、'(' 或行尾/空白/逗号之前的整数。"""
    if not gres:
        return (None, 0)
    m = re.search(r"gpu:(?:.*?:)?(\d+)(?:\(|,|\s|$)", gres)
    cnt = int(m.group(1)) if m else 0
    mt = re.search(r"gpu:([A-Za-z0-9_]+):\d", gres)   # 仅当型号是干净字母数字时才取
    return (mt.group(1) if mt else None, cnt)


# ------------------------- 直连机 (nvidia-smi) -------------------------

def report_direct(srv, raw=False):
    q = "nvidia-smi --query-gpu=index,name,utilization.gpu,memory.used,memory.total --format=csv,noheader,nounits"
    ok, out, err = run_ssh(srv["host"], q)
    lines = [f"### {srv['name']}  ({srv['host']}) — {srv['note']}"]
    if not ok or not out.strip():
        lines.append(f"  ⚠️ 不可达：{err or '无输出'}")
        return "\n".join(lines), None
    free_slots = 0
    rows = []
    for ln in out.strip().splitlines():
        parts = [x.strip() for x in ln.split(",")]
        if len(parts) < 5:
            continue
        idx, name, util, used, total = parts[:5]
        used_i, total_i = int(float(used)), int(float(total))
        free_i = total_i - used_i
        name = name.replace("NVIDIA ", "").replace("GeForce ", "")
        flag = "🟢空闲" if free_i > total_i * 0.85 and int(float(util)) < 15 else \
               ("🟡余量" if free_i > total_i * 0.4 else "🔴占用")
        if free_i > total_i * 0.85 and int(float(util)) < 15:
            free_slots += 1
        rows.append(f"  GPU{idx} {name:<22} util {util:>3}% | 空闲 {free_i:>6}/{total_i} MB  {flag}")
    lines.append(f"  可用整卡(≈全空) ≈ {free_slots} 张")
    lines += rows
    if raw:
        lines.append("  --- raw ---\n" + "\n".join("    " + l for l in out.strip().splitlines()))
    return "\n".join(lines), free_slots


# ------------------------- Slurm 机 -------------------------

SLURM_PROBE = r"""
echo '###JOBS###'
squeue -u {u} -h -o '%i|%P|%j|%t|%M|%b|%N|%R' 2>/dev/null
echo '###QUOTA###'
sacctmgr -n show assoc user={u} format=Account,Partition,GrpTRES%60 2>/dev/null
echo '###GROUPUSE###'
squeue -h -t R,PD -o '%a|%P|%t|%b' 2>/dev/null
echo '###NODES###'
sinfo -N -h -O NodeList:16,Partition:20,StateLong:14,Gres:36,GresUsed:36 2>/dev/null
"""


def report_slurm(srv, raw=False):
    inner = SLURM_PROBE.format(u=srv["user"])
    remote = "bash -lc " + shlex.quote(inner)
    ok, out, err = run_ssh(srv["host"], remote)
    lines = [f"### {srv['name']}  ({srv['host']}) — {srv['note']}"]
    if not ok or "###NODES###" not in out:
        hint = "  （若 VPN 未连，请先在终端跑  ! ucrvpn  再重试）" if "timeout" in (err or "").lower() or not out else ""
        lines.append(f"  ⚠️ 不可达：{err or '无输出'}")
        if hint:
            lines.append(hint)
        return "\n".join(lines), None

    sec = {"JOBS": [], "QUOTA": [], "GROUPUSE": [], "NODES": []}
    cur = None
    for ln in out.splitlines():
        m = re.match(r"###(\w+)###", ln.strip())
        if m:
            cur = m.group(1); continue
        if cur and ln.strip():
            sec[cur].append(ln.rstrip())

    # ---- 我的作业 ----
    my_accounts = set()
    my_run_by_part, my_pd_by_part = {}, {}
    job_lines = []
    for ln in sec["JOBS"]:
        f = ln.split("|")
        if len(f) < 8:
            continue
        jid, part, name, st, t, tres, nodel, reason = f[:8]
        _, g = gpu_count(tres)
        d = my_run_by_part if st == "R" else my_pd_by_part
        d[part] = d.get(part, 0) + g
        state = "🟢跑" if st == "R" else ("⏳排队" if st == "PD" else st)
        extra = f"@{nodel}" if nodel else f"({reason})"
        job_lines.append(f"    [{jid}] {part}/{name} {state} · {g} GPU · {t} {extra}")

    # ---- 我的配额 (GrpTRES gres/gpu) ----
    quota = {}   # partition -> gpu 上限
    for ln in sec["QUOTA"]:
        f = [x.strip() for x in ln.split()]
        # 形如: account partition cpu=48,gres/gpu=4,mem=512G   （partition 可能为空）
        if len(f) < 2:
            continue
        acct = f[0]; my_accounts.add(acct)
        part = f[1] if len(f) >= 3 else ""
        grp = f[-1] if "=" in f[-1] else ""
        mg = re.search(r"gres/gpu=(\d+)", grp)
        if part and mg:
            quota[part] = int(mg.group(1))

    # ---- 组内(我的账号)用量: 消耗共享 GrpTRES ----
    grp_run, grp_pd = {}, {}
    for ln in sec["GROUPUSE"]:
        f = ln.split("|")
        if len(f) < 4:
            continue
        acct, part, st, tres = f[:4]
        if acct not in my_accounts:
            continue
        _, g = gpu_count(tres)
        (grp_run if st == "R" else grp_pd)[part] = (grp_run if st == "R" else grp_pd).get(part, 0) + g

    # ---- 节点 GPU 空闲 (去重: 一个 node 多分区只留一次; 跳过无 GPU 的 CPU 节点) ----
    nodes = {}            # node -> dict
    part_type_free = {}   # partition -> {型号: 空闲整卡数}
    for ln in sec["NODES"]:
        f = ln.split()
        if len(f) < 5:
            continue
        node, part, state, gtot, gused = f[0], f[1], f[2], f[3], f[4]
        typ, tot = gpu_count(gtot)
        _, used = gpu_count(gused)
        if tot == 0:            # 非 GPU 节点(CPU-only)，忽略
            continue
        free = max(tot - used, 0)
        down = "down" in state or "drain" in state
        if node not in nodes:
            nodes[node] = {"type": typ, "tot": tot, "used": used, "free": free,
                           "state": state, "parts": set(), "down": down}
        nodes[node]["parts"].add(part)
        if not down and free > 0:
            part_type_free.setdefault(part, {})
            part_type_free[part][typ] = part_type_free[part].get(typ, 0) + free

    lines.append("  ── 我的作业 ──")
    lines += job_lines or ["    (无)"]

    lines.append("  ── 我的 GPU 配额 / 剩余 (GrpTRES 为组共享, 已扣组内在跑/排队) ──")
    if quota:
        for part, cap in sorted(quota.items()):
            used_g = grp_run.get(part, 0)
            pend_g = grp_pd.get(part, 0)
            remain = max(cap - used_g, 0)
            mine = my_run_by_part.get(part, 0)
            note = f"（其中我在跑 {mine}）" if mine else ""
            pend = f" · 排队 {pend_g}" if pend_g else ""
            flag = "🔴配额已满" if remain == 0 else "🟢有余"
            lines.append(f"    {part:<12} 上限 {cap} · 组内在用 {used_g}{note}{pend} → 剩 {remain} {flag}")
    else:
        lines.append("    (该集群无显式 GPU 配额上限 → 受限于节点空闲)")

    lines.append("  ── 节点 GPU 空闲 (空闲/总, 按型号) ──")
    for node, d in sorted(nodes.items()):
        if d["down"]:
            lines.append(f"    {node:<8} {d['type'] or 'gpu':<14} DOWN/drain")
            continue
        vr = VRAM.get((d['type'] or '').lower())
        vrs = f" ~{vr}G/卡" if vr else ""
        tag = "🟢" if d["free"] == d["tot"] and d["tot"] else ("🟡" if d["free"] else "🔴")
        lines.append(f"    {node:<8} {(d['type'] or 'gpu'):<14} 空闲 {d['free']}/{d['tot']}{vrs} {tag}  [{'/'.join(sorted(d['parts']))}]")

    # ---- 我实际能新申请多少 = min(分区空闲, 剩余配额) ----
    lines.append("  ⇒ 我实际能新申请 (min[分区空闲, 剩余配额]) ──")
    any_reco = False
    for part in sorted(set(part_type_free) | set(quota)):
        tf = part_type_free.get(part, {})
        free_here = sum(tf.values())
        if free_here == 0:
            continue
        remain = max(quota[part] - grp_run.get(part, 0), 0) if part in quota else None
        eff = free_here if remain is None else min(free_here, remain)
        if eff <= 0:
            continue
        any_reco = True
        brk = ", ".join(f"{t or 'gpu'}×{n}" for t, n in sorted(tf.items(), key=lambda x: -x[1]))
        cap = f"配额剩 {remain}" if remain is not None else "无配额上限"
        pn = " · 可抢占" if "preempt" in part else ""
        lines.append(f"    {part:<12} 可申请 ≈ {eff} 张{pn}   [空闲: {brk} · {cap}]")
    if not any_reco:
        lines.append("    (受配额或占用限制，暂无可新申请的空闲 GPU)")

    if raw:
        lines.append("  --- raw ---\n" + "\n".join("    " + l for l in out.splitlines()))
    return "\n".join(lines), None


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    raw = "--raw" in sys.argv
    targets = SERVERS
    if args:
        targets = [s for s in SERVERS if any(a.lower() in s["name"].lower() or a.lower() in s["host"].lower() for a in args)]
        if not targets:
            print("无匹配 server，可选:", ", ".join(s["name"] for s in SERVERS)); return

    print("=" * 68)
    print(" checkGPUStatus — 远程 GPU 巡检")
    print("=" * 68)
    for srv in targets:
        rep, _ = (report_direct if srv["type"] == "direct" else report_slurm)(srv, raw=raw)
        print(rep)
        print("-" * 68)


if __name__ == "__main__":
    main()
