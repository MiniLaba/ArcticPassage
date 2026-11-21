"""Read-only ordinary-role R01 checkpoint; never grants, warps or writes saves."""
from pathlib import Path
import json
import xml.etree.ElementTree as E
R = Path(__file__).resolve().parents[1]
S = Path.home()/'.config/StardewValley/Saves'
name = 'FrostTest_452177277'
r = E.parse(S/name/name).getroot(); p = r.find('player')
fish = {i.findtext('key/string'): [int(x.text) for x in i.findall('value/ArrayOfInt/int')] for i in p.findall('fishCaught/item')}
items = [(i.findtext('itemId'),int(i.findtext('stack','0'))) for i in p.findall('items/Item') if i.findtext('itemId')]
quests = {q.findtext('id'): {'completed':q.findtext('completed'),'reward':q.findtext('moneyReward')} for q in p.findall('questLog/Quest')}
assert (r.findtext('currentSeason'),r.findtext('dayOfMonth'),p.findtext('money')) == ('spring','6','1060')
assert fish['(O)ArcticPassage_Capelin'][0] == 3
assert fish['(O)ArcticPassage_PolarCod'][0] == 1
assert not any(i=='ArcticPassage_Capelin' for i,n in items)
assert quests.get('ArcticPassage_FirstCatch_spring',{'completed':'true','reward':'0'}) == {'completed':'true','reward':'0'}
assert quests['ArcticPassage_Shed'] == {'completed':'false','reward':'250'}
assert '9' in quests and '13' in quests
assert sum(n for i,n in items if i=='ArcticPassage_FlightTicket') == 1
assert p.findtext('lastSleepLocation') == 'ArcticPassage_Guesthouse'
report = {'save':name,'season':'spring','day':6,'gold':1060,'nativeFishCaught':fish,'items':items,'quests':quests,
          'evidence':'Ordinary five-mod session; native casting/BobberBar/three fish, Ada dialogue, native journal +400 and native bed save; raw log and screenshots separate.',
          'limits':'Only first shipment completed. Shed, boat, processing and four consecutive quests/three full days not yet passed.'}
(R/'docs/FirstShipmentSaveState_R01.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print('PASS ordinary save spring6/1060g; native capelin3 and polar cod1; three capelin absent; first shipment reward cleared; shed active; original quests and unique ticket preserved.')
