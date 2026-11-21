# 0.7.7 月月鸟航空初访

2026-10-20。按用户最新要求，将初访故事改为月月鸟邀请农夫探索、感受北极，附赠月月鸟航空往返机票。基础航空初访提前并入M1；完整主线和总体规划继续保留。新美术均由代码绘制，未调用生图。当前是可玩的首版，飞机、雪原与航站材质仍需提高，不能称达到大奖品质。

## 玩家流程

读农场邮箱的邀请并领取原生机票附件；邮箱旁可按G使用原生邮箱。步行至巴士站按B查看个人登机牌、Enter登机、Esc取消。山谷至机场的接驳由文字交代，未改造原版巴士站为实际起飞跑道。

24秒分层动画：冰峡湾巡航8秒→下降6秒→雪跑道滑行6秒→停机4秒；螺旋桨转动、发动机渐变与触雪粒子。Esc在开始0.5秒后可跳到相同机场，手柄B为实现但未实测。原生单人时钟在菜单动画内暂停。返程目前采用登机确认后原生转场，未制作独立返航演出。

降落Airstrip(25,26)，沿南侧四列步道进入Town(27,2)，沿主路到红色旅舍；入住接续同一个Arrival/FirstCatch原生任务。镇东侧原返程牌(40,24)改为免费机场接驳，机场B、Enter返回BusStop(12,9)。原版沙滩自动传送删除，海港至峡湾船运仍保留。

## 兼容及边界

旧地点、物品和六步任务标识保持。旧Invitation邮件记录保留；新AirlineInvitation使用独立一次性标识，因此已经读过旧信的角色也能获得新票。旧版尚未读的邀请可能与新信并存，旧信无附件、新信只附一票；本轮现成正常存档属于此升级情形。全新角色仅新航空邀请由触发器发出，已做数据检查，尚未另外再建一个新角色实测。

实体机票不消耗、无售价、不可送礼或丢弃；读信后的预约记录用于登机，防止背包满或票放入箱子导致软锁。满背包领取仍使用原生邮件/取物流程，未单独实测。只支持单人航空，联机显示未开放提示。无授予渔获、技能、材料或金币的开发快捷操作。

雪原机场64×40、四季4图，属于镇外较高雪原的虚构设计；不代表格陵兰所有机场全年雪跑道。航站小屋仅外观与说明，内部、完整航空人员/时刻/天气系统后续实现。手记现六区路线、五处原自然观察点，未用机场凑科研记录。

## 实际桌面证据

本机游戏1.6.15 / SMAPI4.5.2 / CP2.9.1，正常入口5mods、无QA。独立角色FrostNewQA/FrostTest由原生新建菜单建立，未用API创造角色或传送。本轮使用其原生春3/450g存档，普通行走、按键读信、领票、登机、入住和睡眠。

| 项目 | 结果与证据 |
|---|---|
| 邀请及原生附件入包 | 实际打开新信、看到票、原生关闭信后领取；InGame_Airline_letter_ticket_077.jpg |
| 巴士站登机牌 | 玩家姓名、航线、Enter/Esc；最终按钮文字在框内，InGame_Airline_checkin_final_077.jpg |
| 完整24秒飞行 | 21:58:37开始，8/14/20秒四阶段，21:59:01完成、21:59:02原生落地；NativeAirline_077_final_flight_save.txt |
| 原始飞行实拍 | previews/flight077/frame-00至19，时间见FlightFrames077.json；InGame_Airline_flight_native_077.gif是这些真实截图的抽帧回放，不是直接录屏或离线模拟 |
| Esc跳过 | 22:00:06开始，22:00:07跳过，22:00:08同一机场安全抵达；InGame_Airline_skip_landing_077.jpg |
| 南步道进镇 | 22:00:29普通S步行触发Town；K实际记录Town27,8，继续主路进入旅舍，InGame_Airline_guesthouse_077.jpg |
| 原生过夜保存 | 22:04:23—24保存无异常，春4/450g/旅舍床4,7；InGame_Airline_saved_day4_077.jpg |
| 退出冷重载 | NativeAirline_077_reload_return.txt真实加载春4；K已显示后续三条毛鳞鱼任务，InGame_Airline_reload_day4_077.jpg；无邀请触发再次执行 |
| 镇区接驳及返程 | 从旅舍普通步行至镇东牌、X接驳机场，再B/Enter免费回BusStop，S普通步行可见角色和工具栏；InGame_Airline_return_walk_077.jpg。返程转场完成前短暂不绘制角色/工具栏，完成后恢复，未另写原版显示状态 |
| 磁盘保存核对 | report_airline_save.py只读核对春4、450g、票1张、新邮件1条、AirArrival=1；Arrival完成待领150/FirstCatch春单未完成400；原版9/13任务保留，四份旧QA日期余额保持。AirlineSaveState_077.json |

曾发现的失败保持记录：首轮机场步道x25/28边缘未接出口，能走出40格地图至y53。已补齐四列边缘，并加入四季全可走边缘必须有出口的回归检查；上述最终实走为修正后的版本。NativeAirline_077_boundary_found.txt不可当通过日志。原InGame_Airline_flight_077.jpg实际是首次落地图，已更名InGame_Airline_landed_first_077.jpg；真正飞行帧在flight077。

另外更正早前正常建档记录：首次正常首夜到春2后，等待期间未成功暂停，角色在21:10:43自然昏倒保存到春3/450g，原生莱纳斯邮件已观察。因此春4不是三个完整游玩日；正常新角色多日主线、全部鱼种仍待。未改旧玩家存档。

## 构建及后续

AirTravelBuild_077.txt：0错误/0警告；SDK另有CSSM_ModuleLoad提示。AirTravelContent_077.txt：15组内容检查；AirTravelNativeData_077.txt：本机真实52记录/36TMX；AirTravelGuide_077.txt：20观察锚点与103运行双语键；AirTravelContracts_077.txt：一次性信件/机票/无沙滩传送/机场所有可走边缘有出口。它们是结构/API检查，不代替上表游玩证据。

保留原ContentHashes/Steam成就警告及联网检查失败（若出现），不宣称全日志零警告。声音循环已原生加载、完成/跳过时释放，听感和声景混音尚未定稿；英文、小窗口、满背包、其他季节实走和多人未通过。下一步回到M1真实钓获交货、多日建设流程，同时打磨航空美术与初到教学。

## 现实参考与代码资源

参考[De Havilland Twin Otter](https://dehavilland.com/twin-otter/)、[厂商特殊任务配置](https://dehavilland.com/defence/)中的轮式/滑橇/浮筒适应性及[Air Greenland机队](https://www.airgreenland.com/about-us/the-fleet/)的北方航空语境。飞机为本项目虚构月月鸟涂装，不声称真实航空公司或完全复刻某机型。

生成程序tools/build_air_travel.py；运行Code/ArcticPassage/AirTravel.cs；六张独立PNG/原生WAV存Runtime/assets/flight。原地图生成器末尾调用航空生成器，重建后仍保留航空邮件、机场与接驳。只分发本项目自己的程序集。
