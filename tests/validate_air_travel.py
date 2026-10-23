"""Airline content contracts and a regression for walkable airport edge leaks.
Static proof only; flight/skip/return/save must still be played in the native game.
"""
from pathlib import Path
import json
import xml.etree.ElementTree as E
R=Path(__file__).resolve().parents[1];P=R/'ContentPack'
changes=json.loads((P/'content.json').read_text())['Changes']
def entries(target):
 out={}
 for c in changes:
  if c['Target']==target:out.update(c.get('Entries',{}))
 return out
triggers=entries('Data/TriggerActions');mail=entries('Data/mail')
assert 'ArcticPassage_Invitation' not in triggers
assert triggers['ArcticPassage_AirlineInvitation']['Actions']==['AddMail Current ArcticPassage_AirlineInvitation now']
assert '!PLAYER_HAS_MAIL Current ArcticPassage_AirlineInvitation' in triggers['ArcticPassage_AirlineInvitation']['Condition']
assert mail['ArcticPassage_AirlineInvitation']=='{{i18n:mail.invitation}}'
for lang in ['default','zh']:
 t=json.loads((P/f'i18n/{lang}.json').read_text())
 assert t['mail.invitation'].count('%item object ArcticPassage_FlightTicket 1 %%')==1
 assert '%item' not in t['mail.invitation.legacy']
assert not any(c['Target']=='Maps/Beach' and c.get('AddWarps') for c in changes)
ticket=entries('Data/Objects')['ArcticPassage_FlightTicket']
assert ticket['Price']==0 and not ticket['CanBeGivenAsGift'] and not ticket['CanBeTrashed']
print('PASS one airline invitation/one native ticket attachment; old invitation ID retained without duplicate ticket; old beach teleport removed')
for season in ['spring','summer','fall','winter']:
 root=E.parse(P/f'assets/maps/Airstrip_{season}.tmx').getroot();w,h=int(root.get('width')),int(root.get('height'))
 properties={p.get('name'):p.get('value') for p in root.findall('./properties/property')};raw=properties['Warp'].split()
 warps={(int(raw[i]),int(raw[i+1])) for i in range(0,len(raw),5)}
 grid=[int(x) for x in root.find("layer[@name='Buildings']/data").text.split(',')]
 edge={(x,y) for y in range(h) for x in range(w) if (x in [0,w-1] or y in [0,h-1]) and grid[y*w+x]==0}
 assert edge==warps, (season,edge,warps)
 assert all(raw[i+2:i+5]==['ArcticPassage_Town','27','2'] for i in range(0,len(raw),5))
print('PASS all four seasons: every walkable map-edge cell has a native town exit, including both outer lanes')
print('Static contracts only; native flight/skip/return/save evidence is recorded separately in docs/AirTravel077.md')
