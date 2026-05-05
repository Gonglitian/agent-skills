---
name: ghostty-cjk-input-debug
description: "Diagnose and fix Chinese / Japanese / Korean (CJK) input method (IME) issues in Ghostty terminal on Linux — specifically the snap-distributed Ghostty + fcitx5 + GTK4 + X11 / Wayland combination. Trigger this skill whenever the user reports: 'ghostty 输入不了中文 / 中文打不了 / 输入法不工作 / fcitx 在 ghostty 里失灵', 'ghostty 装好了但输入法没反应', 'snap 应用 + 输入法 / IME 问题', 'GTK4 + XIM 不工作', or wants to mirror a working ghostty + fcitx5 setup from another machine. Also trigger for adjacent symptoms like 'gnome-terminal 能用中文但 ghostty 不行' or 'ghostty 输入候选窗不弹'. The skill provides a 5-pitfall checklist (GTK4-XIM removal, snap classic GTK module loading, --gtk-single-instance zombie, desktop-entry priority shadowing, env propagation paths) and a /proc-based diagnostic protocol that pinpoints the exact failure layer in under 60 seconds. Prefer this skill over generic 'install fcitx5' guidance whenever the user already has fcitx5 working in other apps (e.g., gnome-terminal, browser) but ghostty is the holdout — that pattern is the high-value case this skill is built for."
---

# Ghostty CJK Input Debug

A focused troubleshooting playbook for **CJK input not working in Ghostty on Linux**. Built from a real debug session where every "obvious" fix failed and the actual root cause was 4 layers deep.

> **Scope:** Snap-distributed Ghostty + fcitx5 + GTK4. Most examples assume Ubuntu + GNOME + X11; Wayland deviations called out where they matter.
>
> **Out of scope:** Basic fcitx5 installation. If the user has fcitx5 working in *no* app, point them at `setup-dev-env-ubuntu` first. This skill is for the case where fcitx5 works elsewhere but Ghostty is the holdout — or the user is replicating a known-good setup from another machine and hitting silent failures.

---

## When to use

Use this skill when **all** of these are true:

- The user uses Ghostty on Linux (typically the snap install, the most common distribution).
- CJK / IME input fails *inside Ghostty* — typing produces no candidate window, or candidates appear but commit nothing, or input method switching has no effect.
- Either (a) other apps (gnome-terminal, browser, gedit) accept CJK input fine — narrowing the problem to Ghostty's IM connection — or (b) the user is replicating a known-working setup but Ghostty silently behaves differently.

Don't use this skill for "fcitx5 broken everywhere" — that's an OS-level setup problem, not the Ghostty-specific pattern this skill addresses.

---

## The mental model

Five layers must all line up for CJK input in Ghostty to work. Each layer has a sneaky failure mode:

```
[1] fcitx5 daemon running and reachable on session D-Bus
        ↓
[2] Ghostty process started with the right GTK_IM_MODULE / XMODIFIERS
        ↓
[3] GTK4 inside Ghostty's snap can find libim-fcitx5.so
        ↓
[4] libim-fcitx5.so connects back to fcitx5 daemon over D-Bus
        ↓
[5] fcitx5 has the right input method (e.g. pinyin) enabled and the user can switch to it
```

When CJK input fails, **diagnose top-down** — verify each layer is intact before moving to the next. The 60-second protocol below does this.

---

## The 60-second diagnostic protocol

Run these in a **non-Ghostty** terminal (gnome-terminal works) so you can compare. Replace `$GP` with the Ghostty PID: `GP=$(pgrep -f '/snap/ghostty/.*/bin/ghostty' | head -1)`.

```sh
# Layer 1: Is fcitx5 alive and on D-Bus?
pgrep -af fcitx5
gdbus introspect --session --dest org.fcitx.Fcitx5 --object-path / 2>&1 | head -3

# Layer 2: What env vars did Ghostty actually inherit?
cat /proc/$GP/environ | tr '\0' '\n' | grep -iE 'IM_MODULE|XMODIFIERS|XDG_SESSION_TYPE'

# Layer 3: Did Ghostty load the host's libim-fcitx5.so?
cat /proc/$GP/maps | grep -iE 'fcitx|libim-' | awk '{print $NF}' | sort -u

# Layer 4: Cross-check — XIM_SERVERS atom (X11 only)
xprop -root XIM_SERVERS

# Layer 5: fcitx5 active state and input methods
fcitx5-remote          # 0=inactive, 1=ready, 2=active
ls ~/.config/fcitx5/profile && grep -A2 '^Name=' ~/.config/fcitx5/profile
```

