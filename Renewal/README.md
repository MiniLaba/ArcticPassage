# 霜灯港焕新版开发交接

## 在新电脑上恢复

1. 克隆 ArcticPassage 仓库。文本、Tiled 地图、地图矢量稿、程序和轻量素材可以直接编辑。
2. 从 [开发资产归档](https://github.com/MiniLaba/ArcticPassage/releases/tag/handoff-2026-11-21)下载需要的 ZIP，核对 [SHA-256 及逐文件清单](assets-manifest.json)，解压到**仓库根目录**。各 ZIP 可以单独解开。它们保留工程相对路径。
3. 做地图先下载 `blender-*.zip`。用 Blender 5.3 打开下表对应源文件。做像素地图同时打开 Tiled 的 `霜灯港.world`。做实机按 [源码构建指南](../docs/BUILDING.md) 配置自己电脑的游戏与 SMAPI 路径。
4. 继续官网时进入 `Projects/FrosthavnWebsite/lovable-ready`，执行 `npm ci`、`npm run dev`，部署前运行 `npm run check` 和 `npm run build`。如需宣传片网页素材，解开 `website-film-*.zip`。继续剪辑时根据子工程说明恢复 `film-raw-*`、`film-audio-*`、`film-components-*`、`film-masters-*` 或 `promo-media-*`，再按用途恢复包管理器依赖。

| 用途 | 源文件 |
| --- | --- |
| 当前 Blender 母场景 | `霜灯港焕新版·港湾搭建/四类地表与种子库/霜灯港 · 地表与种子库.blend` |
| 已确认的基准沙盘 | `霜灯港焕新版·地形沙盘/霜灯港 · 地形沙盘.blend` |
| 区域与游戏格网 | [坐标及地图说明](霜灯港焕新版·地图规划/规划与坐标说明.md) · [Tiled 世界](霜灯港焕新版·地图规划/Tiled/霜灯港.world) |
| 场景取景 | 极夜旅客视高第 5 帧。冬末低阳第 88、100 帧。地表和物候第 92–100 帧。远海冰山第 106 帧。候机楼和塔台第 108、109 帧。 |
| 网页和 3D 导出 | [官网工程说明](Projects/FrosthavnWebsite/README.md) · [Lovable 源码](Projects/FrosthavnWebsite/lovable-ready) · [Blender 到网页导出程序](Projects/FrosthavnWebsite/lovable-ready/tools/export-atlas.py) |
| 宣传片 | [首版工程](Projects/FrosthavnPromo/README.md) · [新版工程及流程](Projects/FrosthavnPromo-v2/README.md) |
| 兼容与维护工具 | [模组的测试目录](../tests/) · [补充开发工具](Support/) · [旧电脑入口参考](LocalNotes/) |

网页版模型为 Blender 的轻量导出。轮廓、地图布局、像素件与剧情修改应回到各自源工程。GitHub Pages 和 Lovable 有独立发布流程，本仓库用来保存接续开发所需源文件。网站的正式编辑项目仍由该站原仓库连接维护。

归档以开发交接为范围。游戏本体、本机存档和个人票券、第三方工具与依赖安装目录、机器日志以及可重建的中间帧、重复的发布压缩包未收入交接。历史 Blender 源文件、实录、可编辑脚本、字幕和音频交接文件保留相对路径。旧版制作计划中的数字记录各轮审阅时的状态，以当前母场景及本页帧索引为准。
