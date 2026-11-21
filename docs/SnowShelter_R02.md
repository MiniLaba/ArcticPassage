# 营地雪块排列

2026-10-24；固定R02雪屋互动、供既定R07冬季章节接续。没有新增地图、奖励门类或第十一个交付包。

在营地西侧雪屋前已有告示(20,35)互动，冬季打开三层雪块模型；站位(20,36)面北。左右方向键或A/D调整半块，Enter/空格安放，Esc退出；也有鼠标按钮和手柄输入接口。必须逐层错开接缝；错放不扣物，提前离开不记完成。完成后个人modData保存首次日期，再开显示已记录并可重练，重玩不覆写日期、不发钱／物品。模型不改地图实体、不消耗背包材料、不自动过夜。玩家需照常睡眠保存记录。

非冬季仅保留帆布营地说明。换季、换日或离开营地的旧菜单关闭，不能补记完成。现有红色研究站床位与返回路径保留；雪屋尚无独立内部。R07实际向导剧情、家具图纸奖励、冰钓衔接仍待，不把这个小互动算完整第8章。

## 资料与表现边界

[Pitquhirnikkut Ilihautiniq / Kitikmeot Heritage Society](https://www.kitikmeotheritage.ca/inuinnaitstonehouse)的Inuinnait资料区分近期历史上的冬季雪屋、夏季皮帐篷以及更早的石屋；本项目其他季节的现代帆布帐篷只是虚构野外营地，不称历史复原。

[加拿大公共档案中的1972年器物手册，PDF第60页](https://publications.gc.ca/collections/collection_2018/aanc-inac/R5-647-1972-eng.pdf#page=60)记述合适的压实雪、雪块沿螺旋上升并内倾及封顶，也明确雪屋并非全北极通用。该历史手册部分用语已过时，游戏采用“因纽特”表述，不照搬其泛化叙述。另参照[加拿大国家电影局影片目录](https://collection.nfb.ca/film/how_to_build_an_igloo)关于雪块庇护所演示的介绍；本轮未完整逐帧观看影片，不称建筑专家认证。

三层错缝是游戏的平面排列规则，不是完整螺旋结构或真实承载模拟。场景仍为文化学习展示，不把雪屋改为全镇永久民居，不加入刻板神秘符号。画面完全由代码绘制，无新增生图或下载照片贴图；当前是功能首版，未宣称达到大奖美学。

## 验证与限制

- 运行模块构建0警告0错误；测试夹具0错误，RepairAudit已有可空警告1条保留。SDK环境提示亦保留在构建记录。
- SnowShelter_model_R02.txt：15项实际模型源码回归，覆盖错放、反复调整、逐层完成、完成后不变及取消后新会话。
- 原生冬档API定向检查：真实地图动作、完整玩家碰撞盒、非冬关闭、错放／中途取消、真实菜单三层完成、重玩首次日期及背包钱包不变、失效日期／季节拒绝补记。夹具临时准备位置／日期并冻结时钟，不请求保存；不能称普通冬季解锁、普通章节通关或保存冷载。
- 首次实拍发现缩窄层的渲染基点额外错移半块，已统一中心网格，保留InGame_R02_snow_model_before_alignment_fix.png及NativeSnowShelter_before_alignment_fix_R02.txt。随后A/D＋Enter实际完成三层，InGame_R02_snow_model_completed_AD.png与NativeSnowShelter_AD_R02.txt有证据。
- 为避免多个原生菜单输入通道重复切换，最终键盘／手柄由本菜单专属SMAPI输入路径处理，原生重复回调忽略。最终桌面实际D＋Enter完成三层，重新打开显示已记录，Esc退出通过；InGame_R02_snow_model_completed_final.png、InGame_R02_snow_model_reopen_recorded.png、InGame_R02_snow_model_exit.png为实拍。CUA发送Right和A时，追踪未看到游戏ButtonPressed事件，故不能认定原生导航是根因，也不能称方向键／A实机通过。夹具直接调用Control处理器不证明桌面传输。鼠标、手柄硬件、英文／小窗口、多人与普通过夜保存仍待。

最终暂存DLL及翻译逐字节匹配源构建，QA开关全部关闭；本机正常入口实见5模组无QA，未加载角色。七个存档SHA256与春15开始检查一致，所有隔离测试均未请求保存。核对见SnowShelter_validation_R02.json、NativeSnowShelter_final_R02.txt及NativeSnowShelter_normal_entry_R02.txt。
