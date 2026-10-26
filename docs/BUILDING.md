# 源码构建

玩家请使用发布页install.zip和[安装指南](../INSTALL.zh-CN.md)。本页面向开发者。

## 构建运行模块

需要.NET SDK、自己安装的Stardew Valley1.6.15及SMAPI4.5.2。项目目标net6.0，使用C#12；SDK8可编译。`GamePath`指向同时包含`Stardew Valley.dll`、`StardewValley.GameData.dll`和`StardewModdingAPI.dll`的游戏目录。

```sh
dotnet build Code/ArcticPassage/ArcticPassage.Runtime.csproj -c Release -p:GamePath="/your/game/directory"
python3 tools/package_release.py
```

输出位于dist。运行模块只引用游戏/前置程序集；打包器仅允许项目自有DLL进入玩家包。

## 内容和素材

ContentPack是可编辑内容。Code/ArcticPassage/Runtime包含运行清单、文本和运行资源。art/source保留原始素材，art/prompts记录相关历史来源，art/music包含乐谱。个人登机牌、测试存档、机器日志和本机游戏不在发布范围。

重建内容需Python3、Pillow、NumPy：

```sh
python3 tools/build_content.py
python3 tests/validate_content.py
```

重建会覆盖生成内容，应在副本中进行。配乐重建另外需要FluidSynth、ffmpeg及GeneralUser GS，许可见licenses/GeneralUser-GS.txt。现成音轨已经在内容包中，玩家不用安装这些工具。

部分tools脚本服务原开发机的独立测试游戏、SDK和本机入口，需自行配置对应路径；它们不是跨平台安装器。tests/RuntimeFixture是隔离原生API验证工具，必须自己准备专用测试存档，不能分发给玩家或放入正常Mods。

## 发布核对

运行tests/validate_content.py、tests/validate_air_travel.py、tests/validate_frontier.py、tests/validate_weekly_orders.py及tests/validate_guide.py。NativeValidation可使用本机实际游戏数据类型与TMX解析器检查；为其构建时同样提供GamePath。

打包器使用文件白名单，排除本机日志、存档检查点、个人票券与游戏程序集。源码压缩包和GitHub仓库由同一白名单产生；不要从整个工作区递归上传。

主线提示／缺失后继恢复规则可单独运行`dotnet run --project tests/HarborProgressRegression -- .`。已构建运行模块后，`dotnet run --project tests/NativeValidation -- . --runtime-hooks`只检查真实节日身份与钓鱼接口，不载入玩家存档；完整地图解析仍使用不带该选项的命令。上述检查不等于普通游玩或Windows游戏实测。
