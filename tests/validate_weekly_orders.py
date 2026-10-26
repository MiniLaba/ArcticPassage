"""Static contract boundaries, not proof of native catch/reward completion."""
from pathlib import Path
import json
R=Path(__file__).resolve().parents[1];P=R/'ContentPack';c=json.loads((P/'content.json').read_text())['Changes']
def entries(t):
 out={}
 for p in c:
  if p['Target']==t:out.update(p.get('Entries',{}))
 return out
orders=entries('Data/SpecialOrders');assert set(orders)=={'ArcticPassage_CoastalLog','ArcticPassage_FreshCrates','ArcticPassage_StormSupplies','ArcticPassage_StormFish','ArcticPassage_ExportBoxes'}
for key in ('ArcticPassage_CoastalLog','ArcticPassage_FreshCrates'):
 order=orders[key]
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
supplies=orders['ArcticPassage_StormSupplies']
assert supplies['OrderType']=='ArcticPassage_Story' and supplies['Repeatable']
assert supplies['Condition']=='PLAYER_HAS_MAIL Current ArcticPassage_StormSuppliesUnlocked, !PLAYER_HAS_MAIL Current ArcticPassage_StormSuppliesComplete'
assert supplies['Objectives'][0]['Type']=='Donate' and supplies['Objectives'][0]['RequiredCount']=='20'
assert supplies['Objectives'][0]['Data']['AcceptedContextTags']=='id_o_771'
assert supplies['Objectives'][0]['Data']['DropBox']=='ArcticPassage_StormSupplies'
fish=orders['ArcticPassage_StormFish']
assert fish['Condition']=='PLAYER_HAS_MAIL Current ArcticPassage_StormFishUnlocked, !PLAYER_HAS_MAIL Current ArcticPassage_StormFishComplete'
assert fish['Objectives'][0]['Type']=='Fish' and fish['Objectives'][0]['RequiredCount']=='1'
assert fish['Objectives'][0]['Data']['AcceptedContextTags']=='arcticpassage_rod_fish'
objects=entries('Data/Objects');tagged={k for k,v in objects.items() if 'arcticpassage_rod_fish' in v.get('ContextTags',[])}
assert len(tagged)==7 and not any('Receipt' in k or k.endswith(('Shrimp','SnowCrab')) for k in tagged)
assert any(p['Target']=='Maps/ArcticPassage_CommunityHouse' and any(t.get('SetProperties',{}).get('Action')=='ArcticPassageWeekly' for t in p.get('MapTiles',[])) for p in c)
assert any(p['Target']=='Maps/ArcticPassage_CommunityHouse' and any(t.get('SetProperties',{}).get('Action')=='ArcticPassageFishCrate' for t in p.get('MapTiles',[])) for p in c)
a=json.loads((P/'i18n/default.json').read_text());b=json.loads((P/'i18n/zh.json').read_text());assert set(a)==set(b)
print('PASS two repeating native weekly contracts plus two chapter-gated community orders; the supply order consumes 20 fiber and the emergency fish order counts one real rod catch; 7 rod species remain tagged.')
print('Static only: board acceptance, donation, fresh-catch progress, expiration, reward and save/reload require separate evidence.')
