# 最新：飞越四季 · 航空广播版

`renders/Frosthavn-飞越四季-航空广播版.mp4`，199.7秒，1920×1080，30fps。

开头改成英文女声航空欢迎词和相应中文字幕；下降阶段加入另一位英文男声的机长客舱广播，语速约158词/分，带麦克风接通／断开、底噪与静电质感。广播10.8–24.407秒，无字幕，在接地前约3.3秒结束。机窗“下一站”改为“飞往”，机翼修正和实机标识保留。

单独试听：`voice/flight-v9/Captain-PA-preview.mp3`。新话音是本地合成预设，非真实机长录音；审阅记录见`evidence/DirectorV9Review_20261029.md`。

复现（沿用已保留的V8/V7/V6素材）：

```sh
voice/.venv/bin/python tools/make_flight_voice_v9.py
voice/.venv/bin/python tools/make_captain_pa_v9.py
../FrosthavnPromo/.venv/bin/python tools/prepare_captions_v9.py
voice/.venv/bin/python tools/mix_director_v9.py
node tools/render_mg.mjs --v9 --shot=window
python3 tools/assemble_director_v9.py
voice/.venv/bin/python tools/review_director_v9.py
```

---

# 上一版：飞越四季 · 机翼修正版

`renders/Frosthavn-飞越四季-机翼修正版.mp4`，199.7秒，1920×1080，30fps。

修正右侧机窗的反侧机翼：翼根在左、翼尖向右后掠，与实际航向及景物流动一致。V7实机标识、商店字幕与雪橇剪辑修整全部保留。审核记录为`evidence/DirectorV8Review_20261029.md`。

复现（沿用下文V7/V6已制作素材）：

```sh
node tools/render_mg.mjs --v8 --shot=window
python3 tools/assemble_director_v8.py
python3 tools/review_director_v8.py
```

---

# 上一版：飞越四季 · 实机标识精修版

`renders/Frosthavn-飞越四季-实机标识精修版.mp4`，199.7秒，1920×1080，30fps，H264/AAC。

全部游戏实录增加原创灯塔“实机画面 / NATIVE GAMEPLAY”标识，按世界、商店、手记／教学画面避让界面。修顺雪橇接营地的连续压暗，商店字幕移到留白处。118秒实录总量不变，英语旁白和配乐沿用V6，音频包直接复制。

复现：

```sh
../FrosthavnPromo/.venv/bin/python tools/make_gameplay_badge_v7.py
python3 tools/assemble_director_v7.py
python3 tools/review_director_v7.py
```

沿用已保留的V6规范化CG片段与原生素材；初次需先完成下文V6流程。实际剪辑、字幕与标识区间分别为`voice/script/story-v7.json`、`voice/script/captions-v7.json`、`evidence/gameplay-badge-v7.json`。审阅记录见`evidence/DirectorV7Review_20261029.md`。旧版MP4保留。

---

# 上一版：飞越四季 · 航拍与实录完整版

`renders/Frosthavn-飞越四季-航拍与实录完整版.mp4`，199.7秒，1920×1080，30fps，H264/AAC。当前依据 `voice/script/story-v6.json` 剪辑。

28秒机窗进场展示小镇俯瞰、三边／四边／五边、接地与持续滑跑；机场独立在西侧半岛。30秒全年景观连续融雪、长日、秋色、极夜，摄影机缓慢航拍。鱼市、研究站、雪屋营地、雪橇、夏季皮划艇与冰川栈道补入同一模型；港湾／营地／冰川各有远景推进接实录。全部118秒实录源段保留。

保留用户选定温暖日常配乐、24句合成英文解说和中文字幕，随新剪辑重新排时；字幕可编辑：`voice/Frosthavn-v6.zh-CN.srt`、`voice/Frosthavn-v6.en.srt`。CG是概念模型，不冒充游戏引擎画面。

复现（沿用本地缓存语音、原生录屏及已制作的 `full-edition-parts`、V5短线透明视频）：

```sh
node tools/render_mg.mjs --v6
voice/.venv/bin/python tools/retime_voice_v6.py
../FrosthavnPromo/.venv/bin/python tools/build_voice_captions_v6.py
python3 tools/make_director_sound_v6.py
voice/.venv/bin/python tools/mix_director_v6.py
python3 tools/assemble_director_v6.py
python3 tools/review_director_v6.py
```

审阅记录：`evidence/DirectorV6Review_20261029.md`。所有旧版保留。本轮是宣传片修改，未改动游戏和官网。

---

# 上一版：一条线，带你回家 · 导演精修版

`renders/Frosthavn-一条线带你回家-导演精修版.mp4`，168.5秒，1920×1080，30fps，H264/AAC。当前以 `voice/script/story-v5.json` 为剪辑依据。

本次重做三维票纸开场，实际齿孔、厚度、折弯和沿航线推进；在开冰→抛竿、冬季全景→内陆章节之间加入两段短线动效。结尾从旅舍窗帘、台灯、书、薄霜与雪台细节连续拉回港湾，品牌留在左侧，航线落到同一扇暖窗的实际投影上。积雪屋沿、木框和稀疏窗前落雪进入概念模型。

