# 0.3 桌面验证接续记录

2026-10-16 02:00 一次续作。

开始阶段 CUA 成功绑定北境航路应用并 Raise；真实窗口仍为0.2中文渔港、玩家和HUD。为更新专用QA模块，使用真实 Cmd+Q 关闭游戏。

再次通过桌面应用入口启动时，CUA明确返回：The Mac is locked and automatic unlock could not unlock it. Ask the user to unlock the Mac manually before continuing.

因此停止桌面操作，没有尝试绕过系统锁屏，没有修改锁屏或睡眠设置。本轮没有保存新的 Icefjord / Tundra 实机截图，也没有真实键盘抛竿记录。previews 中新野外普通图均为 TMX 合成/导航校对；InGame_ 前缀仍是上轮真实截图。

独立测试游戏可在后台原生加载，因此继续完成数据/TMX与原生场景、水域、碰撞、返程动作验证；这些 API 检查不能替代桌面操作。原生记录见 NativeSession_030.txt。

下一次 Mac 解锁后：从北境航路.app启动，Raise窗口；预览按 F6 循环到峡湾/苔原，核对新美术与角色尺度、真实走通木桥和返程栈道；选背包第6格竹竿（若原背包布局不同则按实际位置），在海边实际抛竿；捕捉 previews/InGame_Icefjord_spring.png 与 InGame_Tundra_spring.png。F6本轮只完成编译，尚无按键实机通过记录。
