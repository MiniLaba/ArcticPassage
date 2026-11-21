"""Read only the independent normal-play save and existing named QA baselines.

This checks persistence after native play; it neither creates nor edits saves.
"""
from pathlib import Path
import json
import xml.etree.ElementTree as E

ROOT = Path(__file__).resolve().parents[1]
SAVES = Path.home()/'.config/StardewValley/Saves'
name = 'FrostTest_452177277'
root = E.parse(SAVES/name/name).getroot()
player = root.find('player')
mail = [m.text for m in player.findall('mailReceived/string')]
data = {p.findtext('key/string'):p.findtext('value/string') for p in player.findall('modData/item')}
items = [(p.findtext('itemId'), int(p.findtext('stack', '0'))) for p in player.findall('items/Item') if p.findtext('itemId')]
quests = {q.findtext('id'): {'completed':q.findtext('completed'), 'reward':q.findtext('moneyReward')} for q in player.findall('questLog/Quest')}
assert (root.findtext('currentSeason'), root.findtext('dayOfMonth'), player.findtext('money')) == ('spring','4','450')
assert player.findtext('lastSleepLocation') == 'ArcticPassage_Guesthouse'
assert sum(count for item,count in items if item == 'ArcticPassage_FlightTicket') == 1
assert mail.count('ArcticPassage_AirlineInvitation') == 1
assert data['WhiteBay.ArcticPassage/AirArrival'] == '1'
assert quests['ArcticPassage_Arrival'] == {'completed':'true','reward':'150'}
assert quests['ArcticPassage_FirstCatch_spring'] == {'completed':'false','reward':'400'}
assert '9' in quests and '13' in quests
baselines = {}
for old, expected in {
    'ArcticQA_451755789': ('spring','6','1618'),
    'ArcticWinterQA_451755789': ('winter','7','1618'),
    'ArcticFlowQA_451755789': ('spring','10','1683'),
    'ArcticShipmentQA_451755789': ('winter','8','1618'),
}.items():
    r = E.parse(SAVES/old/old).getroot()
    actual = (r.findtext('currentSeason'),r.findtext('dayOfMonth'),r.findtext('player/money'))
    assert actual == expected, (old,actual)
    baselines[old] = actual
report = {'save':name,'season':'spring','day':4,'money':450,'lastSleepLocation':player.findtext('lastSleepLocation'),
          'items':items,'airlineMailCount':1,'arrivalSeen':data['WhiteBay.ArcticPassage/AirArrival'],
          'quests':quests,'baselineDatesAndMoney':baselines,
          'evidence':'Read-only saved XML; native play and cold-reload proof are separate logs/screenshots.'}
(ROOT/'docs/AirlineSaveState_077.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print('PASS native saved spring 4 / guesthouse / 450g / one ticket and invitation / arrival complete with pending 150g / first catch active; four old QA dates and balances retained.')
