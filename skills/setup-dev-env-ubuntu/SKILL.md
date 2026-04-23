---
name: setup-dev-env-ubuntu
description: Bootstrap a fresh Ubuntu machine to Gonglitian's personal dev setup — zsh + oh-my-zsh + fzf, Ghostty terminal (TokyoNight), Edge as default browser, VSCode, Miniconda, Claude Code with the `cc` alias + claude-hud plugin, GitHub CLI auth (HTTPS), Snipaste, WeChat, fcitx Chinese input, and Tailscale. Trigger this skill whenever the user says "setup this machine", "new ubuntu", "新电脑配置", "配一下开发环境", "装一下常用软件", "装 claude code / ghostty / edge / zsh / miniconda", "fresh ubuntu install", "new computer dev env", or asks to install any of the tools above on a fresh box. Also trigger on requests to fix Chinese input in Ghostty, to set up `gh auth login`, or to add the `cc=claude --dangerously-skip-permissions` alias.
---

# Ubuntu Dev Environment Bootstrap

Install and configure Gonglitian's preferred dev stack on a fresh Ubuntu host. This skill encodes decisions already made in past sessions — follow them by default, and only deviate if the user asks.

## User Identity (defaults)

| Field | Value |
|-------|-------|
| Git name | `Gonglitian` |
| Git email | `gongc9@qq.com` |
| Default shell | `zsh` (oh-my-zsh, `robbyrussell` theme) |
| Default browser | Microsoft Edge |
| Terminal | Ghostty (TokyoNight, 14pt) |
| Language needs | English UI + Chinese input (fcitx) |

**Sudo password**: The user will provide it inline (e.g. "run for me, pwd:xxxx"). **Never hardcode it in files.** If a step needs sudo and no password has been given this session, ask once: "I need sudo for this — what's your password?" Then use `echo '<pwd>' | sudo -S <cmd>` for non-interactive execution. Don't log the password.

## When to Trigger

- User says they're on a new/fresh Ubuntu machine and wants "the usual setup"
- User asks to install any one of: zsh/oh-my-zsh, ghostty, edge, vscode, miniconda, snipaste, wechat, tailscale, fcitx, gh, claude code / claude-hud
- User asks to configure the `cc` alias or `--dangerously-skip-permissions`
- User hits a known problem this skill already documents (e.g. "Chinese input doesn't work in ghostty", "ghostty tokyonight theme not found", "gh auth warning about /etc/gitconfig")

## Execution Philosophy

1. **Show the menu first.** Print the full checklist below and ask which items to install. The user likes to pick ("show me and i will decide"). Don't install everything unsolicited.
2. **Run commands yourself.** The user prefers "run this for me" — execute directly, don't paste instructions for the user to run manually unless the step is interactive (gh auth web flow, fcitx-diagnose).
3. **Batch sudo.** Group `apt` installs so the user only provides the password once per session (or use `sudo -v` to refresh the cache).
4. **Verify after each group.** `command -v <tool>` or a `--version` check. Report pass/fail before moving on.

## The Install Menu

```
[ ] 1. Shell:      zsh + oh-my-zsh + fzf (default shell)
[ ] 2. Terminal:   Ghostty (snap, classic) + TokyoNight config
[ ] 3. Browser:    Microsoft Edge (+ set default)
[ ] 4. Editor:     VSCode (snap)
[ ] 5. Claude:     Claude Code + cc alias + claude-hud plugin
[ ] 6. Git:        gh auth login + git identity + /etc/gitconfig fix
[ ] 7. Python:     Miniconda
[ ] 8. Screenshot: Snipaste 2 (AppImage)
[ ] 9. Chat:       WeChat (Linux)
[ ] 10. Input:     fcitx Chinese input (may need build-from-source for ghostty)
[ ] 11. Network:   Tailscale
```

---

## Step 1: Shell — zsh + oh-my-zsh + fzf

```bash
sudo apt update && sudo apt install -y zsh curl git fzf
sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended
chsh -s "$(which zsh)"  # takes effect after logout
```

