# 0.7.1 键盘柜台与真实交易

2026-10-18，本机游戏1.6.15、SMAPI4.5.2、CP2.9.1。生产运行模块新增可选键盘导航，仅用于栖光湾收购、补给与日常订单三个原生ShopMenu。Tab启用及切换商品/背包，方向键选择，Enter确认，Esc沿用原生关闭。焦点以青色框显示，帮助行随窗口宽度换行；鼠标按下退出键盘焦点模式，子窗口打开时不处理导航。

Enter经生产模块调用原生receiveLeftClick，库存、价格、配方学习、可出售类型、余额与容量仍由原生商店检查。这是正式交互功能；测试通过桌面工具发送真实按键，不是QA夹具直接给金币或自动购买。F4/F9仅把专用预览角色定位到柜台相邻格，仍需W/X实际打开，不代表从零步行抵达。

## 出售与购买

- 原春6预览存档原有风干北极鳕1份，以Tab/方向键选择背包第7格，Enter售出，1618→1737（＋119），原格清空，原生商店出现回购条目。工具尝试保持1618，重复确认空格保持1737。
- 同柜台实际购买普通鱼饵1份，1737→1732；商品在手时Tab切到背包空格、Enter放入，不再扣钱。证据NativeCounter_071_first_sale.txt与InGame_KeyboardSale_{before,after}_071.jpg、InGame_KeyboardPurchase_071.jpg。
- 补给柜台购买红点鲑汤配方450，1618→1168，真实cookingRecipes登记ArcticPassage_CharSoup；再买煎鳕鱼、虾浓汤各450，1168→718→268，三个正确ID均出现在只读账目中。第四份炖鱼土豆配方450在268余额下拒绝，金币不减且未学会。
- 上下键把焦点移过初始4行，实际显示到油、韭葱等后续商品；买走食谱后剩余列表的焦点正常。证据NativeCounter_071_recipes_and_fishing.txt、InGame_KeyboardRecipe_071.jpg、InGame_KeyboardScroll_071.jpg、InGame_KeyboardNoFunds_071.jpg。

## 钓获边界

本轮普通竹竿在港口实际投向开放水面；桌面截图中识别到原生黄色咬钩符号。持续截图观察后尝试C/X提竿，尚未进入BobberBar或取得鱼获。只读记录确有nibble=True→False，没有hit/reeling/caught=True，因此不把咬钩算钓获。InGame_HookAttempt_071.jpg仅是失败尝试截图。QA新增只读菜单/竿状态/背包账目记录，无自动提竿、自动钓鱼、强制成功或鱼获注入。

预览时钟固定正午；QA启动时原有配方API审计会临时购买后恢复，日志18秒阶段不是本轮桌面配方证据。本轮实际购买在11:20—11:21，前后只读账目证明购买前没有配方、购买后准确登记。所有本轮交易未保存，原春QA仍春6/1618；尚不能宣称正常新角色多日通关、已验证交易重载、烹饪或吃饭。鼠标实际出售仍待独立验证。

实现依据使用本机公开游戏菜单接口与[SMAPI官方输入接口](https://github.com/Pathoschild/SMAPI/blob/develop/src/SMAPI/IInputHelper.cs)；只抑制已处理的柜台按键。地图、人物、音乐与完整任务书未因本功能而判定完成。

## 最终0.7.1回归

NativeCounter_071_final.txt确认加载实际0.7.1运行模块；再次实际出售风干北极鳕1618→1737，InventoryChanged移除1份，F5账目第7格为空、另一份风干大西洋鳕仍在。最终帮助行移到柜台上方安全区域，实拍InGame_KeyboardCounter_final_071.jpg。

从收购柜台沿下方通道绕过中央工作台，实走到订单柜台15,7，W/X打开，Tab/Enter尝试无原鱼的普通订单：金币1737不变、无收据，原生材料限制生效。见InGame_KeyboardOrder_guard_071.jpg。这只证明缺料拒付，不代表订单成功交付的实际桌面闭环已完成。订单提示已改用“交货/提交所需渔获”，不称购买。

最后从菜单正常退出，未保存。磁盘原QA仍春6/1618，见CounterSaveBaseline_071.txt；正常入口包含同一生产模块，QA只负责定位和观察。
