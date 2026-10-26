# 白湾美术实景依据

2026-10-16：用户指出地图缺少真实北极感后，重新研究格陵兰西岸聚落。白湾为虚构地点，不把不同北极地区拼接成地理复刻。

## 一手资料

- NSIDC《Arctic Weather and Climate》：https://nsidc.org/learn/parts-cryosphere/arctic-weather-and-climate 。包含 Twila Moon 拍摄的伊卢利萨特夏季港口、Mads Pihl / Visit Greenland 的 Kangaamiut 冬季彩屋照片。前者展示密集船只、低矮圆缓裸岩、坡地彩屋与夏季植被；后者帮助判断雪地中的屋色和建筑尺度。照片仅供研究，不随模组分发。
- Visit Greenland《The 13 Best Viewpoints in Ilulissat》：https://visitgreenland.com/articles/the-13-best-viewpoints-in-ilulissat/ 。研究城镇、港湾和冰峡湾的空间关系。
- Visit Greenland 伊卢利萨特目的地介绍：https://visitgreenland.com/destinations/ilulissat/ 。研究渔业城镇与迪斯科湾冰山的关系。
- Visit Greenland 冰峡湾：https://visitgreenland.com/activities/ilulissat-icefjord/ 。采用岸上栈道、开阔海面与漂浮崩解冰山的空间关系；没有把生成的海蚀拱洞当作该地特定冰山的精确复刻。
- 伊卢利萨特冰峡湾中心步道：https://www.isfjordscentret.gl/en/experiences/hiking/ 。与 Visit Greenland 步道介绍交叉参考，形成可步行观景路径的关卡语言。
- Realdania 伊卢利萨特冰峡湾中心项目资料：https://cdn.realdania.dk/media/tebl5qvn/ilulissat_isfjordscenter_en.pdf 。搜索可见建筑与地形资料，全文过大未在网页阅读器加载，暂不作为精确细节的唯一依据。

## 转化为关卡的设计决定

1. 低圆缓花岗岩作为地形骨架，房屋与步道落在岩丘间隙；移除规则石柱围边和孤立石块摆件。
2. 彩色木屋采用相近尺度、不同屋身与门廊细节，基础抬高，屋前留生活空间。
3. 小镇是可居住的作业聚落：港口开放水面、系缆桩、网具、燃料桶、柴堆与晒鱼架有明确用途。
4. 冰山在港外，采用低阔不规则形体。删去同一巨型冰墙的机械重复与三角冰山图标。
5. 春季斑雪、夏季苔原、秋季赭红矮植被、冬季蓝紫雪影。北极感依靠地貌和材料，不仅依赖白色。
6. 主步道、门前台阶、码头必须与碰撞和交互坐标一致，漂亮的背景不能代替关卡可玩性。

## 素材制作

新场景采用内置 imagegen 生成原创像素场景；实景照片不直接拼贴。完整生成提示词保存在 art/prompts。原图保存在 art/source，游戏图片为网格导出。现阶段需要逐季核对布局、遮挡和通路，目标美术品质尚不等于已经获奖或完成全部验收。

## 02:00 续作

新增 Icefjord / Tundra 四季原图。冰峡湾采用不重复的大块浮冰、低裸岩头地和观测栈道；苔原采用蜿蜒溪流、单一木桥、低矮矮灌丛与小水塘。夏秋陆地去雪，冬季保留开放主河槽以维持既有玩法；这项水文安排是游戏化简化。原图尺寸及构图保持季节对齐，碰撞按实际输出的地标重新标定。

## 2026-10-26野生动物与目击范围

- [格陵兰自然资源研究所：陆生哺乳动物](https://natur.gl/leksikon/land-animals/?lang=en)：核对白狐、北极兔、驯鹿和麝牛等真实陆生动物。游戏本轮采用任务书已有的北极狐、格陵兰驯鹿与偏远北极熊，不将偏北／偏东地区的物种随意安排到港口近旁。
- [格陵兰自然资源研究所：鸟类与哺乳动物研究部门](https://natur.gl/about-us/dpt-mammals-and-birds/?lang=en)：核对研究部门监测的海象、鲸、海鸟、驯鹿和麝牛类别；作为观察题材的交叉参考。
- [格陵兰自然资源研究所：格陵兰鲨](https://natur.gl/arter/groenlandshaj/)及[格陵兰海域调查资料](https://www.nafo.int/Portals/0/PDFs/sc/2018/scr18-037.pdf)：用于将鲨鱼表现限定为外海深水中的罕见科研目击，不作普通鱼获、售卖或战利品。
- [Visit Greenland：格陵兰鲸类](https://visitgreenland.com/articles/whales/)：说明多种鲸类在夏季无冰水域出现，座头鲸可在峡湾和近岸水域见到。因此游戏将夏季鲸影放在峡湾外海，且不变成可钓物。

物种动画、出现日期与观察半径均为游戏机制，不是种群数量或某一真实城镇的出现概率。地图只安排远望或安全岸上观察；不添加喂熊、驯养、狩猎、熊袭击或取得海洋哺乳动物材料。风雪封航和晴夜极光日历也属于玩法调度，不作为气候统计。

## 2026-10-17整体复核

本轮重新查看伊卢利萨特目的地、城镇观景点和NSIDC照片资料，新增挪威极地研究所关于低伏植物/风暴露/雪床的资料：https://npolar.no/en/themes/vegetation-svalbard/ 。其用途仅是植物形态参考，不把斯瓦尔巴种群移植成迪斯科湾名录。Visit Greenland的Sermermiut栈道实景见 https://traveltrade.visitgreenland.com/latest-news/wellness-tourism/ 。完整逐项整改与设计判断见ArcticReview060.md；照片仅参考，不分发。全部17张新资源由内置imagegen原创编辑并保留提示词。
