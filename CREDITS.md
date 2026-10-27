# 素材、依赖与资料

- 原创：`ContentPack/assets` 所有 PNG、TMX、WAV、三名虚构人物和对白、鱼图标、内容包数据以及生成/验证程序，由本项目制作，MIT。
- 游戏：Stardew Valley / ConcernedApe。读取本机合法安装的数据定义与资源；没有将游戏贴图、音乐或程序集打进发布包。
- SMAPI 4.5.2：Pathoschild 与贡献者，官方 GitHub 发布包，仅在本地开发环境安装。
- Content Patcher 2.9.1：Pathoschild 与贡献者，MIT，使用官方 stable 源码进行本地测试编译。为适配已下载的 C#12 编译器，仅将 C#14 `field` 属性和泛型 nameof 改为等价旧语法；不作为官方发布版分发。
- .NET SDK 6.0.428 / 8.0.408：Microsoft 官方下载，在工作区独立安装。
- 0.2—0.6 新增内置 imagegen 生成的原创场景位图，原图保留在 `art/source`，完整提示词在 `art/prompts`。旧的基础像素资源由绘图程序生成。生成场景通过图块导出程序接入游戏，没有直接拼贴实景摄影。0.4增加三段NumPy谱噪声/周期包络原创合成风潮WAV，不是实地录音，不使用外部采样。0.4室内、居民肖像/行走源图与近景冰山同样使用内置imagegen制作并保留原图/完整提示词。
- 实景资料：NSIDC / Twila Moon 的伊卢利萨特夏季港口、NSIDC / Mads Pihl / Visit Greenland 的格陵兰冬季彩屋，以及 Visit Greenland 城镇、冰峡湾与步道资料；仅供研究，不分发原摄影。具体链接及采用范围见 `docs/RealWorldReferences.md`。

技术核对：

- [Content Patcher 官方作者指南](https://github.com/Pathoschild/StardewMods/blob/stable/ContentPatcher/docs/author-guide.md)
- [地图](https://wiki.stardewvalley.net/Modding:Maps)、[地点](https://wiki.stardewvalley.net/Modding:Location_data)、[鱼类](https://wiki.stardewvalley.net/Modding:Fish_data)、[NPC](https://wiki.stardewvalley.net/Modding:NPC_data)、[任务](https://wiki.stardewvalley.net/Modding:Quest_data)、[触发动作](https://wiki.stardewvalley.net/Modding:Trigger_actions)
- 本机 `StardewValley.GameData.xml` 与实际1.6.15类型定义，用于验证具体字段。不存在的任务完成查询没有继续使用，改为交货对话的原生邮件标记。

自然资料参考沿用任务书来源；本版不声称完成对全部现实资料与文化细节的专项审阅。物种学名、淡水/海洋和深水区分为设计依据，具体季节与出现概率为游戏化简化。

0.5晾鱼架/风干产品、0.6全四季17张重绘资源均使用内置imagegen模式；提示词art/prompts/arctic-review-060，主源图art/source，旧图archive/before-060。0.6新增挪威极地研究所植物形态资料，只作研究参考，不分发照片。

- 0.6.2三首配乐的旋律、和声、MIDI编排由本项目制作，MIT；声音使用FluidSynth 2.6.1与[GeneralUser GS 2.0.3](https://github.com/mrbumpy409/GeneralUser-GS)渲染，不属于无外部采样的合成风潮。GeneralUser GS由S. Christian Collins及贡献者提供，完整许可见docs/licenses/GeneralUser-GS.txt；仅分发渲染音轨，不分发音色库。

- 0.6.3九海产与四料理位图使用内置imagegen，原图art/source/*063*，完整提示词art/prompts/seafood-063；程序只做技术排版。物种形态与捕捞方式资料见docs/SeafoodDesign063.md。

- 0.7项目自有SMAPI运行模块采用MIT。使用SMAPI随附的Harmony，仅引用本机0Harmony.dll，不将其或游戏程序集放入安装包。


2026-10-27：诺拉、莱文、阿玛的新肖像为项目原创 SVG 代码绘图，源文件与六表情原图位于 art/source/code-portraits；生成程序为 tools/draw_resident_portraits.py 与 render_resident_portraits.mjs。官网和游戏使用同一套造型，不依赖新增生图。
