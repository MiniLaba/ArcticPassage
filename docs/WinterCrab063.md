# 冬季港口蟹笼验证 · 0.6.3

2026-10-18。本轮从独立ArcticWinterQA_451755789载入真实冬6日，再走原生睡眠进入冬7日、保存并重启载入。源春季ArcticQA仍为春6日，普通玩家存档未参与。

## 已有证据

- 冬季CP实际展开ap_crab_winter，六地图都加载winter贴图；原生蟹笼限制与岸边步行格联合筛选出港口12处位置。峡湾冬季0处是岸冰关闭状态，雪蟹冬季改在港口。
- 普通710物品通过原生placementAction转换为CrabPot，投入真实鱼饵，原生日更获得雪蟹，checkForAction收取恰好增加一只并清空笼。最初夹具错误地将普通物品直接强转CrabPot，已修复；NativeWinter_063_before_fixture_fix.txt保留该夹具失败记录，不是生产内容包故障。
- 另留(32,13)就绪笼，用F11仅定位到(32,12)，S朝下、X实际收取。02:07:38的InventoryChanged记录加入SnowCrab×1，就绪气泡消失，背包第九格出现雪蟹。真实截图InGame_WinterCrab_ready_063.png、InGame_WinterCrab_collected_063.png。该笼由API日更准备，不能用它单独证明睡眠过夜。
- 随后在12个可达水格放置空且已投饵的笼，通过F12启动原生旅舍睡眠→新日→保存；进入冬7日，12笼全部就绪，6只雪蟹、6份原生垃圾。NativeWinter_063_overnight.txt记录。F12触发的是QA原生睡眠调用，不是玩家从家走到床的整段键盘流程。
- 保存XML独立检查确认冬7日、12个CrabPot、readyForHarvest=true与6个SnowCrab；原春季QA日期保持春6。WinterSaveState_063.txt。
- 退出并重启游戏，winter-reload.enabled跳过重新放笼/配方测试，原生SaveGame.Load后仍为12笼、6只雪蟹、冬季鱼池；NativeWinter_063_reload.txt。重载阶段没有重新注入雪蟹。
- InGame_WinterCrab_next_morning_063.png显示实际冬7日06:00在旅舍醒来；InGame_WinterHarbor_walk_063.png是重载后的冬季码头步行画面。

## 重载后的步行与按键收取

重新载入后，从F6港口抵达点(24,23)出发，D到(36,23)、W到(36,12)、A到(32,12)，S朝下、0选择空格、X收取(32,13)笼。F5只读日志记录位置和方向；没有F11定位到笼边，也没有重新注入渔获。背包雪蟹由1变为2，就绪气泡消失，实拍InGame_WinterCrab_reload_collected_063.png，完整日志NativeWinter_063_reload_walk_collect.txt。该阶段未再次保存，冬季副本磁盘仍为刚过夜的12个就绪笼。

## 继续核对

尚未验证秋冬交界时原峡湾已放置的笼如何处理，以及春/夏/秋的实际捕获保存；七种钓竿鱼的完整小游戏和普通新角色多日流程仍待验收。

冬季副本只用于测试；结束时关闭两个QA开关恢复默认春季入口。生产内容包无QA DLL，普通游玩入口不含这些快捷键。

测试结束游戏正常退出，两个QA开关已关闭，双击入口恢复原春季专用预览。原生鼠标左键事件在桌面工具点击（含900毫秒按压）时未出现，F5所读鼠标位置固定；商店鼠标出售仍不能记通过。短于约250毫秒的某些按键没有被游戏采样，方向/交互使用400—450毫秒并读取状态更可靠。上述为本次工具环境观察，不是游戏控制要求。
