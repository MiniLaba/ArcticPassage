# Credits and asset boundaries

- Website code, moonbird mark, CSS animation and code-drawn panorama adaptations: Arctic Passage / Frosthavn project, 2026.
- Arctic Passage project assets remain under the project's MIT license, included as LICENSE.
- Actual Stardew Valley captures include game artwork owned by ConcernedApe. They document this unofficial mod; this repository does not relicense the underlying game artwork or distribute game files.
- The shared bay, five lighting states, six workrooms and ski aircraft are reproducibly drawn by tools/draw_prologue.py. The user-approved town plan informed the composition. These are website illustrations, not exact in-game geometry.
- Native portraits and wildlife frames are taken from the current 0.7.10 candidate mod. Public downloads still point to 0.7.9.
- Gameplay captures are from the 0.7.9 isolated QA character. They do not establish ordinary winter unlock progression.
- Cormorant Garamond and DM Sans are redistributed under their respective SIL Open Font License files in public/assets/. Only Latin WOFF2 subsets are served locally.
- Chinese text uses device fonts. No macOS or commercial font files are redistributed.
- No new image-generation calls were made. Retained mod source portraits and town artwork are reused; earlier code-drawn panorama remains the bay plan. Wind is synthesized locally with Web Audio, off by default.
- No passenger personal data, private boarding pass, game save, credential, or SDK is included.

- The passenger-window wing, runway, snow markers and low shoreline are code-native SVG illustrations in WindowFlight.tsx. ScrollJourney.tsx controls the finite flight, deceleration, parked hold and subsequent reveal. No new image-generation service or paid asset was used.

- Player presentation restores the original continuous bay plan, original 512×512 portrait frames for Ada/Mira/Roan, and four 1448×1086 town masters used by the game scene exporter. Other residents use their meeting-place scenes. Source mapping is in public/assets/experience/sources.json.


2026-10-27：诺拉、莱文、阿玛采用原创代码绘制 SVG 肖像，六种表情同时用于游戏，保留原版服装与职业配色；原三位居民继续使用既有高清原稿。新肖像没有使用生图。源程序 tools/draw_resident_portraits.py；游戏源图与渲染工具位于 ArcticPassage 的 art/source/code-portraits。

2026-10-27 官网配乐《冰海来信 / A Letter from the Ice》及港湾编配《霜灯归港 / Harbour Light》：本项目原创旋律、和声与MIDI编排（tools/compose_site_music.py）。钢琴、弦乐、钟音与尼龙弦吉他由 FluidSynth / GeneralUser GS 2.0.3 渲染。仅分发渲染音轨，不分发音色库；完整许可随 public/assets/music/GeneralUser-GS-license.txt 提供。非实地录音，不代表格陵兰传统音乐。自动播放遵循浏览器规则，未修改浏览器权限。
