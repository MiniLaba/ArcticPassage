# R03 固定安全冰钓候选

2026-10-23，既定冬季特色范围。生产实现IceFishing.cs，生成器build_ice_fishing.py已接入build_content.py；未增加地图或改变原海冰通行性。

## 实际玩法

冬季修船开通峡湾后，在木平台(40,34)朝南，手持十字镐与(40,35)标记互动。约1.4秒凿冰，随后朝东短投到(41..43,34..35)。当日有效，隔日需重新检查。北极鳕可用训练竿；比目鱼要求钓鱼4级且训练竿不适用。原生鱼池仍可能抽到垃圾。只有房主可清理，房主日期状态供其他玩家共享；多人尚未实测，不声称多人通过。

## 已验证与边界

- 生产构建0警告0错误：IceFishingBuild_R03.txt；夹具0错误、1条既有RepairAudit可空警告：IceFixtureBuild_R03.txt。
- 57实际数据记录/52真实TMX解析：NativeIceFishingParser_R03.txt。内容/经济/声音隔离既有定向检查：IceContentValidation_R03.txt。
- 原生API夹具：全图4032格可钓性只有6格变化；6格清理前后均碰撞阻挡；错误工具不开放、延时前不开放、冻结结束；普通竿0级/4级、训练竿4级分别500次原生鱼池选择符合种类与等级限制；逻辑日期改变即失效。见NativeIce_rules_before_keyboard_R03.txt。抽取不是实际小游戏钓获，逻辑改日不是原生过夜。
- 初测误把FishingRod(1)当普通竿，实际为训练竿，比目鱼测试失败，完整保留NativeIce_first_training_rod_R03.txt。已改明确BambooPole并独立测训练竿，没有放宽生产限制。
- 最终桌面：实际X执行地图动作凿冰，实拍InGame_R03_ice_cleared.jpg；按1选择训练竿、C短投，原生fishing=True，后续nibble=True，实拍InGame_R03_ice_native_cast.jpg。角色ArcticQA、工具/技能/位置与冻结时间由测试准备，目标保存名改ArcticIceQA，未请求保存，不是普通角色到达或解锁。
- 最后会话完整日志在CmdQ退出后对已退出app继续获取状态导致正常入口重启，被SMAPI覆盖；保留较早完整规则日志及现场已输出追踪摘录NativeIceFishing_R03.txt，不补造缺失日志。正常入口5模组标题实见；该启动日志NativeIce_exit_normal_entry_R03.txt保留。以后退出前先复制日志，不对退出app获取状态。

## 尚待

普通新角色解锁到达；冰洞原生小游戏钓获入包；真实过夜/同日保存冷载/跨季；手柄与鼠标；主客机同步。R03犬橇与四步解锁链未完成，整包未结项。原始普通角色本轮检查点为RepairNormalDay11_R01.json，旧档未编辑。
