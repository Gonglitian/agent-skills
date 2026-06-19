---
name: vlog-editor
description: "本地 AI 驱动的端到端视频剪辑流水线，让 Claude Code 自己把原始素材剪成成片——引擎是 FFmpeg（不依赖 DaVinci/Blender/任何付费 MCP）。覆盖：下载素材、探测、从长连续镜头里抽帧选高光（B-roll 内容选取，替代 shot detection）、mlx_whisper 语音转写 + 卡拉OK/普通字幕、librosa 音乐节拍卡点（downbeat 硬切）、暖色电影感调色、交叉转场/硬切/Ken-Burns 推镜、竖屏模糊填充、标题与下字幕、配乐淡入淡出、渲染后自检循环、project.md 跨会话记忆。Use whenever the user wants to EDIT or ASSEMBLE video from footage — 触发词：剪辑视频 / 剪个 vlog / 把素材剪成片 / 做个 montage / 旅游vlog / 卡点 / 节拍卡点 / 踩点 / 语音字幕 / 自动字幕 / 给视频加字幕 / 视频调色 / 自动剪辑 / 选素材 / edit my video / make a montage / travel vlog / beat sync / cut to the beat / auto captions / burn subtitles / color grade footage。也适用于用户给一个素材目录并希望产出一支剪好的片子。不要用于：生成全新 AI 视频（文生视频）、纯音频处理、或仅转录不剪辑（那用 audio-transcribe）。"
---

# vlog-editor — 本地 AI 视频剪辑流水线

你是一个能**端到端剪视频**的助手。核心理念(来自社区 `video-use` 等 coding-agent 剪辑器的共识):

> **你看不到视频/听不到音频信号，所以把"感知"外包给工具(ffprobe/抽帧/whisper/librosa)，它们吐出结构化数字，你在数字+按需图像上做剪辑决策，再交给 FFmpeg 渲染。**
> 原则:*Text + on-demand visuals, no frame-dumping* —— 只在决策点抽几帧看，不要 dump 整片。

引擎是 **FFmpeg**。不要建议 DaVinci/Blender/OTIO MCP:它们的剪辑调色 API 被封，OTIO 也不渲染像素。

---

## 0. 环境(每次开工先确认)

```bash
# 渲染必须用完整版 ffmpeg（带 drawtext/libass/videotoolbox）。Homebrew 那个常缺 libfreetype！
FFMPEG=/opt/homebrew/Caskroom/miniconda/base/envs/whisper/bin/ffmpeg
$FFMPEG -hide_banner -filters | grep -q drawtext && echo "OK: drawtext 可用" || echo "换一个带 libfreetype 的 ffmpeg"
WHISPER_PY=/opt/homebrew/Caskroom/miniconda/base/envs/whisper/bin/python   # mlx_whisper + librosa
```

所有 `bin/*.py` 默认就用这个 ffmpeg(`FFMPEG` 环境变量可覆盖)。缺工具时:
`brew install yt-dlp` · `$WHISPER_PY -m pip install librosa auto-editor` · whisper 模型 `mlx-community/whisper-large-v3-turbo`。

---

## 1. 工作流总览

```
摄入 → 选取 → 决策(写 EDL) → [卡点] → 组装渲染 → 自检循环 → 更新 project.md
probe   scan/transcribe   你         beats     assemble       qc            记忆
```

**先读项目里的 `project.md`**(若存在)续上历史；没有就从 `project.md.template` 建一份。

---

## 2. 摄入 & 选取

### 探测
```bash
python3 bin/probe.py footage/*.mp4 > work/probe.json   # 分辨率/帧率/时长/是否有音轨/横竖屏
```

### 素材分两类，选取方式不同:

**B-roll(空镜/风景/无人说话)——用 `scan.py`，不要用 shot detection**
连续长镜头几乎没有硬切，PySceneDetect/TransNetV2 找不到东西。正解是抽帧让你看:
```bash
python3 bin/scan.py footage_real/hawaii.mp4 --interval 3   # 出带时间戳的接触印相表 + freezedetect 静态段
```
然后 **Read 那张 `work/scan/<name>_sheet00.jpg`**，认出好窗口(光线/构图/主体/有没有动作)，**避开过曝/偏暗/静止段**。在决策点对候选窗口中点抽全分辨率帧复核:
```bash
$FFMPEG -ss <t> -i clip.mp4 -frames:v 1 -vf scale=560:-1 work/scan/pick.jpg   # 再 Read 确认
```

**A-roll(口播/人物说话)——用 `transcribe.py`**
```bash
$WHISPER_PY bin/transcribe.py narration.wav > work/transcript.json   # 词级时间戳
```
读转写，标出要保留的句子、删掉 "umm/uh"/重复/静默。把保留段写进 EDL。

