# 开发接续记录

更新：2026-10-17，版本0.4.0。承接0.3；用户授权设计及实施自行决定，无需普通阶段确认。既定02:00一次续作已执行，未追加定时任务。大奖级美术是目标，当前仍是开发预览。

## 此轮落实的反馈

用户指出鸟鸣不合场景、画面仍像普通小雪村。实际代码检查定位到自定义地点继承Default环境，春季会回退spring_day_ambient并随机播放鸟鸣。现增加两个独立LocationContext、三段原创合成WAV声景：海岸风潮、苔原风声、室内隔墙风声。24图显式指定Context，随机环境声关闭，六地点MusicDefault均指向本模组音轨，昼夜回退也使用自有声景。没有修改山谷全局音乐。完整旋律配乐仍待作曲。

小镇与苔原春季重绘为冷灰碎石、裸岩、低灰褐植被、地衣与风塑积雪，减少鲜艳橙色花园感；0.3原图保留archive。小镇(45,15)、峡湾(42,27)增加12×7格独立近景浮冰；不将冰面算作可钓水域。小镇抵达点改(36,23)，让海湾进入玩家初见镜头。港口、峡湾春季部分暖色植被仍需进一步统一，不把这一轮修正称作全部场景最终定稿。

旅舍与收购站重做完整场景并重新标定家具碰撞、出口、床/柜台动作；旅舍暖炉、海图、厚毯和靴架，收购站秤台、网绳、冰箱和处理台。实机发现原生默认室内光照使新图偏紫，显式AmbientLight修正后已重启截图确认。夜间仍待验收。

三名居民各重做6表情肖像及16帧行走原图并导出原生尺寸；实机室内可见新居民立绘，尚未留存新肖像对话画面或完成全天行走验收。鱼图标仍为初版。

## 验证证据与边界

- 10组静态检查通过：24图、56出口、8季节设施动作、129日程落点、162双语键、任务链/鱼池/订单及三段音频和独立环境配置。
- 使用本机真实游戏类型严格反序列化32条数据记录，SMAPI原生解析24张TMX及Action实例属性通过。
- 最终0.4在本机1.6.15/SMAPI4.5.2/CP2.9.1启动，原生读入ArcticQA保存文件；三处isTileFishable=True，同处水碰撞=True、抵达点=False。
- Mac已解锁，此轮独立桌面实测F6依次进入全部六地点。真实日志逐地点确认randomAmbience=False，Town/Harbor/Icefjord为CoastalWind，Tundra为TundraWind，两室内为IndoorWind。证明引擎选曲与开关生效；没有录下设备输出，不能把日志当作听感主观验收。
- 真实键盘在峡湾观测栈道行走，常用镜头内可见近冰；苔原完成局部行走，尚未完整走过木桥。曾在本轮早期工具画面见到抛竿线/浮标，但持久截图没有保留该状态，因此不列为可复核投竿成功证据。最终投竿尝试截图只有动作帧，不声称已落钩或钓获。
- 最终实机图为previews/InGame_Town_040.png、InGame_Icefjord_040.png、InGame_Tundra_040.png、InGame_Guesthouse_040.png、InGame_Fishery_040.png；Harbor_040为本轮前一运行画面。旧图和intermediate文件均有版本说明。
- 未完成完整六步交货、每日订单真实扣鱼入账、睡醒/保存重载、全日NPC和多人。原0.2键盘镇→港→镇、中文航线牌、原生门动作完成入住和鱼池采样结果保留。
- 原始证据docs/SMAPILoad_040.txt、NativeSession_040.txt、DesktopSession_040.md、StaticTestResults.txt、NativeTestResults.txt。启动仍有Steam未加载成就不可用、缺ContentHashes及联网更新检查失败提示；不是零警告结论。

## 接续优先级

1. 在正常游玩环境完成六鱼真实钓获和主线交货→扣材料→睡醒→设施/航线解锁，检查订单钱包/鱼堆/库存与重载；床铺醒来地点。
2. 继续实测桥面和室内柜台交互；三居民肖像对话、正常时钟全天跨图、礼物/中文排版。预览固定12:00跳过早间日程，不能用于全天行走结论。
3. 统一港口、峡湾暖色春季植被；检查冰山各季节地理与画面比例、近景遮挡、夜间灯光、环境动态、鱼图标；提升声景听感并完成原创旋律配乐。
4. 雪橇、动物、极光、节日、其余地区/居民和十章主线均仍待实现，不把阶段美术重制当作全任务书完成。

