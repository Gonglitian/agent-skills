---
name: omnibox-video
description: >-
  把 OmniBox（小黑 / omnibox.pro/s/<token>）分享里的视频资源（B站 b23.tv + 小红书 type=video）端到端"预阅读"：
  下载音频 → 本地 faster-whisper(GPU) 转写 → 分类并抽取视频里口播/讨论的论文 → 与已有库去重 → 对新 arXiv 论文跑 arxiv-deepdive 出工程报告 → 归档+INDEX。
  解决"视频内容无法被文本收藏覆盖"的问题（很多论文/方法只在讲座、解读视频里出现）。
  Use PROACTIVELY whenever the user wants to process / transcribe / mine the VIDEO items in an OmniBox share, or says
  "把 OmniBox 里的视频转文字", "处理小红书/B站视频", "视频转录后抽论文", "视频预阅读", "transcribe omnibox videos",
  "mine papers from the saved videos", "视频里提到的论文也整理一下"。
  依赖三个 skill：omnibox-sync(取视频清单)、audio-transcribe(GPU转写)、arxiv-deepdive(出报告)；本 skill 负责把它们串起来并处理下载这一最难环节。
---

# omnibox-video：OmniBox 视频资源 → 论文工程报告

OmniBox 收藏里有大量视频（B站讲座、小红书论文解读）。OmniBox 自身的视频转写常因额度耗尽而缺正文，导致这些视频里口播的论文/方法被漏掉。这个 skill 把视频"读"出来：**下音频 → GPU 转写 → 抽论文 → 去重 → 出报告**。

## 一次性环境准备

两个 conda 环境 + 一个克隆仓库（详见各依赖 skill）：

```bash
# 1) 转写环境(py3.11, faster-whisper, GPU)  —— 见 audio-transcribe skill
conda create -n whisper python=3.11 -y && conda run -n whisper pip install faster-whisper yt-dlp
# 2) 小红书下载环境(py3.12, XHS-Downloader 需要 3.12 的多行 f-string)
conda create -n xhs python=3.12 -y
git clone --depth 1 https://github.com/JoeanAmier/XHS-Downloader.git ~/.cache/XHS-Downloader
conda run -n xhs pip install -r ~/.cache/XHS-Downloader/requirements.txt yt-dlp
```
GPU 不可用时 transcribe 可加 `--device cpu`（见 audio-transcribe，约 1.8x 实时；GPU 约 8-12x）。

## 流水线（4 步）

### 1. 取视频清单（用 omnibox-sync 同款 API）
```bash
python <skill_dir>/scripts/list_videos.py --token <share_token> --out <proj>/video_targets.json
```
只拉元数据，按 URL 特征识别：`b23.tv`/`bilibili` → bilibili；`xiaohongshu` 且 `type=video` → xhs。

### 2. 下载音频（最难的一环，本 skill 的核心脚本）
```bash
conda run -n xhs python <skill_dir>/scripts/download_videos.py \
  --targets <proj>/video_targets.json --out <proj>/audio \
  --xhs-repo ~/.cache/XHS-Downloader [--cookie '<xhs网页cookie,可选>']
```
- **B站**：`b23.tv` 短链必须先解析成 `bilibili.com/video/BV...`（否则 yt-dlp 走 generic 提取器被 412 拦），再 `python -m yt_dlp -x` 取 m4a。成功率 ~95%。
- **小红书**：yt-dlp 的小红书提取器是坏的（"No video formats"）。脚本用 **XHS-Downloader**（正规签名 API，拿新鲜签名地址）为主，失败回退抓页面 `masterUrl`。无 cookie 也能下（低清，转写足够）；给 cookie 成功率/清晰度更高。已删帖/硬过期 token 无法救（约 4 成）。
- 产出 `<proj>/audio/{bili,xhs}_<id>.<ext>` + `download_manifest.json`（含每条状态）。
- 建议下完用 `ffprobe` 抽查时长，确认是真实视频（不是错误页伪装的 mp4）。

### 3. GPU 转写（用 audio-transcribe 的 transcribe.py）
```bash
conda run -n whisper python <audio-transcribe>/scripts/transcribe.py <proj>/audio \
  --device cuda --gpus 0 --compute-type float16 --language zh \
  --context "VLA,具身智能,世界模型,机器人,强化学习,扩散模型,π0,OpenVLA,arxiv,论文" \
  --output-dir <proj>/transcripts
```
- skip-existing、可断点续；`--context` 注入领域词显著改善专有名词识别。
- **务必用容错版 transcribe.py**（单文件解码失败返回 error 而非抛异常）——视频里常有无音轨/损坏文件，否则一个坏文件会让整批崩溃。

### 4. 抽论文 → 去重 → arxiv-deepdive
- **清洗转写**：去掉 `#` 头部与 `[MM:SS-MM:SS]` 时间戳，截断 ~8000 字，分块（~12/块）。
- **分类+解析**（fan-out 一个 workflow，每块一 agent）：判 paper-related、抽点名的工作、对每个用 WebSearch 解析 arXiv id。提示 agent **ASR 名字纠错**（"派零"=π0、"迪诺V2"=DINOv2）。
- **去重**：从 `omnibox_papers/<topic>/<slug>/` 目录名提取已完成 arXiv id 集合，剔除已有。
- **deepdive**：对真正新增的 arXiv 论文调用 **arxiv-deepdive** 流程（PDF+repo+两份报告），归档到 `omnibox_papers/<topic>/<arxivid_slug>/`。
- 最后重建 `INDEX.md`（扫目录，按主题列全部论文）。

## 实测参考（一次全量运行）
421 视频目标 → 下载 284(B站95% / 小红书初次44%) → +XHS-Downloader 救回小红书 75 → 转写 ~95%(GPU 10x 实时) → 抽出 ~186 arXiv(去重) → 与已有库去重后 **81 篇真新增** → 全部出工程报告。视频独有收获：BrickSim、SuSIE、MASt3R、DROID-SLAM、Ouro、MaskedMimic、HERMES、MINT、Vega… 这些只在讲座/解读视频里出现。

## 关键坑（都已在脚本里处理）
- `~/.local/bin/yt-dlp` 若依赖损坏会在 PATH 抢先 → 脚本统一用 `python -m yt_dlp`。
- XHS-Downloader 需 **py3.12**（多行 f-string）；装它的依赖会把 click 降到 8.3.3，所以**必须用独立 xhs 环境**，别污染 whisper 环境。
- 小红书 `xsec_token` 有时效，保存久了会失效；XHS-Downloader 能救新鲜签名，但帖子被删/token 硬过期的救不回。
- 增量复用：第 4 步天然幂等（按 arXiv id 去重），重复运行只补新论文。配合 omnibox-sync 可只处理"新增的视频"。