---

## 3. 决策:写 EDL(`edl.json`)

EDL 是唯一的"创作"文件，`assemble.py` 读它出片。Schema:

```jsonc
{
  "output": "output/final.mp4",
  "width": 1920, "height": 1080, "fps": 30,
  "font": "/System/Library/Fonts/Supplemental/Futura.ttc",
  "xfade_transition": "fade",      // "fade"=交叉转场 ; "cut"=硬切(卡点用)
  "xfade_duration": 0.8,           // cut 模式忽略
  "kenburns": false, "kenburns_max": 1.06,   // 每镜缓慢推进；硬切处重置=视觉踩点
  "grade": "eq=...,curves=...,vignette=...,unsharp=...",   // 见预设
  "end_fade_to_black": 1.0,
  "title": {"text":"WANDERLUST","subtitle":"...","in":0.6,"hold_until":5.0},
  "music": {"path":"footage/music.mp3","start":0,"fade_in":1.5,"fade_out":2.8,"gain_db":-1},
  "segments": [
    {"clip":"footage/a.mp4","in":20.0,"dur":8.0,"role":"open","caption":""},
    {"clip":"footage/b.mp4","in":2.0,"dur":7.0,"portrait":true,"caption":"ON THE ROAD"},
    {"clip":"footage/c.mp4","in":3.0,"dur":8.0,"role":"close","caption":"UNTIL NEXT TIME"}
  ]
}
```
- `role:"open"` 段叠大标题；`portrait:true` 竖屏素材自动模糊背景填充；`caption` 是下字幕(留空则无)。
- 直接复制 `presets/cinematic.json`(舒缓) 或 `presets/beat.json`(踩点) 当起点，改 `segments` 即可。

```bash
python3 bin/assemble.py edl.json    # 两遍渲染：pass1 逐段归一化+调色+字幕，pass2 转场+配乐+编码
```

---

## 4. 卡点(可选，节奏感强)

```bash
$WHISPER_PY bin/beats.py footage/music.mp3 > work/beats.json   # BPM + 每拍/每小节(downbeat)时间戳
```
让每段 `dur` = 相邻 downbeat 之差(视频从 0 起、音乐从 0 起)→ 硬切正好落在小节线。`xfade_transition:"cut"` + `kenburns:true`。

## 5. 语音字幕(口播片)

```bash
$WHISPER_PY bin/subtitles.py work/transcript.json work/captions.ass --style karaoke   # 逐词高亮；或 --style plain
$FFMPEG -i base.mp4 -vf "ass=work/captions.ass" -c:a copy out.mp4   # libass 烧入
```

## 6. 自检循环(渲染后必做)

```bash
python3 bin/qc.py output/final.mp4 --edl edl.json   # 黑帧/削波/时长/规格 检查 + QC 印相表
```
**Read `work/qc/<name>_qcsheet.jpg`** 视觉确认标题/字幕/调色都对。verdict=WARN 或印相表有问题 → 改 `edl.json` 重渲(最多 ~3 轮)，**别把有问题的片子给用户**。

## 7. 更新记忆

渲染通过后，在 `project.md` 的 Render Log 追加一行(日期/EDL/输出/时长/QC)，并把新决策、新踩坑记下来。

---

## 关键踩坑(违反必出 bug)

1. **drawtext 字幕全部消失**:① ffmpeg 没 libfreetype → 用 conda 完整版；② **`-ss` 必须在 `-i` 之前**(输入端定位、重置时间轴)——放之后保留源 PTS，高 in 点片段的字幕 alpha 淡入淡出窗口永不命中、alpha 恒 0。`assemble.py` 已正确处理，自己写临时命令时注意。
2. **亮背景字幕看不见** → 白字必须配黑色描边 `borderw=4:bordercolor=black@0.9` + 加强底板。
3. **连续素材别用 shot detection** → 用 `scan.py` 抽帧选取。
4. **混合帧率/分辨率/横竖屏** → `assemble.py` 已统一到目标 `width/height/fps`、竖屏走模糊填充。

## 快速上手(最短路径)

```bash
# 1) 有素材在 footage/ 后：
python3 bin/probe.py footage/*.mp4 > work/probe.json
python3 bin/scan.py footage/<longclip>.mp4          # B-roll 才需要；Read 印相表选窗口
cp presets/cinematic.json edl.json                  # 改 segments 的 clip/in/dur/caption
python3 bin/assemble.py edl.json
python3 bin/qc.py output/final.mp4 --edl edl.json   # Read QC 印相表，必要时重渲
```

工具清单:`probe.py`(探测) `scan.py`(B-roll选取) `transcribe.py`(转写) `subtitles.py`(字幕) `beats.py`(卡点) `assemble.py`(渲染) `qc.py`(自检)。
