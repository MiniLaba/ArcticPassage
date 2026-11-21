# R01 键盘购买后原生入包

2026-10-26。KeyboardCounters在键盘Enter购买成功且仍位于同一个原生商店、无子菜单、heldItem非空时，查找背包已解锁空格，调用该格的原生receiveLeftClick完成安放。不直接向Items赋值或调用发物API；价格、库存、配方和交易由原生商店负责。满包时保留手持物品及原有Tab背包操作，不自动扔掉、卖出或替换已有物品。鼠标购买路径保持不变。

本机运行构建0警告0错误；正式暂存DLL与Release逐字节一致，SHA256 a62ce43b56db70059583ac4d40315227a8bd824e07ff746fcb9043a16957a949。默认系统Python缺PIL的首次构建未运行完成；换既有项目Python后完整构建通过。未安装新依赖、未开启QA。

普通5模组、无QA角色春18／530金，实际步行到材料柜台、X打开原生商店、Tab与方向键选择500金竹竿、Enter购买。15:11:58日志记录native stow (T)BambooPole slot=8 held=none、钱包530→30；随后Esc关闭商店、K手记与正常移动有效。步行回旅舍，实际床位/Y，15:13:53保存到春19／30金。次日原生背包实拍可见竹竿，铁材已用完，煤9、唯一机票1仍在。只读存档钓鱼1级、经验268，未修改技能。

证据NativeBamboo_stow_day19_R01.txt、RepairNormalDay19_R01.json、InGame_R01_bamboo_sleep.png、InGame_R01_bamboo_day19_inventory.png。重新启动普通入口、实际载入后背包确认竹竿仍在，春19／30金，煤9／唯一机票1；目标存档SHA未变。冷载证据NativeBamboo_day19_cold_R01.txt、InGame_R01_bamboo_day19_cold_inventory.png。满包、可堆叠批量购买、配方及换物未针对本次新行为逐一桌面复验，不扩大为全部商店通过。此前输入未响应在非商店场景也出现，根因未确定，不宣称原生入包优化修复了所有桌面输入。