**Reading the output:**

| Symptom | Layer | Likely cause |
|---|---|---|
| `pgrep -af fcitx5` empty | 1 | fcitx5 not autostarted — fix `~/.xinputrc` (`run_im fcitx5`) and re-login |
| `gdbus introspect` fails | 1 | fcitx5 running but D-Bus not available — usually a session-bus issue (root-owned daemon, wrong DBUS_SESSION_BUS_ADDRESS) |
| Layer 2 shows `GTK_IM_MODULE=xim` | **Pitfall #1** | GTK4 dropped XIM on X11. Fix env to `fcitx`. See pitfall section. |
| Layer 2 shows `GTK_IM_MODULE=` (empty) | Pitfall #1 variant | GTK4 falls back to simple, never connects fcitx5. Set to `fcitx`. |
| Layer 2 looks right but **Layer 3 has no `libim-fcitx5.so`** | **Pitfall #2 / #5** | env is OK *now* but Ghostty was started before env was right — singleton-process zombie. `pkill -9` and restart. |
| Layer 3 has the lib but no input | Layer 4 / 5 | fcitx5 daemon issue — try `fcitx5-remote -r` (reload) or check `fcitx5-configtool` for enabled IMs |
| Pinyin/Wubi missing from `~/.config/fcitx5/profile` | Layer 5 | Open `fcitx5-configtool` and add the input method, or copy a working `~/.config/fcitx5/` from another machine |

---

## The 5 pitfalls (each one shipped me into a wall in the original debug session)

### Pitfall #1 — `GTK_IM_MODULE=xim` is a **dead end** on GTK4

**Symptom:** Many old guides recommend a wrapper like:

```sh
#!/bin/sh
export GTK_IM_MODULE=xim
export QT_IM_MODULE=xim
export XMODIFIERS=@im=fcitx
exec /snap/bin/ghostty "$@"
```

Ghostty inherits these env vars but no input method ever activates.

**Why:** Ghostty uses GTK4. **GTK4 removed XIM support on X11** (Wayland uses `text-input-v3` instead). Setting `GTK_IM_MODULE=xim` makes GTK4 silently fall back to the `simple` module — fcitx5 is never consulted.

**Fix:** Use `GTK_IM_MODULE=fcitx` (not `xim`, not empty). Even though Ghostty's snap GTK runtime doesn't ship fcitx5's GTK module, **snap classic confinement** lets it load the host's `/usr/lib/x86_64-linux-gnu/gtk-4.0/4.0.0/immodules/libim-fcitx5.so`. That module talks to fcitx5 via D-Bus, no XIM involved.

**Verify after fix:**
```sh
cat /proc/$GP/maps | grep libim-fcitx5
# expect: /usr/lib/x86_64-linux-gnu/gtk-4.0/4.0.0/immodules/libim-fcitx5.so
```

---

### Pitfall #2 — Ghostty's `--gtk-single-instance=true` zombie

**Symptom:** You changed env vars / desktop entry / `.xprofile`. Closed all Ghostty windows. Reopened from launcher. **Same broken state.** Process env still shows old values.

**Why:** Ghostty is launched with `--gtk-single-instance=true` (the default in the snap desktop entry). Once the first Ghostty process exists, every subsequent "launch" is just a **D-Bus message to the existing process to open a new window**. The new "launch" never spawns a process, never re-reads the desktop entry, never picks up new env.

Closing all windows ≠ killing the process. The singleton hangs around in the background, holding its original env hostage.

**Fix:**
```sh
pkill -9 -f '/snap/ghostty/.*/bin/ghostty'
```
Then relaunch from the GNOME Activities icon. Verify with `ps -o pid,lstart,cmd -p $(pgrep -f /snap/ghostty/.*/bin/ghostty | head -1)` — the start time should be *now*, not hours ago.

> **Confirming this is the bug:** look at `cat /proc/$GP/cmdline`. If you see `/snap/ghostty/<rev>/bin/ghostty` with **no `--gtk-single-instance=true` flag**, that's the singleton main process — started long ago by some old wrapper or pre-fix invocation, still alive.

