export type Place = {id:string; name:string; en:string; group:string; point:[number,number,number,number]; intro:string; route:string};
export const places:Place[] = [
 {id:'market',name:'灯市与港街',en:'Lamp Market',group:'镇区',point:[848,1323,10,148],intro:'鱼摊和商店夹着一小段港街。彩屋架在桩上，檐下留出积雪的空间；天黑时，主街的灯罩把光收在行人脚边。',route:'从码头沿港街向西北步行。'},
 {id:'port',name:'工作渔港',en:'Working Harbour',group:'镇区',point:[975,1230,3,185],intro:'木栈桥伸向防波堤内侧，小船在这里卸鱼、收网。沿岸依次是船具所、索具仓和加工棚。',route:'从灯市下坡，沿港街抵达码头。'},
 {id:'church',name:'北坡教堂',en:'Hillside Church',group:'镇区',point:[669,1364,26,115],intro:'红木礼拜堂以朗伊尔城的斯瓦尔巴教堂为原型。低矮的会客厅、脊塔与相邻牧师楼，在山坡上形成错落的轮廓。',route:'从西街转入礼拜堂支路。'},
 {id:'craft',name:'工艺院',en:'Craft Court',group:'镇区',point:[818,1415,25,130],intro:'版画室、织造坊和小院展售廊围出一处避风的作业空间。沿小街走，能从工坊后门回到灯市。',route:'从灯市后巷转入工艺院小街。'},
 {id:'air',name:'镇西机场',en:'Western Airfield',group:'郊外',point:[-662,1481,14,1170],intro:'机场沿西侧天然海岸台地展开。约八百米的跑道呈西北偏西至东南偏东走向，机坪和航站设施集中在陆侧。深褐环形航站楼两侧设双道门的拱形防风通廊。',route:'经航站北门，沿镇西联络路进镇。'},
 {id:'camp',name:'季节冰屋营地',en:'Winter Camp',group:'郊外',point:[12,1660,18,123],intro:'冬季，驿路北侧的缓平台上搭起四座雪屋，旁边留出雪块教学和犬队停靠的空地。最近的冰屋距北界冰缘约 1.16 公里。',route:'由镇西驿路向北分岔，经科考站抵达。'},
 {id:'station',name:'西台地科考站',en:'Field Station',group:'郊外',point:[30,1606,17,90],intro:'研究站与物资帐分立在营地南面。这里既是整理样品和补给的地方，也是步行进入季节营地的前站。',route:'从镇西联络路转入台地小径。'},
 {id:'vault',name:'岩肩种子库',en:'Seed Vault',group:'郊外',point:[565,1622,48,102],intro:'参考斯瓦尔巴全球种子库，带有冰裂纹饰的门廊嵌入岩肩。入口之后，通道向山体内部的冷藏室延伸。',route:'在西侧登顶道的鞍部转上种子库支径。'},
 {id:'lookout',name:'山脊望冰台',en:'Ridge Lookout',group:'自然地标',point:[858,1616,112,110],intro:'木平台贴着最高点附近的山脊。向南看小镇和港湾，向东北看冰舌末端，视线跨过整条山谷。',route:'从北坡登顶道上山，在山脊转入短径。'},
 {id:'ice',name:'北界冰川',en:'Northern Glacier',group:'自然地标',point:[1300,1920,35,695],intro:'常年冰舌自北向南伸入谷地，在终碛内侧变薄。融水从舌端流向湾口，冰前砾地与河道留给地貌自然变化。',route:'在山脊望冰台隔谷观察。'},
 {id:'light',name:'北极灯塔',en:'Cape Light',group:'自然地标',point:[1176,974,18,137],intro:'红带灯塔立在海岬，灯室高过守灯屋。从湾外回望，塔身与岬角一起标出港口的方向。',route:'由渔港向东，沿岬角灯塔道前往。'},
 {id:'sea',name:'外海漂冰与岛屿',en:'Outer Fjord',group:'自然地标',point:[740,670,2,890],intro:'外海漂着宽大的桌状冰山和露出裂脊的倾覆冰块，较小的冰块散在外湾。航线在内湾与外岛之间转折，登陆点接上礁岸和背风滩的步道。',route:'沿码头出海航线查看岛屿与登陆点。'}
];
