# 独立桌面复核 0.4

日期：2026-10-17，上海。使用CUA控制北境航路.app真实游戏窗口，游戏1.6.15、SMAPI4.5.2、CP2.9.1。中文，ArcticQA专用保存文件，预览固定12:00与0.75缩放。

实际启动并按F6依次进入Town、Harbor、Icefjord、Tundra、Guesthouse、Fishery，日志每次warp与音轨对应；最终运行01:32进入Town，01:35Harbor/Icefjord，01:38Tundra，01:39Guesthouse，01:40Fishery。文件SMAPILoad_040.txt保留完整加载与状态。该时钟是本机日志时间，不声称每个画面是不同游戏日。

在峡湾实际向东步行，镜头从入场观测台移到东边缘，可看到新近冰主体；小镇初见镜头也能看到港外近冰。苔原局部步行，没有完整过桥。F6是预览跳转，不代表正式航线已经解锁。

两室内初次画面偏紫，追查原生默认indoorLightingColor后添加AmbientLight和AmbientNightLight。重建并重启后，旅舍和收购站恢复木色、暖炉与冷窗色，保存最终截图。夜间尚未操作验收。

| 文件（previews目录） | 真实内容与边界 |
|---|---|
| InGame_Town_040.png | 最终小镇春季抵达镜头，36,23，新裸岩/碎石和近冰 |
| InGame_Harbor_040.png | 0.4第一运行港口，未改其春季主图 |
| InGame_Icefjord_040.png | 最终近冰42,27，入场观测台；部分顶面仍被HUD遮住 |
| InGame_Icefjord_cast_attempt_040.png | 向东走到平台边后的投竿动作帧；没有浮标/鱼获，不作为成功落钩证据 |
| InGame_Tundra_040.png | 新春季苔原裸岩/低植被的实际入场镜头 |
| InGame_Guesthouse_040.png | 最终照明修正后的旅舍，米拉和罗安新精灵可见 |
| InGame_Fishery_040.png | 最终照明修正后的收购站，艾达新精灵可见 |
| InGame_Icefjord_040_intermediate.png | 本轮冰山位置调整前的中间帧，非最终布局 |
| InGame_Tundra_030_baseline.png | 本轮开始时旧0.3橙色植被对照 |
| InGame_Icefjord_030_rod_selected.png | 旧0.3持竿/选竿画面；原先cast命名已纠正，未保留浮标 |
| InGame_Town_spring / Harbor_spring / Harbor_route_notice | 历史0.2真实截图 |

本轮早期工具图像曾显示抛竿线/浮标，但保存截图时该状态已结束。最终尝试因朝向/工具输入未留存有效入水状态，诚实保留为未验收，不以API水域判定替代真实钓获。新肖像资源加载和精灵可见不等于肖像对话验收；多次交谈定位未留下对话框，仍待复核。完整主线、订单结算、过夜/存档和多人均未验收。

全部PNG为真实窗口截图，未做合成或修饰。普通地图预览不列入此表。CUA偶尔返回timeout/noWindowsAvailable，重新绑定后同一游戏仍可操作，日志没有对应崩溃；较长的单次按键比一串短按可靠。没有更改锁屏/系统安全设置。