---

### Pitfall #3 — User-level desktop entry override silently shadows system entry

**Symptom:** You edited `/var/lib/snapd/desktop/applications/ghostty_ghostty.desktop` (or expected snap to do the right thing), but Ghostty still launches with weird env.

**Why:** XDG desktop entry priority: `$XDG_DATA_HOME/applications/` (= `~/.local/share/applications/`) wins over `XDG_DATA_DIRS` entries. A user-level `~/.local/share/applications/ghostty_ghostty.desktop` — often left over from an old fcitx wrapper era — silently overrides the snap-managed system one.

Older guides explicitly recommended creating one:
```
Exec=env GTK_IM_MODULE=xim QT_IM_MODULE=xim XMODIFIERS=@im=fcitx /snap/bin/ghostty
```
That file lingers forever and breaks future fixes.

**Fix:** Either
- Delete it: `rm ~/.local/share/applications/ghostty_ghostty.desktop` (cleanest — fall back to system entry, which inherits IM env from the GNOME session via `.xprofile`)
- Or correct it: `Exec=env GTK_IM_MODULE=fcitx QT_IM_MODULE=fcitx XMODIFIERS=@im=fcitx /snap/bin/ghostty --gtk-single-instance=true`

**Recommended:** Just delete the user-level override and rely on `.xprofile` for env propagation. One source of truth.

---

### Pitfall #4 — Env propagation: terminal ≠ GNOME launcher

**Symptom:** `export GTK_IM_MODULE=fcitx` in `.zshrc` / `.bashrc`. Run `ghostty` from a terminal — works. Click Ghostty icon from GNOME Activities — old env, broken.

**Why:** Two completely different env propagation paths:

| Launch path | Env source |
|---|---|
| Run `ghostty` from a shell | Inherits from your interactive shell (`.zshrc` / `.bashrc`) |
| Click Ghostty icon (GNOME) | Inherits from `gnome-shell` process, which got env from systemd user session + `.xprofile` at session login |

`.zshrc` / `.bashrc` are **only sourced for interactive shells**. They have zero effect on what GNOME-launched apps see.

