"""Regressions for exclusive repair scenes and new native route connections.
Static checks only. Native walks/events/save are recorded independently.
"""
from pathlib import Path
import json
import xml.etree.ElementTree as E
from collections import deque
R=Path(__file__).resolve().parents[1];P=R/'ContentPack';patches=json.loads((P/'content.json').read_text())['Changes']
loads=[p for p in patches if p['Action']=='Load' and p['Target']=='Maps/ArcticPassage_Harbor']
assert len(loads)==2
flag='HasFlag |contains=ArcticPassage_Shed'
assert {p['When'][flag] for p in loads}=={True,False}
print('PASS repair scene loads are mutually exclusive, before/after the saved flag')
market=next(p['Entries']['ArcticPassage_Market'] for p in patches if 'ArcticPassage_Market' in p.get('Entries',{}))
assert 'id_o_smokedfish' in market['SalableItemTags']
assert any(p['Action']=='Load' and p['Target']=='Data/Events/ArcticPassage_Harbor' for p in patches)
print('PASS native smoked-fish ID accepted by local buyer; harbor event asset has a Load source before EditData')
def read(name,s):
 root=E.parse(P/f'assets/maps/{name}_{s}.tmx').getroot();w,h=int(root.get('width')),int(root.get('height'))
 ly={v.get('name'):[int(x) for x in v.find('data').text.split(',')] for v in root.findall('layer')}
 walk={(x,y) for y in range(h) for x in range(w) if not ly['Buildings'][y*w+x]}
 raw=next(p.get('value') for p in root.findall('./properties/property') if p.get('name')=='Warp').split()
 exits={(int(raw[i]),int(raw[i+1])):(raw[i+2],int(raw[i+3]),int(raw[i+4])) for i in range(0,len(raw),5)}
 return root,w,h,walk,exits,ly
for s in ('spring','summer','fall','winter'):
 for n in ('SledTrail','Glacier','CommunityHouse'):
  root,w,h,walk,exits,ly=read(n,s)
  edges={p for p in walk if p[0] in (0,w-1) or p[1] in (0,h-1)}
  assert edges==set(exits),(n,s,edges,set(exits))
  for p,(dest,x,y) in exits.items():assert (x,y) in read(dest.removeprefix('ArcticPassage_'),s)[3]
  if n=='Glacier':
   assert not any(p.get('name')=='Water' for p in root.findall('./tileset/tile/properties/property'))
   assert not any(y<25 for x,y in walk),'Ice face must stay inaccessible'
 root,w,h,walk,exits,ly=read('WinterCamp',s)
 assert (49,23) in walk
 ts=root.find("tileset[@name='z_FrontierCampLink']")
 assert ly['Buildings'][23*w+50]==int(ts.get('firstgid'))
 assert ts.find('./tile/properties/property').get('value')=='Warp 60 24 ArcticPassage_SledTrail'
print('PASS 12 seasonal maps: every walkable edge has an exit; arrivals walkable; glacier face/stream inaccessible; camp link is a real action tile')
assert any(p['Target']=='Maps/ArcticPassage_Tundra' and '26 3 ArcticPassage_SledTrail 12 42' in p.get('AddWarps',[]) for p in patches)
assert any(p['Target']=='Maps/ArcticPassage_Town' and any(t.get('SetProperties',{}).get('Action')=='Warp 12 14 ArcticPassage_CommunityHouse' for t in p.get('MapTiles',[])) for p in patches)
assert not any('ArcticPassageSled' in p.read_text() for p in (P/'assets/maps').glob('SledTrail_*.tmx'))
print('PASS town/community and tundra/trail connections; no unregistered sled action advertised as playable')
