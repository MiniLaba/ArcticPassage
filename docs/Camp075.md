# 0.7.5 苔原营地与研究站

2026-10-20。开发预览；本轮交付一个可往返、可住宿、可保存观察记录的新区域，不代表全任务书完成或美术目标已经达到。

## 路线和实际功能

镇区北口→苔原→中段东侧木桥→桥尽头营地。Tundra54,23/24进入WinterCamp2,24；营地0,23/24返回Tundra53,23，抵达点错开出口，避免反复传送。营地31,24正门交互进入ResearchStation12,14，室内12,17南口回营地31,25。室内3—5,7是原生Bed/TouchAction Sleep；桌前17,8可读说明。

营地64×48、研究站24×18，均四季，增加8图。营地为无开放水域的内陆岩地，没有额外鱼池或虚假的冰钓。冬季两座圆顶雪屋仅展示，其他季节换帐篷；住宿使用木屋。没有新增NPC、研究奖励、机场或解锁章节。

K路线增加第五块实际季节场景；研究站橙框归属营地。第五笔记camp观察点19,37，记录距离仍不超过2格；保留原四点key和原始日期。旧3/4将正常显示3/5，不重置已记内容。20张缩略图来自实际发布贴图。三处夜灯使用现有黄昏渐变，尚不是极昼/极夜系统。

## 美术与现实依据

总体图的连贯聚落、岩坡、冬季雪屋是方向。现有地点ID、已有NPC和鱼池优先兼容，本轮接在苔原木桥，实际邻接不等于把艺术总体图方位与比例完整搬入引擎。

[Visit Greenland 的建筑介绍](https://visitgreenland.com/activities/architecture/)说明了彩色房屋与坡地，也区分地区性雪屋传统和现代住房。营地因此保留有工作用途的木屋，把雪屋限定为冬季展示，没有把它们当成所有北极居民的日常住宅。[Pitquhirnikkut Ilihautiniq / Kitikmeot Heritage Society](https://www.kitikmeotheritage.ca/inuinnaitstonehouse)的Inuinnait资料区分历史上的冬季雪屋、夏季皮帐篷和更早的石屋。本游戏现代帆布野外营地只是受季节变化启发的虚构安排，不声称是历史建筑复原。

代码绘制路线、雪屋/帐篷、气象杆与标志；环境材料通过确定性最小接缝组合复用本项目已有四季苔原岩岸，研究站外观复用本项目镇区季节木屋，室内复用原有木屋基底后补纸质日志与样本。素材来源仍见CREDITS，未下载参考照片制作贴图，未改源图，未新增生图调用。过程中的扁平初稿因与现有场景差距过大被替换；雪屋、帐篷和新道具仍是需要继续精修的资产，不是获奖品质证明。

## 真实桌面证据

使用本机1.6.15与SMAPI4.5.2，生产包0.7.5。测试副本与普通新角色严格区别：最初营地测试开关只把独立QA角色放在Tundra50,23；之后都是普通方向键和X/R/Y交互，不自动交货、记录或睡觉。

- 春8实际跨区、走到18,36、R记录camp，随后研究站睡到春9。首轮全文日志被一次桌面读取意外重启覆盖；保留了初稿截图和后续春9真实冷读日志NativeCamp_075_reload_before_art.txt，不把转录工具观察冒充原始日志。
- 冬7独立WinterQA：普通按键Tundra→Camp→Tundra→Camp，实际到18,36雪屋旁并进入研究站，桌前17,8打开本包说明。NativeCamp_075_winter.txt、InGame_Camp_winter_final_075.jpg、InGame_ResearchStation_final_075.jpg、InGame_ResearchStation_desk_075.jpg。冬季未保存。该轮桌面输入一度失去焦点，Raise恢复；不要重复启动多个实例。
- 最终Flow春9以原生SaveGame.Load从研究站4,7加载，旧三项和营地记录均在；研究桌X打开、Enter通过原生receiveLeftClick翻页关闭，CanMove恢复。实际南口离开到Camp31,25，春季20:30后3灯夜景通过；K路线图例重叠修正后的实拍已留。随后再次普通进入研究站、走到4,7、Y确认睡眠，02:00:03原生SaveGame.Save完成，春10/1683。NativeCamp_075_final_sleep.txt、InGame_Camp_notice_enter_075.jpg、InGame_Camp_night_075.jpg、InGame_Camp_routes_final_075.jpg、InGame_ResearchStation_sleep_final_075.jpg、InGame_ResearchStation_nextday_075.jpg。
- 最终退出再冷启动，原生加载春10/1683、ResearchStation4,7、4/5笔记，原始日期不变。NativeCamp_075_reload_final.txt、InGame_Camp_reload_final_075.jpg。冷读后不再保存。
- 最后检查修正了夏季取样带入池水、但地图没有对应钓鱼水域的问题：按原生Water元数据过滤材料候选，重建四季地表及缩略图，未改动通路。再次冷载冬7副本、实际跨入营地、走到18,36，最终冬季实拍和五区路线截图已更新，NativeCamp_075_winter_final_art.txt。夏秋实际行走仍未验收，不能因贴图修正就记作通过。

纯说明牌Enter只在本包两个营地地点、匹配三条本包文字、非问题框、非NPC对白时使用，调用原生翻页/退出，保留原生安全等待与打字行为。没有强制关闭或自动回答睡眠框；最终Y睡眠仍是原生流程。原版鼠标受本机桌面工具限制未全部验收。

## 自动检查与保存边界

StaticTestResults_075.txt：15组通过，32图、80出口/门、129NPC落点、191内容双语键、原有鱼池/机器/订单/气候。NativeTestResults_075.txt：本机真实数据类50记录和SMAPI32TMX解析。validate_guide.py：20四季观察锚点、20缩略图、72运行双语键。运行模块构建0警告0错误。

report_camp_save.py只读三份测试存档，CampSaveState_075.json：Flow春10/1683、lastSleep=ResearchStation、camp首次春8/18:40和三条春7原日期；原QA春6/1618、WinterQA冬7/1618均无笔记，未被本轮保存。历史report_guide_save.py是0.7.4春8快照核对器，不适合作为新日期的当前断言。

既有ContentHashes缺失、未加载Steam成就警告保留；冬季日志包含SMAPI联网检查更新失败，未掩盖。没有把API解析当作全季节桌面游玩。夏秋实走、冬季研究站过夜、换季停留/玩家放置物、联机、长线经济、正常新角色多日与其余真实钓获仍待。首批交货目前按原设计沿用接取时的鱼种，跨季可能等待下一适用季；下一轮评估改订当季鱼的体验，同时保护已完成未领的奖励，本轮未改。