Oh-my-zsh theme defaults to `robbyrussell` — leave it unless asked.

**fzf key-bindings**: after `apt install fzf`, also run:
```bash
/usr/share/doc/fzf/examples/key-bindings.zsh  # sourced by ~/.zshrc automatically on most distros
```
If Ctrl-R doesn't trigger fuzzy history, add `source /usr/share/doc/fzf/examples/key-bindings.zsh` to `~/.zshrc`.

---

## Step 2: Terminal — Ghostty

```bash
sudo snap install ghostty --classic
```

`--classic` is required; the default strict confinement breaks ghostty's PTY behavior.

Write `~/.config/ghostty/config`:

```ini
# Claude Code: ensure Shift+Enter inserts a newline (required for cc multi-line input)
keybind = shift+enter=text:\n

# Appearance
theme = TokyoNight
font-size = 14
background-opacity = 0.96
background-blur = true
cursor-style = bar
minimum-contrast = 1.3
window-padding-x = 10
window-padding-y = 10

# Behavior
mouse-hide-while-typing = true
copy-on-select = clipboard
```

**Known gotcha — TokyoNight theme "not found"**: Ghostty ships bundled themes under `/snap/ghostty/current/share/ghostty/themes/`. The name is case-sensitive: use `TokyoNight`, NOT `tokyonight`. If it still fails, list available themes with `ghostty +list-themes` and pick an exact match.

---

## Step 3: Browser — Microsoft Edge

```bash
# Official Microsoft repo
curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | sudo gpg --dearmor -o /usr/share/keyrings/microsoft.gpg
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/microsoft.gpg] https://packages.microsoft.com/repos/edge stable main" | sudo tee /etc/apt/sources.list.d/microsoft-edge.list
sudo apt update && sudo apt install -y microsoft-edge-stable

# Set as default
xdg-settings set default-web-browser microsoft-edge.desktop
```

Verify default: `xdg-settings get default-web-browser` should print `microsoft-edge.desktop`.

---

## Step 4: Editor — VSCode

```bash
sudo snap install code --classic
```

---

## Step 5: Claude Code

### 5a. Install Node + Claude Code