## 本机环境与关键规则

- 根目录 北境航路.app 自动载入指定 ArcticQA_451755789，中文、时钟固定正午；启动北境航路·正常游玩.command 使用 .development/PlayableMods，无QA。两个入口依赖本机原版游戏资源与工作区.development。
- 预览源码 .development/QA/ModEntry.cs，编译后DLL在.development/TestGame/Mods/ArcticQA，源码同步tests/RuntimeFixture。F6顺序Town→Harbor→Icefjord→Tundra→Guesthouse→Fishery。
- 原生 SaveGame.Load 后必须清除 TitleMenu，等待SaveLoaded/Context.IsWorldReady再warp；否则残留标题盖住场景。
- Water=I保留水域关闭原生蓝色叠层；Buildings不覆盖水格。Action同时写TileData图块实例属性，原生NPC updateDoors才识别；Town doors=3 / Icefjord doors=1。
- CP新增DynamicToken定义需重启；普通资源可reload。季节地图用MapSeason动态令牌，在原生创建地图早期回退spring。
- PNG需和TMX同目录。ContentPack由生成程序重建；直接手改导出文件会被覆盖。
- SDK .development/dotnet；DOTNET_CLI_HOME=.development/cli，NUGET_PACKAGES=.development/nuget。
- Pillow/NumPy Python：/Users/moonmoonbird/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3。
- 旧入口在.development/legacy-launchers；说明以根目录“从这里开始.md”为准。父Desktop是含个人文件的Git工作区，不要全局git add/status扫入无关内容。

- 音频由tools/build_audio.py独立构建；普通内容构建不重生成WAV。Data/AudioChanges的FilePaths必须用CP AbsoluteFilePath令牌，不能写入本机绝对路径。
- 室内床(4,7)、床前(4,9)；收购站售鱼(8,6)、订单(15,6)，原生实例属性与Back睡眠属性均需保留。

## 0.5 开发中（当前未归档）

目标已作为持续goal激活，完整范围见CompletionMatrix.md，不将0.4或第一阶段缩成最终完成。上一goal前的0.4轮次属于实质进展。

2026-10-17继续：新增专用ArcticQA原生集成夹具IntegrationAudit.cs，仅测试角色。原生OnWarped/OnItemOfferedToNpc证明六步任务依次完成、扣鱼/40木/2铁正确、重复交货不重扣、交货对话实际设置材料标记。原生Sleep_Yes→完整新日→自动原生保存→旅舍4,7醒来通过，次日Shed/Boat及奖励邮件到达。航线真实Action抵达峡湾且触发后续完成。原生商店purchase方法证明三订单273/202/84g到账和扣鱼、同日重开无补货。它们是API集成验证，不是鼠标游玩通关；真实钓获和日志领取金币仍未验证。

重要新发现：实际退出引擎再重载后，钱包1059、六步完成、四施工标记和旅舍床位保留，但原生个人商店库存恢复3份，重复交单漏洞成立。证据NativeCoreAudit_040_reload_failure.txt。已在生成源为订单增加带Year/Season/Day的原生mail持久标记，仍待最终回归；不要标为修复验收通过。

晾鱼架功能制作中：tools/build_processing.py新增纯原生BigCraftable/Machines/CraftingRecipes、3风干产品、2夜无燃料/1.4倍基价/保留品质及独立图纸邮件补发（兼容已修棚0.4保存文件）。source与提示词drying-rack和dried-fish-products已保存；内置imagegen原创，导出仅尺寸规范化。生成后38真实类型/24地图解析通过；实际加工/过夜/重载和图纸学习待验。尚未更新发布版本与包。

当前QA新增F7可传送米拉相邻10,13，随后正常交谈用于桌面肖像验证；不调用菜单点击函数冒充UI输入。CLI游戏运行不在CUA应用清单，完成原生API验证后再启正式app做桌面。
