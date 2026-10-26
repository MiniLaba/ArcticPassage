#!/bin/zsh
set -eu
AP_GAME_ROOT="${0:A:h}"
# Focus the existing game. Quit it before switching between normal and preview.
if /usr/bin/pgrep -f '[/]霜灯港[.]app/Contents/MacOS/StardewModdingAPI( |$)' >/dev/null; then
    exec /usr/bin/open "$AP_GAME_ROOT/霜灯港.app"
fi
exec /usr/bin/open -n "$AP_GAME_ROOT/霜灯港.app" --args --mods-path "$AP_GAME_ROOT/.development/PreviewMods"