User's preferred Node manager is `nvm` (already on machine at `~/.nvm/versions/node/v20.20.2/`). On a fresh box:

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
# reload shell, then:
nvm install 20 && nvm use 20
npm install -g @anthropic-ai/claude-code
```

### 5b. The `cc` alias

Add to **both** `~/.zshrc` AND `~/.bashrc` (user works in both depending on context):

```bash
alias cc='claude --dangerously-skip-permissions'
```

### 5c. `~/.claude/settings.json`

Merge (don't overwrite) these keys:

```json
{
  "skipDangerousModePermissionPrompt": true,
  "extraKnownMarketplaces": {
    "claude-hud": {
      "source": { "source": "github", "repo": "jarrodwatts/claude-hud" }
    }
  },
  "enabledPlugins": { "claude-hud@claude-hud": true }
}
```

### 5d. Install claude-hud plugin

Inside Claude Code:

```
/plugin marketplace add jarrodwatts/claude-hud
/plugin install claude-hud
/reload-plugins
/claude-hud:setup
```

If `/claude-hud:setup` says "Unknown command" right after install, run `/reload-plugins` first.

---

## Step 6: Git + GitHub CLI

### 6a. Fix `/etc/gitconfig` permissions (recurring warning)

```bash
sudo chmod a+r /etc/gitconfig
```

`gh auth login` emits `warning: unable to access '/etc/gitconfig': Permission denied` until this is fixed. One-time, persists across reinstalls.

### 6b. gh auth

```bash
sudo apt install -y gh     # or: sudo snap install gh
gh auth login
```

Answer the prompts with:
- Protocol: **HTTPS**
- Authenticate Git with GitHub credentials: **Yes**
- How to auth: **Login with a web browser**

User reads the one-time code from the terminal, presses Enter, completes flow in Edge.

### 6c. Git identity

```bash
git config --global user.name "Gonglitian"
git config --global user.email "gongc9@qq.com"
git config --global init.defaultBranch main
git config --global pull.rebase false
git config --global credential.helper store
```

---

## Step 7: Miniconda

```bash
wget -O /tmp/miniconda.sh https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash /tmp/miniconda.sh -b -p "$HOME/miniconda3"
"$HOME/miniconda3/bin/conda" init zsh bash
```

After restart, `(base)` prefix should appear in the prompt.

---

## Step 8: Snipaste 2 (free version)

Free Linux version ships as AppImage only.

```bash
mkdir -p ~/Applications && cd ~/Applications
# Grab latest x86_64 AppImage from https://www.snipaste.com/download.html
# Example:
wget -O Snipaste-2.10.6-x86_64.AppImage https://download.snipaste.com/archives/Snipaste-2.10.6-x86_64.AppImage
chmod +x Snipaste-2.10.6-x86_64.AppImage
./Snipaste-2.10.6-x86_64.AppImage &
```

Add to GNOME startup apps so F1/F3 shortcuts work after reboot.

---

## Step 9: WeChat (Linux)

Tencent ships an official Linux build now:

```bash
# Option A: download .deb from https://linux.weixin.qq.com/ (x86_64 .deb)
sudo dpkg -i wechat_*.deb || sudo apt -f install -y
```

If it launches but fonts look broken, install `fonts-noto-cjk`.

---

## Step 10: fcitx — Chinese input

**Default path (try first):**

```bash
sudo apt install -y fcitx fcitx-pinyin fcitx-config-gtk
im-config -n fcitx
# logout/login, then:
fcitx &
fcitx-config-gtk3   # add Pinyin
```

**Known gotcha — Ctrl+Space works in GNOME apps but NOT in Ghostty**: Ghostty's snap sandbox doesn't pick up the IM socket. The fix that worked last time was to **build fcitx from source** outside the snap world, or run ghostty with explicit IM env vars:

```bash
# Try first:
GTK_IM_MODULE=fcitx QT_IM_MODULE=fcitx XMODIFIERS=@im=fcitx ghostty
```

If that still fails, fall back to fcitx5 (newer, sometimes plays nicer with sandboxed apps):

```bash
sudo apt install -y fcitx5 fcitx5-chinese-addons fcitx5-config-qt
im-config -n fcitx5
```

Last resort per past session: build fcitx from source.

---

## Step 11: Tailscale

```bash
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up
```

User may ask to invite others — `tailscale` CLI does NOT have an invite subcommand. Direct user to the admin console: https://login.tailscale.com/admin/users

---

## Verification

After a full run, print this report:

```bash
echo "== tools =="
for t in zsh ghostty microsoft-edge code claude gh conda fcitx tailscale; do
  printf "%-18s %s\n" "$t" "$(command -v $t || echo MISSING)"
done
echo
echo "== shell =="
echo "default: $(getent passwd $USER | cut -d: -f7)"
echo
echo "== git =="
git config --global --get user.name
git config --global --get user.email
echo
echo "== gh =="
gh auth status 2>&1 | head -5
```

## Key Rules

1. **Never hardcode the sudo password** — always ask or use the value from the current turn, never write it into a dotfile or script on disk.
2. **Show the menu, let the user pick** — don't install everything unsolicited.
3. **`cc` alias goes in BOTH bashrc and zshrc** — user switches between them.
4. **Ghostty needs `--classic` snap confinement**, case-sensitive `TokyoNight` theme, and explicit IM env vars if fcitx fails.
5. **Fix `/etc/gitconfig` perms once**, even if it looks unrelated — it suppresses warnings across every future `gh`/`git` invocation.
6. **After installing plugins in Claude Code**, run `/reload-plugins` before trying their commands.
7. **Prefer `.deb` from official vendor repos** (Edge, WeChat) over random PPAs; prefer `snap --classic` when the app needs full filesystem access (Ghostty, VSCode).
