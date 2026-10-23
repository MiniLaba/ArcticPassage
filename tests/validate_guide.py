"""New guide invariants: each observation is reachable in every shipped season."""
from pathlib import Path
from collections import deque
import json
import xml.etree.ElementTree as ET
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
PACK=ROOT/'ContentPack'
RUNTIME=ROOT/'Code/ArcticPassage/Runtime'
sites={'Town':(25,24),'Harbor':(32,11),'Icefjord':(35,31),'Tundra':(25,4),'WinterCamp':(19,37)}
index=json.loads((ROOT/'docs/build-index.json').read_text())['maps']
checked=0
for region,site in sites.items():
 for season in ['spring','summer','fall','winter']:
  root=ET.parse(PACK/f'assets/maps/{region}_{season}.tmx').getroot()
  w,h=int(root.get('width')),int(root.get('height'))
  props={}
  for ts in root.findall('tileset'):
   first=int(ts.get('firstgid'))
   for tile in ts.findall('tile'):
    props[first+int(tile.get('id'))]={p.get('name'):p.get('value') for p in tile.findall('./properties/property')}
  layers={l.get('name'):[int(n) for n in l.find('data').text.strip().split(',')] for l in root.findall('layer')}
  def walk(p):
   x,y=p
   return 0<=x<w and 0<=y<h and layers['Back'][y*w+x]>0 and not layers['Buildings'][y*w+x] and 'Water' not in props.get(layers['Back'][y*w+x],{})
  start=tuple(index[region]['points']['spawn']);seen={start};queue=deque([start])
  while queue:
   x,y=queue.popleft()
   for p in [(x-1,y),(x+1,y),(x,y-1),(x,y+1)]:
    if p not in seen and walk(p):seen.add(p);queue.append(p)
  assert site in seen,(region,season,'observation unreachable',site)
  thumb=RUNTIME/f'assets/guide/{region}_{season}.png'
  with Image.open(thumb) as im:assert im.size==(256,192)
  checked+=1
en=json.loads((RUNTIME/'i18n/default.json').read_text());zh=json.loads((RUNTIME/'i18n/zh.json').read_text())
assert en.keys()==zh.keys()
for site in ['rock','harbor','ice','tundra','camp']:
 for field in ['name','where','body']:
  assert en[f'guide.site.{site}.{field}'] and zh[f'guide.site.{site}.{field}']
localized=json.loads((PACK/'i18n/zh.json').read_text())
assert all('栖光湾' not in value for value in localized.values())
for region in ['Town','Harbor','Guesthouse']:
 assert '霜灯港' in localized['location.'+region]
for key in ['location.Town','location.Harbor','location.Guesthouse']:
 assert 'Frosthavn' in json.loads((PACK/'i18n/default.json').read_text())[key]
data=json.loads((PACK/'content.json').read_text())
assert any(p['Action']=='Load' and p['Target']=='Maps/ArcticPassage_Town' for p in data['Changes'])
assert any(p['Target']=='Data/AudioChanges' and 'ArcticPassage_LumenhavenTheme' in p.get('Entries',{}) for p in data['Changes'])
print(f'PASS {checked} seasonal observation anchors reachable; matching scene plates present.')
print(f'PASS {len(en)} runtime bilingual keys; complete landmark entries; Frosthavn display names and stable internal IDs.')