英文合成解说、24组中文字幕和选定的Life in Silico配乐延用上一版；原生实录源段118秒、所有游戏镜头取段与正常速度保持。并未新增游戏功能或把CG当成游戏引擎画面；概念全景不是地图的逐格拼接。

复现新增画面（先保有上一版已制作的音轨、字幕与full-edition-parts）：

```sh
node tools/render_mg.mjs --v5
../FrosthavnPromo/.venv/bin/python tools/make_line_transitions.py
voice/.venv/bin/python tools/mix_director_v5.py
python3 tools/assemble_director_v5.py
python3 tools/review_director_v5.py
```

最终复核记录见 `evidence/DirectorV5Review_20261029.md`；本轮目视检查与编码音频自动测量分开记录，未作主观试听认证。旧版MP4均保留。

---

# 上一版：从一张机票，到一段生活

`renders/Frosthavn-从一张机票到一段生活-英文解说中字版.mp4`：166.5秒，1920×1080，30fps，H264/AAC。新的叙事顺序把人物放回活动中，实录源段仍为118秒。新增合成英文女声、24组中文字幕、音乐自动让位；原创MG增加岩脊、裸岩及季节岸冰，并简化说明文字。

- 导演方案：`voice/script/DirectorTreatment.md`。
- 完整英中脚本：`voice/script/BilingualVoiceover.md`。
- 可编辑字幕：`voice/Frosthavn.zh-CN.srt`、`voice/Frosthavn.en.srt`。
- 实际语音时长：`voice/script/voice-timing.json`。
- 最终审阅：`evidence/DirectorEditionReview_20261029.md`。

复现（依赖已安装于本地独立voice/.venv；模型来源及许可见CREDITS）：

```sh
node tools/render_mg.mjs --v4
voice/.venv/bin/python tools/make_english_voice.py
../FrosthavnPromo/.venv/bin/python tools/build_voice_captions.py
python3 tools/make_director_sound.py
voice/.venv/bin/python tools/mix_director_voice.py
voice/.venv/bin/python tools/assemble_director_film.py
python3 tools/review_director_film.py
```

此前素材、60秒首剪、78秒版和原166.5秒版均保留。更高阶MG美术建议详见导演方案；未将当前结果评为世界级或已完成全部建议。

---

# 霜灯港 B+C 宣传片工程

历史完整四季版：`renders/Frosthavn-四季与港湾生活-完整宣传片.mp4`，166.5秒（约2分47秒），1920×1080，30fps，H.264/AAC。旧60秒首剪和78秒MG版均保留。

本轮按照用户反馈重做机窗路线、补齐完整春夏秋冬，增加实际内容。实录源片段合计118秒，约为上一版的3.3倍；包括六位居民对话、抛竿/咬钩/原生小游戏、实际出售、开洞、犬橇、雪屋三层搭接、冰川、研究手记与社区屋。对话是正常连续录像中的阅读停留，没有截图替代实录。

音乐沿用 Life in Silico — Scott Buckley（CC BY4.0），纸声0.9、音乐0.75后统一响度，片尾和MP4含署名。

## 重现最新版本

```sh
node tools/render_mg.mjs --v3
python3 tools/make_full_sound.py
python3 tools/assemble_full_film.py
python3 tools/update_full_docs.py
python3 tools/review_full_film.py
```

依赖：Node、FFmpeg、系统Python；渲染复用相邻FrosthavnPromo/node_modules的Three.js与Playwright和已安装的Chromium。字体PingFang SC / Avenir Next。原折纸镜头复用本工程已有Blender输出。`cut-v3.json`为最终剪辑依据；`public/mg-v3-timing.json`为MG源场景时长依据。`--resume`只在中间段、来源和剪辑计划未改变时使用。

## 素材与复核

- `evidence/full-edition-edit.json`：精确来源、剪辑范围、输出与音轨哈希。
- `evidence/full-native-sources.json`：全部入片原生录像来源与哈希。
- `evidence/full-edition-probe.json`：最终MP4媒体参数、响度及黑段检查。
- `evidence/full-review-*.jpg`和`full-transition-*.jpg`：最终编码视频的2fps全片联系表、10fps关键转场抽帧。尾部空格为排版补位。
- `evidence/FullEditionReview_20261029.md`：实际目视范围及未验证项。
- 原始QA源存档哈希未变：`evidence/original-save-integrity-full-20261029.json`。

新录像仍采用原生screencapture及用户授权的原生游戏输入；FilmDirector只用于独立FilmHarbor副本的机位、日期、解锁/道具布置，不进入发布模组，不自动保存。未成功的交互不作功能展示；冰川、社区屋等探索镜头已重新录制，避免未收物品提示遮挡。实际主线/全年游玩与Windows验证不属于这轮拍摄。

CG全年全景是原创主题几何演绎，不是游戏地图逐格拼接或引擎画面。钓鱼小游戏没有钓获成功主张；出售的鳕鱼为单独预置。音乐听感不以自动参数代替验收。
