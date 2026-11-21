# Frosthavn · 霜灯港官网

2026-10-27重构为一段北方旅程：自动飞越的机窗首屏、滚动推进接地滑行／停稳后展开海湾、五种光线／八地区、六位居民与职业房间、自然观察手记、十章片段、三节日和一条秘密线索。保留真实游戏截图、中英切换及完整登机安装指南。

官网及公开安装包统一为0.7.10。新增美术均为代码绘制；实机截图、原生素材与网页演绎分别标注。

## 直接查看

双击本目录的 `打开霜灯港官网.command`。使用已打包页面，无需 Lovable 额度，无需联网安装依赖。首次打开需要本机 Node.js；本机已具备。

## 两套入口

- 根目录：轻量本地预览与可静态托管的 Vite 构建，`npm ci`、`npm run build`。
- `lovable-ready/`：从实际 Lovable 项目导出的 TanStack Start 框架，保留路由、SSR 和错误边界；页面已移植并通过构建，`npm ci`、`npm run check`、`npm run build`。

页面文案和发布链接集中在 `src/content.ts`。同步时使用 `tools/prepare-lovable.mjs`，避免维护两份页面发生偏差。

## 发布状态

**已公开上线**：https://frosthavn-siming.lovable.app

Lovable项目名Frosthavn Siming；GitHub同步仓库https://github.com/MiniLaba/frosthavn-siming。累计仅一次AI初始化消息，实际0.4credits；其余设计、代码、修复和发布均未新增AI构建消息。

失效旧连接已获用户明确允许后删除，MiniLaba绑定与main分支同步恢复。完整源码和线上页面均已验证。详细发布提交与部署ID见 docs/Publication.json。

参见 `docs/DEPLOYMENT.md`、`docs/QA.md` 和 `CREDITS.md`。

2026-10-27玩家呈现修订：写给嘶鸣的旅行页面；固定7:10机窗、落地后淡入原全景、原生滚动全屏四季、三位原稿肖像和相遇地点、纯玩家文案。内部验证保留在docs/PlayerExperience-2026-10-27.md，不在网页中展示。


官网原创配乐《冰海来信》使用两套同步编配，在落地时从清冷钢琴弦乐渐入温暖吉他。默认尝试有声播放，浏览器拦截时由首次点击／轻触／键盘交互接续；用户可随时关闭。谱曲和播放行为见 docs/WebsiteMusic-2026-10-27.md，准确发布验证边界见 docs/Publication.json。
