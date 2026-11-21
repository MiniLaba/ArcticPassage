# 加工与北线实机验收（2026-10-22）

本次承接固定R01/R02，未扩大十包范围。仍为0.7.8归档后的工作区候选；正常五模组、无QA模块，FrostNewQA由原生新建流程产生，未授予测试物品、金钱、技能或解锁。所有截图是本机星露谷1.6.15／SMAPI4.5.2实际捕获，保留捕获顶部的桌面边条；地图预览PNG另列，不作实机证据。

## 正常角色连续流程

前段三毛鳞鱼实钓、交付400金和木材40份实购600金／交付250金，见NativeR01_firstshipment_play_save.txt与NativeR01_shed_first_conflict.txt。历史FirstShipmentSaveState_R01.json是春6／1060金检查点，不能用于最新余额结论。

春7冷载710金；旅舍写字台原生Mailbox先显示原版Joja清理山体滑坡信，随后原生修棚信附熏鱼机。Escape离信原生自动领取附件。进入镇区一次领取10煤，在旅舍(17,13)实际放下原版FishSmoker；持前一天真实钓获的北极鳕X投入，煤10→9。按普通时钟运行完成后X收取熏北极鳕1。其间步行到镇北黄色社区屋并打开原生厨房；当前角色没有所需食谱，未制作料理。

第一次收购拒收熏鱼，余额710不变，失败保留NativeR01_processing_first_sale_rejected.txt。根因是收购白名单只有category_fish及本包风干鱼，而原版SmokedFish属加工品；增加原版生成的精确ID标签id_o_smokedfish，只改变本地柜台收购范围。春8冷载后，原生柜台出售成功，00:59前后日志实际710→880，背包熏鱼移除，回购区170金可见。未修改原版对象售价、未直接改钱包。

港口修棚前后Load最初同时匹配、两者被CP拒绝；现用HasFlag Shed互斥条件，冷载和实际完工画面通过。开棚事件最初只有EditData，原生TryGetLocationEvents会先DoesAssetExist，故从未请求新资产；补空字典Load后，春8实际进入港口触发罗安三段原生对话，完成恢复原入场位置及移动。春9磁盘eventsSeen包含ArcticPassage_WorkshopOpening。

## 原生北线行走

同一角色春8雪天：镇北→苔原→北端(26,3)→山路(12,42)→站点院落(25,23)→北口→冰川(32,44)→观测台(31,27)。安全牌(30,25)实际打开，Enter关闭恢复行走；前缘与融水不开放进入。原路返回山路(32,2)，沿东口到营地(49,24)，步行进入研究站床位。

01:19:19原生保存完成，春9／880金／研究站醒来；煤9、唯一机票1、旅舍(17,13)熏鱼机保留，无鲜鱼或熏鱼重复。ProcessingFrontierSaveState_R01_R02.json为只读磁盘核对。

完整重建候选后，01:25:59再次正常五模组冷载春9成功，原地研究站醒来、余额880和煤9保留；步行到营地(49,23)朝东X，01:28:01原生Warp回山路(60,24)，01:28:28从山路东口再次返回营地。八区域手记缩略图在原生界面均显示，实拍已存。01:29:38正常退出，冷载阶段未再保存；磁盘仍春9研究站床位。

## 原始证据

- NativeR01_processing_first_sale_rejected.txt：春7加工／社区屋／拒收／春8保存及正常退出，保留已知Steam与ContentHashes环境提示。
- NativeR01_R02_sale_walk_save.txt：春8冷载、出售170、开棚对话、完整北线、春9原生保存。
- NativeR01_R02_cold_reload_return.txt：春9冷载、营地→山路→营地、八区导览及正常退出。
- previews/InGame_R01_{workshop_repaired,workshop_opening,smoker_running,smoked_cod_collected,smoked_cod_sold}.jpg。
- previews/InGame_R02_{community_kitchen,sledtrail_snow,glacier_lookout,glacier_notice,camp_link_arrival,camp_to_trail,eight_region_guide}.jpg。
- previews/InGame_R01_R02_reload_day9.jpg。
- FrontierBuild_R02.txt：完整生成管线、52TMX／128出口、互斥Load／出口边缘回归、导览109双语键及航空回归。
- NativeFrontierParser_R02.txt：本机真实55数据记录、52TMX解析，无未知数据字段。该项不等于实机走过52张四季地图。

## 未通过项与下一步

R01仍缺实际修船、第四连续任务、峡湾闭环、余5种竿鱼／虾／四料理／差异化日单与周单；不能以三个存档日期替代三个完整游戏日验收。现余额880，进口铁锭1000／块且每日2块，原农场／矿井仍是较省钱来源。下一段接实际材料与修船，不重复本次已通过的熏制出售。

R02仍缺雪屋实际互动、居民／服务衔接、其余季节定向实走。山路犬队站明确显示筹备中，没有未注册动作或假交通。新地图美术只属首版：岩脊纹理重复、冰川体积细节和社区屋物件比例需在R09统一，研究站与旅舍的现有相似家具也需区分；没有宣称审美定稿。机场内部不新增。

当前归档仍dist/0.7.8历史包；本机正常双击入口链接工作区候选。十包全部还有未结项，自动计划全部保持取消。
