#!/usr/bin/env bash
# Install delegate-swarm as a Claude Code skill.
#   ./install.sh                 -> ~/.claude/skills/delegate-swarm (all projects)
#   ./install.sh /path/to/repo   -> /path/to/repo/.claude/skills/delegate-swarm (one project)
set -euo pipefail
SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [[ $# -ge 1 ]]; then DEST="$1/.claude/skills/delegate-swarm"; else DEST="$HOME/.claude/skills/delegate-swarm"; fi

python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)' \
  || { echo "Python 3.11+ required"; exit 1; }

mkdir -p "$DEST"
cp -r "$SRC"/SKILL.md "$SRC"/config.default.toml "$SRC"/scripts "$SRC"/templates "$SRC"/capsules "$DEST"/
chmod +x "$DEST/scripts/swarm.py"

CFG="${SWARM_CONFIG_DIR:-$HOME/.config/delegate-swarm}"
mkdir -p "$CFG/capsules"
if [[ ! -f "$CFG/config.toml" ]]; then
  cat > "$CFG/config.toml" <<'EOF'
# Your machine-wide overrides for delegate-swarm (defaults: config.default.toml in the skill).
# Free models rotate: run `swarm doctor`, then list the ones you want here.
# [models]
# fast = ["opencode/deepseek-v4.1-flash-free", "opencode/mimo-v2.6-flash-free"]
# strong = ["opencode/nemotron-3-ultra-free", "opencode/big-pickle"]
# [run]
# max_parallel = 5
EOF
fi

mkdir -p "$HOME/.local/bin"
ln -sf "$DEST/scripts/swarm.py" "$HOME/.local/bin/swarm"

echo "Installed skill to: $DEST"
echo "CLI: swarm  (make sure ~/.local/bin is on your PATH)"
echo "Next, inside a repo: swarm doctor && swarm init"
