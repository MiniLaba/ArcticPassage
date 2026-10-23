# 霜灯港 0.7.9 · 开发预览

这是《星露谷物语》电脑端模组的开发预览，完整扩展仍在制作，单人优先。

## 玩家安装

1. 安装[SMAPI](https://smapi.io/)和[Content Patcher](https://www.nexusmods.com/stardewvalley/mods/1915)。
2. 在本页Assets下载 **ArcticPassage-0.7.9-install.zip**。
3. 解压后将 **ArcticPassage** 和 **ArcticPassage.Runtime** 两个文件夹一起放进游戏的 **Mods**。
4. 通过SMAPI启动，阅读月月鸟邀请，到巴士站按 **B → Enter** 出发；未收到信时先正常过夜。

[完整中文安装指南](https://github.com/MiniLaba/ArcticPassage/blob/main/INSTALL.zh-CN.md)包含各系统路径、首次游玩、升级、备份与排错。玩家不需要编译；不要把source.zip或GitHub自动生成的Source code当作安装包。

## 本次内容

- 新接入山路、冰川观测区、社区屋，现为八室外与四主要室内。
- 原生周委托、有限鱼货换修船铁锭，修复修棚地图和熏鱼收购衔接。
- 冬季固定冰洞：十字镐清理、当天开放、原生鱼竿钓鱼、海冰不可步行。
- 冬季犬队：找工具→送补给→修站→首次试乘，之后开放苔原/营地/冰川三站及9秒演出。
- 保留月月鸟航空、雪跑道、三居民、海产加工和随身手记。

## 测试范围与已知限制

已测试macOS、星露谷1.6.15、SMAPI4.5.2、Content Patcher2.9.1。普通角色已验证部分交货/修棚/加工出售及保存；冬季新功能由隔离测试角色完成原生规则与实际桌面互动验证，不能视为普通冬季全流程通过。生产构建0警告0错误，五组定向检查及实际游戏数据/TMX解析通过。

Windows/Linux尚未完成实机验证；航空、犬队仅开放单人。雪屋暂不能进入；更多居民、动物科研、极昼极夜/极光、三节日、完整十章和多人等尚未完成。先备份存档，完整旧版升级/卸载边界仍待验收。

[完整状态说明](https://github.com/MiniLaba/ArcticPassage/blob/main/docs/PLAYER_STATUS.md) · [更新记录](https://github.com/MiniLaba/ArcticPassage/blob/main/CHANGELOG.md)

## 文件

- `ArcticPassage-0.7.9-install.zip`：玩家安装包。
- `ArcticPassage-0.7.9-source.zip`：项目源码与素材，面向开发者。
- `INSTALL.zh-CN.md`：可单独阅读的安装说明。
- `SHA256SUMS.txt`：两个压缩包的SHA-256校验值。
