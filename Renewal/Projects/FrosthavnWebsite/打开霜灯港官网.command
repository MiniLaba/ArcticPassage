#!/bin/zsh
set -e
cd -- "${0:A:h}"
if [[ -x /opt/homebrew/bin/node ]]; then
  frosthavn_node=/opt/homebrew/bin/node
else
  frosthavn_node=$(command -v node || true)
fi
if [[ -z "$frosthavn_node" ]]; then
  print '需要先安装 Node.js。按回车关闭。'
  read
  exit 1
fi
exec "$frosthavn_node" tools/preview.mjs
