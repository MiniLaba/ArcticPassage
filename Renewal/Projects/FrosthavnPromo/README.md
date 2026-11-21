# 霜灯港 · 再往北，一点

60秒 / 1920×1080 / 30fps / 中文与英文标题 / H.264 + AAC。

影片介绍现有PC单人模组，使用既有游戏实拍、游戏地图与六位居民肖像；航空开场使用官网原组件，飞机接地镜头以原生C#绘制公式和纹理制作展示适配。它是代码编排的宣传片，不是一段连续游玩录像。既有实拍保留原有UI，不伪造新的游戏状态。未作Windows游戏内兼容、多人、全主线通关或完整年度节日验收承诺。

影片：`renders/Frosthavn-再往北一点-1080p.mp4`
分镜：`DIRECTION.md`；规格和动作声音：`plan.json`；来源和检查：`evidence/`。

## 重现最终导出

需要Node.js >=22、FFmpeg及Playwright对应的无头浏览器。已提供全部视觉资源和混音成品，不需要原版游戏、官网工程、外部服务或生图工具即可重新导出。

```sh
npm ci
npx playwright install chromium --only-shell
npm run build
node render.mjs --audio assets/master.wav --output renders/Frosthavn-再往北一点-1080p.mp4
```

本项目保留原产品组件的逐字节快照，原始路径和SHA256记录在`evidence/product-snapshots.json`。该快照仅为独立渲染；没有修改官网和游戏源码。

要改声音：`tools/mix_audio.py plan.json`（Python标准库 + FFmpeg），再导出。混音记录会核对plan、音乐、音效和master哈希。要重新编曲（原生合成引擎音源已随工程保留），可建立Python虚拟环境并安装`requirements.txt`，使用`tools/compose_score.py --soundfont <GeneralUser-GS.sf2>`；音色库不随工程分发，渲染许可见`assets/GeneralUser-GS-license.txt`。

```sh
python3 tools/mix_audio.py plan.json
node stills.mjs evidence/stills 0 9.5 15 24.7 34.2 49.8 58
python3 tools/check_delivery.py plan.json --video renders/Frosthavn-再往北一点-1080p.mp4 --mix-report evidence/audio-mix.json
```

普通预览：`npm run preview`。预览网页的`seek(seconds)` / `playFilm()`驱动画面；音频以最终MP4为准，预览工具默认不混放声音。只更新必要镜头，修改时间线或声音后重新混音。

## 审阅边界

关键帧、完整影片抽帧、全部转场条带和音频测量会保存到evidence。没有主观试听时明确记录，不能以LUFS或轨道存在冒充听感验收。用户尚未要求上传或公开发布本影片；本次交付为本地文件。
