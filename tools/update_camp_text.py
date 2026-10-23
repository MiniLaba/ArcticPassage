"""One-time structured update of bilingual hand-authored runtime metadata."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
R=ROOT/'Code/ArcticPassage/Runtime'
text={
 'default':{
  'guide.region.WinterCamp':'Tundra field camp',
  'guide.directions':'Walk north from town to the tundra. Cross its eastern wooden bridge to the field camp; the red research hut has a bed. East from town leads to the harbor.',
  'guide.site.camp.name':'Shelters for a season',
  'guide.site.camp.where':'Field camp: follow the western shelter path south to the notice beside the first dome or tent.',
  'guide.site.camp.body':'The camp changes with the season: snow-block domes in winter, canvas tents in the other seasons. These are demonstration shelters, not a description of every Arctic home. The red research hut offers an actual bed; the marked trail returns west to the tundra bridge.'},
 'zh':{
  'guide.region.WinterCamp':'苔原营地',
  'guide.directions':'镇区向北去苔原，跨过东侧木桥后继续向东进入营地。红色研究站里可过夜；镇区向东通渔港。',
  'guide.site.camp.name':'随季节更换的庇护所',
  'guide.site.camp.where':'营地：沿西侧庇护所小路向南，走到第一座雪屋或帐篷旁的告示附近。',
  'guide.site.camp.body':'营地随季节更换庇护所：冬季展示雪块搭建的圆顶雪屋，其余季节改用帆布帐篷。它们不是所有北极居民的日常住房。红色研究站内有实际可用的床，沿标记向西就能回到苔原木桥。'}
}
for locale,entries in text.items():
 p=R/f'i18n/{locale}.json';data=json.loads(p.read_text());data.update(entries)
 p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
p=R/'lighting.json';data=json.loads(p.read_text())
data['ArcticPassage_WinterCamp']=[{'X':428,'Y':352,'Radius':1.6},{'X':588,'Y':352,'Radius':1.6},{'X':214,'Y':320,'Radius':1.3}]
p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
