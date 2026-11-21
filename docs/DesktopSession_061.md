# 0.6.1 桌面验证

2026-10-17。本机已安装的Stardew Valley 1.6.15、SMAPI 4.5.2，生产内容包0.6.1，专用预览存档ArcticQA。通过桌面工具启动北境航路.app、发送真实键盘操作和截取实际游戏窗口。F6–F9只用于测试定位，不能代替正常抵达流程。

## 已有证据

- 0.6四室外与旅舍的实际画面：previews/InGame_{Town,Harbor,Icefjord,Tundra,Inn}_060.png；港口左右步行画面InGame_Harbor_walk_060.png。
- 本轮修复前：InGame_Mira_dialogue_before_fix_060.png，米拉对白只显示“}”。原始Load文件不会展开i18n标记，修改生成器为Load空字典后EditData写入翻译。
- 修复后三人真实对话：InGame_{Mira,Ada,Roan}_dialogue_061.png，介绍文本、中文姓名和肖像均可见，新镇名为栖光湾。未因此宣称所有友谊/天气/日期分支已逐条桌面运行。
- 晾鱼架：InGame_DryingRack_ready_061.png → InGame_DryingRack_collected_061.png。F8定位后按W朝向机器、X收取；就绪气泡消失，风干毛鳞鱼进入第九格。日志19:14:01确认真实InventoryChanged事件加入ArcticPassage_DriedCapelin×1。此前两夜加工由原生引擎验证，本次证明桌面按键收取。
- 收购：F9定位后W、X打开原生商店，InGame_Market_before_sale_061.png显示三种风干产品可出售、工具不可售，金币1618。鼠标点击没有触发出售，金币未增加，不能记出售闭环通过。桌面工具显示的指针位置与游戏自绘指针不同，尚未确定原因。
- 港口钓位：从F6落点沿码头实际步行、按6选择钓竿，面向西侧开放水面后按住C蓄力并松开。InGame_Harbor_cast_061.png可见钓竿、鱼线、浮标。未完成上钩小游戏及鱼获入包，六鱼真实钓获仍待验收。

## 保留的边界

本轮是春6日固定正午预览，未做整套四季/夜景桌面验收、NPC全天跨图路径或正常新角色多日通关；未录制系统声音，不以音轨日志代替主观试听。没有保存临时预览互动，不影响正常玩家存档。

完整日志：SMAPILoad_061_desktop.txt。静态资源14组通过，包含新增的三居民翻译加载检查；Data/地图真实类型解析结果另见NativeTestResults_061.txt。

本轮测试已结束，19:48:19游戏正常退出。依用户要求暂停开发及凌晨续作任务。
