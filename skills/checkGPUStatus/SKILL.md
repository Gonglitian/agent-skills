---
name: checkGPUStatus
description: 巡检本期 SSH 可连的 4 台远程服务器（HPCC / BCC / TASL-LabServer / TASL-7）的 GPU 情况——每卡显存与利用率、Slurm 集群的账号配额/排队作业/全节点空闲 GPU，并算出"我实际还能新申请多少张"。当用户说"检查 GPU""看下 GPU 显存""GPU 情况""哪台服务器有空卡""查一下算力""where can I run""check GPU status""GPU 够不够""有没有空闲显卡"等，或在准备起训练/挑服务器时触发。
---

# checkGPUStatus

一条命令 SSH 到 4 台 server 汇总 GPU 现状。**用户提到检查 GPU/显存/挑服务器时直接调用本 skill。**

## 覆盖的 4 台（本期 SSH 配置内）

| server | host 别名 | 连接 | 类型 |
|---|---|---|---|
| HPCC | `hpcc` | UCR VPN | Slurm（账号 lgong024 / jlilab·raise） |
| BCC | `ucr-bcc` | UCR VPN | Slurm（账号 lgong024，无 GPU 配额上限） |
| TASL-LabServer | `tasl-labserver` | Tailscale 直连 | 裸机 nvidia-smi（8× RTX6000 Ada） |
| TASL-7 | `tasl-7` | Tailscale 直连 | 裸机 nvidia-smi（1× RTX4090） |

## 怎么跑

```bash
python3 ~/.claude/skills/checkGPUStatus/scripts/check_gpu.py          # 全部 4 台
python3 ~/.claude/skills/checkGPUStatus/scripts/check_gpu.py hpcc     # 只查某台(模糊匹配名/host)
python3 ~/.claude/skills/checkGPUStatus/scripts/check_gpu.py --raw    # 附原始 ssh 输出，排错用
```

跑完后 **用中文给用户一句话总结"现在去哪跑最合适"**（结合空闲卡数、显存、配额、是否可抢占），再附各台明细。

## Slurm 关键逻辑（HPCC / BCC）

登录节点没有 GPU，所以不跑 nvidia-smi，而是查：
1. **我的作业** `squeue -u <user>`：在跑(R)/排队(PD) 各占多少 GPU、在哪个节点/分区。
2. **我的配额** `sacctmgr show assoc`：每分区 `GrpTRES` 里的 `gres/gpu=N`（**组共享**上限）。
3. **组内实时占用** `squeue -t R,PD`（按我的 account 过滤）：正在跑 + 排队的 job 一并计入，**扣减剩余配额**。→ 满足"已排队/在跑的额度也标记为不可用"。
4. **全节点 GPU** `sinfo -O Gres,GresUsed`：每型号 `空闲 = 总数 − 已分配`；CPU-only 节点自动跳过。
5. **我实际能新申请** = `min(分区空闲整卡, 剩余配额)`。preempt_gpu 无配额上限但**可被抢占**，会特别标注。

⚠️ `GrpTRES` 是**整组共享**额度，脚本已扣掉本账号(如 jlilab/raise)在跑+排队的用量；若组内他人也在用，实际剩余可能更少。

## 前置条件 / 排错

- **HPCC、BCC 需先连 UCR VPN**：若这两台报"不可达/超时"，让用户在终端跑 `! ucrvpn` 再重试；tasl 两台走 Tailscale 常在线。
- Slurm 命令需登录 shell，脚本已用 `bash -lc` 包裹。
- SSH 用 `BatchMode=yes` + `ConnectTimeout`，不会卡在密码/首连确认上。
- 新增/调整 server：改 `scripts/check_gpu.py` 顶部 `SERVERS` 列表即可。
