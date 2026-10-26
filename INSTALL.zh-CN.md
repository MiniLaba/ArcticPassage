# 霜灯港玩家安装指南

适用：**霜灯港 / Frosthavn 0.7.10 本机核心开发预览版**。这是《星露谷物语》的模组，需要你已安装电脑版本游戏；本版仍在开发，建议先用备份或单独体验存档。

本机0.7.10安装包尚未上传GitHub；公开页面仍为0.7.9。收到本机候选ZIP时按下面相同的两个目录安装步骤操作。

## 1. 下载这三个部分

| 内容 | 下载与版本 |
|---|---|
| 星露谷物语 | 本版实际测试为电脑端 **1.6.15** |
| SMAPI 模组加载器 | [官方网站](https://smapi.io/)，需要 **4.5.2 或更高兼容版本** |
| Content Patcher | [官方 Nexus 页面](https://www.nexusmods.com/stardewvalley/mods/1915)，本版测试 **2.9.1**；清单最低2.4.0，旧版未测试 |
| 本模组 | [GitHub 发布页](https://github.com/MiniLaba/ArcticPassage/releases/tag/v0.7.9)中的 **ArcticPassage-0.7.9-install.zip** |

下载时展开发布页的 **Assets / 资源**。玩家选择名字带 **install.zip** 的文件；`source.zip`、GitHub自动生成的`Source code`是开发源码，不能直接当作玩家安装包。

已实测环境：macOS、星露谷1.6.15、SMAPI4.5.2、Content Patcher2.9.1。Windows/Linux按相同模组目录结构安装，但尚未完成实机验证。本版不支持手机或主机版本；航空与犬队演出当前仅开放单人。

## 2. 安装前置

关闭游戏。解压SMAPI下载包，按自己的系统运行安装程序，选择安装到现有游戏。Windows运行`install on Windows.bat`；macOS和Linux使用各自安装入口。

第一次安装请按[SMAPI官方玩家指南](https://stardewvalleywiki.com/Modding:Player_Guide/Getting_Started)完成对应系统设置，尤其是Steam启动方式和macOS安装步骤。SMAPI安装好后，游戏目录中会有`Mods`文件夹。

解压Content Patcher，将其中带有`manifest.json`的 **ContentPatcher** 文件夹放入`Mods`。

## 3. 安装霜灯港

解压收到的`ArcticPassage-0.7.10-install.zip`（公开旧版包为0.7.9），把其中这两个完整文件夹一起放入`Mods`：

```text
Stardew Valley/
└── Mods/
    ├── ContentPatcher/
    │   └── manifest.json
    ├── ArcticPassage/
    │   ├── manifest.json
    │   ├── content.json
    │   └── assets/
    └── ArcticPassage.Runtime/
        ├── manifest.json
        ├── ArcticPassage.Runtime.dll
        └── assets/
```

关键是：`Mods/ArcticPassage/manifest.json`和`Mods/ArcticPassage.Runtime/manifest.json`都能直接找到。两个文件夹必须来自同一个版本；不要只装其中一个，也不要把整个解压外层文件夹多套一层放进去。

安装包最外层还附有本说明、许可、鸣谢和版本说明，它们可保留在解压目录，不必放进`Mods`。

## 4. 找不到Mods在哪里

Steam版可在库中右键《星露谷物语》→管理→浏览本地文件，从游戏目录找到`Mods`；macOS可能需要进入`Contents/MacOS`。

常见默认目录：

| 系统 | Mods位置 |
|---|---|
| Windows Steam | `C:\Program Files (x86)\Steam\steamapps\common\Stardew Valley\Mods` |
| macOS Steam | `~/Library/Application Support/Steam/steamapps/common/Stardew Valley/Contents/MacOS/Mods` |
| Linux Steam | `~/.local/share/Steam/steamapps/common/Stardew Valley/Mods` |

游戏装在其他磁盘或使用GOG时，以实际游戏目录为准；[官方指南](https://stardewvalleywiki.com/Modding:Player_Guide/Getting_Started#Find_your_game_folder)列有其他路径。

## 5. 启动和第一次出发

1. **通过SMAPI启动游戏**。安装过程中若配置了Steam启动方式，之后从Steam打开即可；否则使用SMAPI安装后提供的启动入口。
2. 进入存档，阅读农场邮箱里的**月月鸟邀请信**，领取随信机票。没有看到信时，先正常睡一晚，再检查邮箱。
3. 步行到山谷**巴士站**，按 **B** 查看登机牌，按 **Enter** 出发。抵达动画可用 **Esc** 跳过。
4. 飞机降落雪跑道后，沿机场南侧步道进入**霜灯港**，前往广场西侧红色旅舍。
5. 按 **K** 看随身手记和当前目标；渔港可以买25金币训练竿。按原版 **C** 投竿、收竿，按 **X** 与柜台、站牌等互动。
6. 返乡时可由镇内接驳牌回机场，再按 **B → Enter** 返回山谷巴士站。

本版界面支持中文和英文，会随游戏语言切换。

## 6. 继续游玩

- **主线起步**：入住→交三条当季鱼→40木材修棚→两块铁锭修船→次日开航→峡湾探索。材料交给任务指定居民。按 **J** 查看待领奖任务，相关任务页按 **Enter** 领奖；普通 **F** 仍打开原版任务日志。
- **错过鱼季**：按K打开今日页；符合条件时按 **U** 把首单改订为当季鱼，仍需实际交货。
- **柜台键盘操作**：打开柜台后按 **Tab** 启用；方向键选物品，Tab切商品/背包，Enter购买/出售，Esc关闭。
- **冬季冰钓**：修船到达峡湾，站在木平台尽头，手持十字镐检查冰洞标记；清理后向东短投。洞口每天需重新检查，海冰不能行走。训练竿能钓北极鳕；比目鱼需钓鱼4级及合适鱼竿。
- **冬季犬队**：修棚后到苔原停靠处查看米拉的任务，依次找工具、送补给、用20木材和5纤维修站、试乘到营地，之后开放苔原/营地/冰川三站。原生选项用X确认，演出中Esc可直接到站。

目前雪屋仅供外部观察；动物演出、完整研究、三节日、完整十章等仍在开发。[当前内容与限制](docs/PLAYER_STATUS.md)说明哪些已经实现、哪些尚未完成。

## 7. 更新、备份与常见问题

**更新**：退出游戏，备份存档，将旧版`ArcticPassage`和`ArcticPassage.Runtime`移到`Mods`之外留作备份，再放入同版新目录。不要在`Mods`中同时保留两份旧新模组，也不要用源码包覆盖。不要在加载模组的过程中更新文件。

**备份**：使用系统文件管理器复制自己的存档文件夹；位置和恢复方法见[官方存档指南](https://stardewvalleywiki.com/Saves)。本版包含新增地点和物品，卸载前应先回山谷并保留可恢复的备份；完整卸载与跨版升级尚未验收。

| 现象 | 检查方法 |
|---|---|
| 游戏里没有变化 | 确认通过SMAPI启动，两个模组目录都在实际游戏的Mods中 |
| 提示缺少依赖 | 安装Content Patcher，确认ArcticPassage.Runtime也已安装；按报错要求检查版本 |
| 找不到DLL或内容文件 | 重新下载install.zip；不要使用GitHub的Source code压缩包，也不要只复制DLL |
| 提示模组重复 | 将旧版和备份目录移出Mods，再启动 |
| 读不到邀请信 | 检查是否已读旧邀请；先正常过夜，并在巴士站尝试B。旧邀请标识保留兼容 |
| 联机不能登机或乘犬队 | 这是当前明确限制，请先使用单人存档体验；多人尚未完成验收 |
| 仍有红字或闪退 | 保留SMAPI日志，可用[SMAPI日志页面](https://smapi.io/log)整理后附到[GitHub Issues](https://github.com/MiniLaba/ArcticPassage/issues)，注明游戏/SMAPI/CP版本和触发步骤 |
