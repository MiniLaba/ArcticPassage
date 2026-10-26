#!/bin/zsh
set -eu
AP_GAME_ROOT="${0:A:h}"
# A second instance can lock startup preferences and compete for the same save.
if /usr/bin/pgrep -f '[/]霜灯港[.]app/Contents/MacOS/StardewModdingAPI( |$)' >/dev/null; then
    exec /usr/bin/open "$AP_GAME_ROOT/霜灯港.app"
fi
exec /usr/bin/open -n "$AP_GAME_ROOT/霜灯港.app"
