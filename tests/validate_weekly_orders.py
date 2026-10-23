"""Static contract boundaries, not proof of native catch/reward completion."""
from pathlib import Path
import json
R=Path(__file__).resolve().parents[1];P=R/'ContentPack';c=json.loads((P/'content.json').read_text())['Changes']
def entries(t):
 out={}
 for p in c:
  if p['Target']==t:out.update(p.get('Entries',{}))
 return out
orders=entries('Data/SpecialOrders');assert set(orders)=={'ArcticPassage_CoastalLog','ArcticPassage_FreshCrates'}
for order in orders.values():
 assert order['OrderType']=='ArcticPassage_Weekly' and order['Duration']=='Week' and order['Repeatable']
 assert order['Condition']=='PLAYER_HAS_MAIL Host ArcticPassage_Shed'
 assert order['Objectives'][0]['RequiredCount']=='6'
 assert order['Objectives'][0]['Data']['AcceptedContextTags']=='arcticpassage_rod_fish'
 assert 0<int(order['Rewards'][0]['Data']['Amount'])<=650
assert orders['ArcticPassage_CoastalLog']['Objectives'][0]['Type']=='Fish'
donation=orders['ArcticPassage_FreshCrates']['Objectives'][0]
assert donation['Type']=='Donate'
assert donation['Data']['DropBox']=='ArcticPassage_FishCrate'
assert donation['Data']['DropBoxGameLocation']=='ArcticPassage_CommunityHouse'
assert donation['Data']['DropBoxIndicatorLocation']=='3 5'
objects=entries('Data/Objects');tagged={k for k,v in objects.items() if 'arcticpassage_rod_fish' in v.get('ContextTags',[])}
assert len(tagged)==7 and not any('Receipt' in k or k.endswith(('Shrimp','SnowCrab')) for k in tagged)
assert any(p['Target']=='Maps/ArcticPassage_CommunityHouse' and any(t.get('SetProperties',{}).get('Action')=='ArcticPassageWeekly' for t in p.get('MapTiles',[])) for p in c)
assert any(p['Target']=='Maps/ArcticPassage_CommunityHouse' and any(t.get('SetProperties',{}).get('Action')=='ArcticPassageFishCrate' for t in p.get('MapTiles',[])) for p in c)
a=json.loads((P/'i18n/default.json').read_text());b=json.loads((P/'i18n/zh.json').read_text());assert set(a)==set(b)
print('PASS two native weekly contracts; isolated type; Sunday deadline; repeatable; 7 rod species across seasons; no gifts/trap/processed substitutions; bounded rewards; real community board action.')
print('Static only: native acceptance, objective progress, expiration, reward and save/reload require separate evidence.')
