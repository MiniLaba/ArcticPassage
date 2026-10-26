# 本机预览与原生验证夹具

只用于隔离开发环境，不属于生产内容包。自动载入专用ArcticQA_451755789，语言中文、缩放75%、时钟固定正午。角色不存在时保留标题菜单；其他玩家不应用预览修改。

主源码为本目录，目标net6；项目GamePath默认指向工作区.development/TestGame，可用MSBuild属性覆盖。设置DOTNET_CLI_HOME和NUGET_PACKAGES到工作区后构建ArcticQA.csproj，将DLL与manifest复制到.development/QA/InstalledArcticQA。2026-10-20已把QA从默认TestGame/Mods迁出；PreviewMods/ArcticQA链接到该目录。正常应用默认目录和PlayableMods均不含QA，发行安装包不带此DLL。仅「启动霜灯港·开发预览.command」显式使用PreviewMods。所有*.enabled测试旗标也改放InstalledArcticQA；不要按历史日志路径重新把QA装回默认Mods。

- F6：循环六地点；0.4已桌面验证，0.6新图还需实际镜头验收。
- F7/F8/F9：米拉对话、晾鱼架收取、收购柜台的相邻定位；定位不等于互动已通过。
- F10：仅定位旅舍料理台；不是旧版季节快捷键。测试临时季节应在控制台连续输入ap_preview_season winter和patch update，5秒后检查日志真实scene文件名。单改日期不会自动刷新Content Patcher的日级令牌。此方法不保存，不代表自然季节过夜转换已验收。返回spring后退出，不保存临时季节。
- ap_qa_maps：原生地图/门/人物，港口33,20、峡湾39,37、苔原41,20水域探针及落点碰撞；冬季另外检查岸冰不可钓。新探针位于四季都开放的西/南水道。
- ap_audit_environment：旧存档载入后地区标识、天气隔离；四季各256次原生预报与天气复制。使用临时LocationWeather，finally恢复原季节，不保存。
- ap_native_interact X Y、ap_native_fish：原生地图动作和鱼池API；不能当作鼠标点击或钓鱼小游戏成功。
- ap_audit_delivery、ap_audit_fjord、ap_audit_orders、ap_audit_stock N：实际任务/交货/航线/商店核心逻辑，仅ArcticQA。delivery会重置该测试角色相关任务与材料，不能随意重复用于已有验收状态。
- ap_audit_sleep：通过真实十分钟更新到22:00，再调用原生睡眠和新日保存；会保存专用测试角色。
- ap_audit_processing：制作、输入、品质/价格、错误输入和三架测试机器，会重置三架状态。ap_audit_compatibility：六鱼熏鱼机/鱼饵机、售鱼筛选、图纸信原生解析。
- ap_audit_collect：原生收取两架已完成产品，中间一架留桌面实际收取。ap_audit_save：真实SaveGame.Save；只用于明确要持久化的测试状态。

所有API结果与实际桌面证据分开记录。SMAPI不允许反射内部CommandManager，已经移除该尝试；不要通过其他机制绕过它，直接使用公开patch update命令。


## 独立冬季测试

测试目录中的winter-preview.enabled只影响QA，改为载入独立ArcticWinterQA_451755789；原春季ArcticQA_451755789和普通玩家存档保持原样。冬季副本日期来自本地复制的XML，只替换根currentSeason后通过正常SaveGame.Load载入，不拿临时鱼池类型替换证明冬季CP令牌。

- 自动AuditSeafood检查真实冬季贴图、港口ap_crab_winter与12处原生可达水格；封冰峡湾没有贴岸水格是预期关闭，不修改海冰为步行地面。
- PrepareWinterPot通过原版Object.placementAction把普通物品710转换为CrabPot，投入真实鱼饵，运行原生日更/收取逻辑；留下一个原生捕获的就绪蟹笼给桌面操作。F11只定位，仍需实际X收取。该步骤单独不能证明正常过夜。
- F12仅在冬季专用副本调用BeginWinterOvernight，先断言Game1.GetSaveGameName(false)==ArcticWinterQA；在12处可达水格放置空的已投饵蟹笼，进入原生旅舍睡眠→新日→保存。操作会写冬季测试副本，不可用于原春季存档或正常人物。
- winter-reload.enabled令测试启动只核对重载状态，不重新放笼/注入食谱。读取保存的测试标记，验证日期、全部就绪笼、雪蟹与垃圾结果；必须单独检查持久化文件和重启日志。
- 测试结束删除这两个QA开关文件，恢复默认春季预览。测试状态与证据均不得冒充鼠标键盘从零游玩。

## 独立秋冬回收测试

recovery-preview.enabled优先载入ArcticRecoveryQA_451755789（备份的秋28基线）；首次载入放三状态峡湾笼和同时适用于秋/冬的港口空笼。F12仅该存档允许原生过夜保存；捕获快照在原生日更之后、生产模块回收之前取得。金星蟹堆叠是预设夹具，不能当作真实捕获。满箱测试与原版地点对照在同一隔离角色执行。

保存后加recovery-reload.enabled，退出重启只核对日期/箱子/港口对照，不重新注入。F11只定位箱子，W/X才是实际打开。结束关闭两旗标恢复春季。开启生产运行模块时SeafoodAudit只测试当前真实日期；运行模块会主动纠正模拟过季标签，旧版2048次临时类型抽取仍仅为历史证据。

0.7.1新增F4仅定位补给柜台；F5记录只读背包/金币/配方，菜单变化和鱼竿状态变化自动记录。不会自动购买/提竿或强制捕获。正式键盘柜台在运行模块中，QA不实现交易功能。


## 雪块模型隔离检查

`shelter-preview.enabled`只放在独立QA暂存目录并使用开发预览入口；读取ArcticWinterQA，临时命名ArcticShelterQA，准备冬季站位且冻结时钟。检查真实地图动作及游戏菜单控制处理器：非冬、错放、取消、三层完成、重玩、失效日期／季节与钱包／背包不变。处理器由反射调用，不冒充桌面按键；另以CUA真实按键实拍。测试不保存，退出后关闭此开关，普通入口不含QA。详见docs/SnowShelter_R02.md。
