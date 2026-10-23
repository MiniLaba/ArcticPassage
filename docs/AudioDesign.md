# 极地声景与原版鸟鸣修复（0.4）

用户实听指出原版鸟叫让白湾像普通雪村。检查本机1.6.15实际代码发现：未指定LocationContext的自定义室外地点回退Default，GameLocation.checkForMusic会选spring_day_ambient，随机鸟鸣/虫鸣另由PlayRandomAmbientSounds控制。

现在24张地图明确指定白湾海岸或苔原Context，两者PlayRandomAmbientSounds=false，Music列表为空；Data/Locations为每个地点配置自有MusicDefault且不随春夏秋冬/雨天忽略。DayAmbience与NightAmbience同样引用自有声景，阻断原版季节环境回退。只增加本模组Context/音频ID，不覆盖原版山谷全局音轨。

| 场所 | 声景 | 用途 |
|---|---|---|
| 小镇、港口、峡湾 | ArcticPassage_CoastalWind | 低风与分层潮汐冲刷声 |
| 苔原 | ArcticPassage_TundraWind | 更干燥的开阔风声，无海潮层 |
| 旅舍、收购站 | ArcticPassage_IndoorWind | 低音量、隔墙滤过的风声 |

三段均为本项目tools/build_audio.py用NumPy谱噪声与周期包络原创合成，36秒、22050Hz、16位立体声WAV，原生Data/AudioChanges载入并循环，Category=Ambient。不是实地录音，不使用未经授权的采样，不含鸟鸣/虫鸣或旋律。此轮先修正环境声，完整原创旋律配乐仍待作曲。

FilePaths采用Content Patcher官方AbsoluteFilePath令牌，随Mods文件夹移动解析，不硬编码本机路径。波形电平与循环周期检查通过；试听音色的主观质量仍需迭代，不能把“无代码报错”当作听感获奖结论。

本机原生日志已逐个确认六地点：全部randomAmbience=False，Town/Harbor/Icefjord为CoastalWind，Tundra为TundraWind，Guesthouse/Fishery为IndoorWind。记录见SMAPILoad_040.txt和NativeSession_040.txt。未录制设备实际输出，主观听感不能由日志证明。

## 0.6环境一致性

地图现在使用CoastClimate/TundraClimate两个新标识，保留原三段声音。新标识避免继续读入0.4/0.5Context已经排定的山谷天气。晴/雨/雪概率独立，苔原跟随白湾海岸；不产生原生Wind（花瓣/落叶）或GreenRain。不以原生Wind作为北极风雪特效。完整动态风雪及三主题旋律仍待制作。

本机1.6.15的playTerrainSound分支表明，Grass类型在winter会选择snowyStep；没有Snow类型。0.6仅对室外冬季雪路采用该原生判定，木栈道保留Wood，室内不变。此为音效选择验证，尚未录制设备输出，不声称完成主观试听。
