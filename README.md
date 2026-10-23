# 北境航路：霜灯港 / Arctic Passage — Frosthavn

《星露谷物语》电脑端的北极渔港扩展：月月鸟航空、雪跑道、彩色木屋、岩岸峡湾、苔原、冬季冰钓和犬队交通。

**当前版本：0.7.9 开发预览。完整扩展仍在开发，单人优先。** 已实测macOS、游戏1.6.15、SMAPI4.5.2、Content Patcher2.9.1；其他电脑系统尚未完成实机验证。

[下载玩家安装包](https://github.com/MiniLaba/ArcticPassage/releases/tag/v0.7.9) · [中文安装指南](INSTALL.zh-CN.md) · [当前内容与限制](docs/PLAYER_STATUS.md) · [更新记录](CHANGELOG.md)

## 安装

1. 安装[SMAPI](https://smapi.io/)和[Content Patcher](https://www.nexusmods.com/stardewvalley/mods/1915)。
2. 从发布页Assets下载`ArcticPassage-0.7.9-install.zip`。
3. 解压，将`ArcticPassage`、`ArcticPassage.Runtime`两个文件夹一起放入游戏的`Mods`目录。
4. 通过SMAPI启动游戏，查看月月鸟邀请信；到巴士站按B、Enter出发。没有收到信时先正常过夜。

正确层级：

```text
Mods/
├── ContentPatcher/manifest.json
├── ArcticPassage/manifest.json
└── ArcticPassage.Runtime/manifest.json
```

玩家请下载**install.zip**；源码包需要开发环境，不能直接安装。详细系统路径、初访、更新、备份和排错见[完整安装指南](INSTALL.zh-CN.md)。

## 已接入内容

- 月月鸟邀请与机票、24秒北极飞行和雪跑道降落、免费返乡。
- 八处室外与四主要室内，四季地图；镇区、渔港、峡湾、苔原、营地、机场、山路、冰川。
- 九种海产、四料理、原生钓鱼/蟹笼、熏鱼机兼容、两夜风干加工。
- 艾达、米拉、罗安三名居民；六步基础交货建设任务，日单与两种周委托。
- 冬季固定冰洞、四步犬队解锁、苔原/营地/冰川三站演出交通。
- 随身手记、五地景观察、分区风潮与三首配乐初稿。

**实现不等于完整验收。** 普通角色已验证航空初访、首批交鱼、修棚、加工出售与部分保存重载；冬季新增功能使用隔离测试角色验证，普通冬季全流程仍待。更多居民、动物科研、极昼极夜/极光、三节日、完整十章和多人仍未完成。具体边界见[玩家状态说明](docs/PLAYER_STATUS.md)。

![犬队雪橇实机画面](docs/images/dog-team.jpg)

![固定冰洞实机画面](docs/images/ice-fishing.jpg)

以上为隔离测试角色的真实游戏截图，尚不代表普通角色完整流程已通过。

## 开发与许可

本仓库提供内容包、运行模块、生成程序及原始素材。[源码构建说明](docs/BUILDING.md)面向开发者；玩家安装无需编译。

原创代码与项目素材使用[MIT许可](LICENSE)。资源来源、历史生成素材和第三方音色许可见[CREDITS](CREDITS.md)及[音色许可](docs/licenses/GeneralUser-GS.txt)。