**Fix:** Put IM env vars in **`~/.xprofile`** (or `~/.profile`):
```sh
export GTK_IM_MODULE=fcitx
export QT_IM_MODULE=fcitx
export XMODIFIERS=@im=fcitx
```
**Log out and log back in** for `.xprofile` to be re-sourced. (Re-running it manually doesn't help — `gnome-shell` already started.)

You can keep them in `.zshrc` too for terminal-launched fallback, but `.xprofile` is the load-bearing one.

---

### Pitfall #5 — A working alias from another machine made this *worse*, not better

**Symptom:** A friend's working machine has `alias ghostty='GTK_IM_MODULE= ghostty'` in `.zshrc` — they swear by it. You copy it. Now Ghostty is broken on yours.

**Why:** That alias **clears** `GTK_IM_MODULE` before launching Ghostty. On the friend's machine it works because their setup is different (e.g., session env propagation already broken; clearing it triggers a different code path that happens to work). On yours, you've been carefully arranging for `GTK_IM_MODULE=fcitx` — and the alias undoes it.

The alias also only fires for **terminal-launched** Ghostty — it has zero effect on GNOME-launcher launches, so it gives the false impression of "fixing" things while the launcher path still does whatever it did before.

**Fix:** Remove the alias from `.zshrc`. Ghostty should inherit your shell's `GTK_IM_MODULE=fcitx` directly. If a friend's setup works with a different value, **diagnose their setup** before copying — the env vars they set are downstream effects of their config, not the root cause.

> **General principle:** When mirroring a setup, use `cat /proc/$PID/environ | tr '\0' '\n'` on the **working machine's** Ghostty process to see what env it *actually* has at runtime, not what their dotfiles claim to set. Multiple layers of `.xprofile`, `.profile`, systemd env, and snap launcher hooks each add or remove vars.

---

## Quick remediation script

If diagnostics narrowed it to one of the pitfalls, this end-to-end script applies the canonical fix. **Run from a non-Ghostty terminal.**

```sh
# Ensure fcitx5 stack is installed (no-op if already present)
sudo apt-get install -y fcitx5 fcitx5-chinese-addons \
    fcitx5-frontend-gtk3 fcitx5-frontend-gtk4 fcitx5-frontend-qt5 \
    fcitx5-module-wayland fcitx5-module-xorg im-config

# Set fcitx5 as the active IM (writes ~/.xinputrc with run_im fcitx5)
im-config -n fcitx5

# Canonical env vars in .xprofile (load-bearing for GUI apps)
cat > ~/.xprofile <<'EOF'
export GTK_IM_MODULE=fcitx
export QT_IM_MODULE=fcitx
export XMODIFIERS=@im=fcitx
EOF

# Remove user-level desktop entry override if present
rm -f ~/.local/share/applications/ghostty_ghostty.desktop

# Remove any wrapper script that might shadow /snap/bin/ghostty in PATH
rm -f ~/.local/bin/ghostty

# Remove zsh/bash aliases that mess with GTK_IM_MODULE
sed -i "/alias ghostty=.*GTK_IM_MODULE/d" ~/.zshrc ~/.bashrc 2>/dev/null

# Kill the singleton so the next launch re-reads env
pkill -9 -f '/snap/ghostty/.*/bin/ghostty'

echo "Now: log out & back in (for .xprofile to take effect),"
echo "     then launch Ghostty from the GNOME Activities icon."
```

After re-login, verify with the 60-second diagnostic protocol above.

---

## Mirroring a known-good setup from another machine

When the user has a working machine (e.g., `glt` over SSH) and wants to replicate, sync these 4 things in this order:

```sh
REMOTE=glt   # working host

# 1. fcitx5 user config (input methods, hotkeys, dictionaries)
mkdir -p ~/.config/fcitx5
rsync -av $REMOTE:~/.config/fcitx5/ ~/.config/fcitx5/

# 2. Ghostty config (font, theme, keybinds — independent of IM)
mkdir -p ~/.config/ghostty
scp $REMOTE:~/.config/ghostty/config ~/.config/ghostty/config

# 3. Fonts (if Ghostty config references one not on local)
mkdir -p ~/.local/share/fonts
rsync -av --include='JetBrainsMono*' --exclude='*' \
    $REMOTE:~/.local/share/fonts/ ~/.local/share/fonts/
fc-cache -f ~/.local/share/fonts/

# 4. .xprofile IM env vars (the load-bearing piece)
# Just write ours — don't blindly copy theirs, dotfiles often diverge
cat > ~/.xprofile <<'EOF'
export GTK_IM_MODULE=fcitx
export QT_IM_MODULE=fcitx
export XMODIFIERS=@im=fcitx
EOF
```

**Do not** copy:
- Their `~/.local/share/applications/ghostty_ghostty.desktop` — likely a stale override
- Their `~/.local/bin/ghostty` wrapper — a relic of pre-GTK4 era
- Aliases from their `.zshrc` like `alias ghostty='GTK_IM_MODULE= ghostty'` — see pitfall #5

After sync: log out → log in → kill any old Ghostty singleton → launch fresh.

---

## When this skill says "give up"

Stop and recommend a different approach if:

- **Wayland session + Ghostty still broken after all 5 pitfalls fixed:** Ghostty's Wayland IM support has historical bugs. Try forcing X11: `GDK_BACKEND=x11 ghostty` to confirm, then file a Ghostty issue.
- **Snap is the problem:** if `/proc/$GP/maps` shows no `libim-fcitx5.so` even with `GTK_IM_MODULE=fcitx` and a fresh process, snap classic confinement may not be exposing `/usr/lib/.../immodules` to the snap. Workaround: install Ghostty from source or `.deb` (non-snap), which uses the host GTK directly.
- **Corporate-managed `/etc/X11/Xsession.d/` overriding env:** check `grep -rln 'GTK_IM_MODULE' /etc/X11/` — IT-pushed scripts can clobber `.xprofile`. User would need to override at the right phase (a 99-named script) or escalate.

---

## Background reading (only if needed)

- GTK4 IM module API: `man gtk4-builder-tool` and `gtk4-query-immodules` — but note GTK4 doesn't require an `immodules.cache` file; it scans `immodules/` directly at runtime.
- fcitx5 D-Bus API: `gdbus introspect --session --dest org.fcitx.Fcitx5 --object-path /` — useful for confirming the daemon side is alive.
- Snap classic vs strict: classic apps see the full host filesystem (so they *can* load host GTK modules); strict apps cannot, and need explicit interfaces. Ghostty is classic.
