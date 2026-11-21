export type Pair = readonly [string, string];
export const PREVIEW_SOURCE = 'https://github.com/MiniLaba/ArcticPassage/tree/codex/windows-compatibility';
export const lights = [
 {id:'dusk', title:['冬夜灯火','Winter lights'], time:'22:00', season:['冬季','WINTER'], line:['在最长的夜里，为你留一盏灯。','A light left on through the longest night.']},
 {id:'noon', title:['冬日正午','Polar noon'], time:'12:00', season:['冬季','WINTER'], line:['短暂的冬日里，海湾映着清冷的微光。','A brief winter day. Cold light finds the bay.']},
 {id:'summer', title:['夏日午夜','Midnight sun'], time:'00:00', season:['夏季','SUMMER'], line:['午夜已过，远方仍是金色。','Past midnight, the horizon is still gold.']},
 {id:'aurora', title:['晴夜极光','Aurora night'], time:'22:00', season:['冬季','WINTER'], line:['抬头的那一刻，夜空有了另一种颜色。','Look up. The night has another colour.']},
 {id:'storm', title:['风雪将至','A gathering gale'], time:'15:00', season:['冬季','WINTER'], line:['有时，最好的出发是再等一等。','Sometimes, the best journey waits until tomorrow.']},
] as const;
export type Light = typeof lights[number]['id'];
export const worldPositions = [[14.8,52],[39.5,56],[64.4,72],[25.8,40],[58,29],[79.7,34],[64,13],[92,15]];
export const people = [
 {id:'ada', name:['艾达','Ada'], role:['渔港管理员','HARBOUR KEEPER'], place:2, scene:['一座港口的日常','The life of a harbour'], quote:['港口很小，有船晚归，大家都会留意。','The harbour is small. When a boat is late, everyone notices.'], body:['第一箱鱼、一本账册，还有明天的航次。艾达会陪你从照看渔获开始，慢慢成为港口的一员。','A first crate, a well-kept ledger, a crossing tomorrow. With Ada, caring for a catch becomes a way of belonging.'], detail:['交货 · 渔业加工 · 港口订单','DELIVER · PROCESS · TRADE']},
 {id:'mira', name:['米拉','Mira'], role:['苔原向导','TUNDRA GUIDE'], place:4, scene:['总有一条归途','A way back home'], quote:['好向导知道什么时候该返程。','A good guide knows when to turn back.'], body:['路标、避风处和风的方向。沿着米拉熟悉的小路走，慢慢学会在辽阔之中照看自己与同行的人。','Markers, shelter and the direction of the wind. Walk with Mira and learn to look after yourself—and the people beside you.'], detail:['标记步道 · 安全路线 · 冬季协作','MARKED PATHS · SAFE RETURNS']},
 {id:'roan', name:['罗安','Roan'], role:['港口工匠','HARBOUR CRAFTSMAN'], place:2, scene:['旧木料的新航次','Another crossing'], quote:['我挺为这座小港口骄傲的。','I am proud of this little harbour.'], body:['在罗安的工作台上，旧木料有了第二次机会。修好加工棚和渔船，再过一夜，港口就会有一点新的变化。','Old timber gets another chance at Roan’s bench. Repair the shed and the boat. Sleep a night. See what changes.'], detail:['维修材料 · 加工棚 · 渔船','RESTORE · BUILD · SAIL']},
 {id:'nora', name:['诺拉','Nora'], role:['航空与气象','AIR & WEATHER'], place:0, scene:['为每一次抵达亮灯','A light for arrivals'], quote:['跑道边的风旗，有时比云更能说明情况。','The flag at the strip tells more than the clouds do.'], body:['雪跑道上的灯，天空中的天气，还有一次次等候与抵达。认识诺拉，从读懂北方的光与风开始。','Runway lights, changing skies, departures and arrivals. Get to know Nora through the light and weather of the north.'], detail:['机场 · 天气 · 灯火小聚','AIRSTRIP · WEATHER · LANTERNS']},
 {id:'levin', name:['莱文','Levin'], role:['野外研究员','FIELD RESEARCHER'], place:5, scene:['把观察留在纸上','Learning to notice'], quote:['野外记录要写清地点、时间和你真正看到的东西。','A field note needs a place, a time and what you really saw.'], body:['一处地貌、一条鲸影记录、一份认真整理的调查袋。莱文让每次驻足，都成为认识海岸的一部分。','A landform, a distant whale, a carefully compiled field packet. With Levin, every quiet pause adds to the story of the coast.'], detail:['动物观察 · 地貌记录 · 科研手记','WILDLIFE · LANDFORMS · FIELD NOTES']},
 {id:'amma', name:['阿玛','Amma'], role:['冬营与犬队照护','CAMP & DOG TEAM'], place:5, scene:['在风雪里照看生活','Care through the winter'], quote:['离开营地前，每一枚扣环都要检查。','We check every buckle before we leave the camp.'], body:['搭接雪块、准备营地、照料休息的犬队。阿玛知道，北方的日常是许多细小而认真的照料。','Fit the snow blocks. Prepare the camp. Let the dogs rest. Amma knows that northern life is made of small, careful acts.'], detail:['雪屋课程 · 冬季营地 · 犬队','SNOW SHELTER · CAMP · DOG TEAM']},
] as const;
export const sightings = [
 {id:'fox', name:['北极狐','Arctic fox'], latin:'VULPES LAGOPUS', where:['低伏苔原 · 四季','TUNDRA · ALL SEASONS'], note:['沿着低矮植物和碎石观察。脚步放轻，让它继续走自己的路。','Watch from the low plants and stones. Keep your distance, and let it go its own way.'], x:34,y:58},
 {id:'seal', name:['海豹','Seal'], latin:'A COASTAL OBSERVATION', where:['冰山峡湾 · 春／秋／冬','ICEFJORD · SPRING / AUTUMN / WINTER'], note:['从岸上安静观察浮冰边缘。靠近风景，不打扰它的休息。','Watch quietly from shore, beside the broken ice. A closer view need not disturb a resting animal.'], x:62,y:52},
 {id:'whale', name:['远海鲸影','A distant whale'], latin:'A MARINE FIELD NOTE', where:['冰山峡湾 · 夏季','ICEFJORD · SUMMER'], note:['夏季午后望向远处海面。先看见一圈波纹，然后是海面下缓缓经过的影子。','Look out across the fjord on a summer afternoon. A ripple first; then a shape moving quietly below.'], x:86,y:58},
] as const;
export const chapters = [
 ['一张机票','An invitation','收到月月鸟来信，向熟悉的山谷暂时道别。','A letter from Moonbird. A little farewell to the familiar fields.','dusk'],
 ['一间亮着灯的房','A room of your own','沿机场步道进镇，在旅舍安顿下来。','Follow the airstrip path and settle into the guesthouse.','dusk'],
 ['第一箱鱼','A first catch','从当季渔获开始，认识港口的日常。','Begin with a seasonal catch and the rhythm of the harbour.','noon'],
 ['修好旧船','Timber & tide','交付材料、修好设施，等待下一次出航。','Bring the materials, restore the facilities, wait for the next crossing.','noon'],
 ['冰山之间','Among the icebergs','乘固定航线到峡湾，探索更深的水域。','Take the fixed boat route to the fjord and its deeper waters.','summer'],
 ['北方自然笔记','Northern field notes','记录动物、地貌与鲸影，把调查袋交到研究站。','Record wildlife, landforms and a distant whale; bring your field packet to the station.','summer'],
 ['风雪之前','Before the gale','为社区准备补给、完成鲜鱼单，再确认返程路线。','Prepare supplies, complete a fresh-catch order and check the way home.','storm'],
 ['冬营的一课','A lesson in winter','搭接雪块，在标记的安全冰洞留下一次真实鱼获。','Fit the snow blocks and make a real catch at the surveyed ice opening.','noon'],
 ['更远的航次','A farther crossing','从两处水域收获鱼货，风干加工，完成首次出口。','Fish two different waters, air-dry a catch and make the first export.','dusk'],
 ['一盏为你留的灯','A light left on','和六位邻居相聚。明天，港口仍有日常。','Gather with six neighbours. Tomorrow, the harbour’s life continues.','aurora'],
] as const;
export const festivals = [
 {date:'09',season:['春季','SPRING'],name:['港口开航日','Harbour Opening Day'],body:['码头钓鱼挑战、猜鱼重，还有一碗热炖鱼。','A pier fishing challenge, a weight-guessing game and hot fish stew.'],mode:'noon'},
 {date:'18',season:['夏季','SUMMER'],name:['极昼海湾日','Midnight Sun Bay Day'],body:['从岸上观察海鸟，在长日光里留下自然笔记。','Watch seabirds from shore and leave a field note in the lingering light.'],mode:'summer'},
 {date:'21',season:['冬季','WINTER'],name:['极夜灯光节','Polar Night Lantern Walk'],body:['分享热汤，沿提灯夜行，晴夜里等一等极光。','Share a bowl of soup, walk by lantern light and wait for a clear-night aurora.'],mode:'aurora'},
] as const;
