"""Read-only checkpoint after the normal role's first catch/sale/overnight.

Run at the 0.7.8 checkpoint; later normal play may legitimately change it.
Never creates, edits, or loads a save into the game.
"""
from pathlib import Path
import json
import xml.etree.ElementTree as E

ROOT = Path(__file__).resolve().parents[1]
SAVES = Path.home()/'.config/StardewValley/Saves'
name = 'FrostTest_452177277'
root = E.parse(SAVES/name/name).getroot()
player = root.find('player')
items = [(i.findtext('itemId'), int(i.findtext('stack', '0')))
         for i in player.findall('items/Item') if i.findtext('itemId')]
quests = {q.findtext('id'): {'completed': q.findtext('completed'),
                           'reward': q.findtext('moneyReward')}
          for q in player.findall('questLog/Quest')}
fish = {i.findtext('key/string'): [int(x.text) for x in i.findall('value/ArrayOfInt/int')]
        for i in player.findall('fishCaught/item')}
mail = [x.text for x in player.findall('mailReceived/string')]
assert (root.findtext('currentSeason'), root.findtext('dayOfMonth'), player.findtext('money')) == ('spring', '5', '660')
assert player.findtext('lastSleepLocation') == 'ArcticPassage_Guesthouse'
assert sum(n for item, n in items if item == 'TrainingRod') == 1
assert sum(n for item, n in items if item == 'ArcticPassage_FlightTicket') == 1
assert not any(item == 'ArcticPassage_PolarCod' for item, n in items)
assert fish['(O)ArcticPassage_PolarCod'][0] == 1
assert mail.count('ArcticPassage_AirlineInvitation') == 1
assert quests.get('ArcticPassage_Arrival', {'completed': 'true', 'reward': '0'}) == {'completed': 'true', 'reward': '0'}
assert quests['ArcticPassage_FirstCatch_spring'] == {'completed': 'false', 'reward': '400'}
assert '9' in quests and '13' in quests
baselines = {}
for old, expected in {
    'ArcticQA_451755789': ('spring', '6', '1618'),
    'ArcticWinterQA_451755789': ('winter', '7', '1618'),
    'ArcticFlowQA_451755789': ('spring', '10', '1683'),
    'ArcticShipmentQA_451755789': ('winter', '8', '1618'),
}.items():
    r = E.parse(SAVES/old/old).getroot()
    actual = (r.findtext('currentSeason'), r.findtext('dayOfMonth'), r.findtext('player/money'))
    assert actual == expected, (old, actual)
    baselines[old] = actual
report = {
    'save': name, 'season': 'spring', 'day': 5, 'money': 660,
    'walletSequenceFromNativeLog': [450, 600, 575, 660],
    'lastSleepLocation': player.findtext('lastSleepLocation'),
    'items': items, 'fishCaught': fish, 'quests': quests,
    'fishingExperience': [int(i.text) for i in player.findall('experiencePoints/int')],
    'airlineMailCount': mail.count('ArcticPassage_AirlineInvitation'),
    'baselineDatesAndMoney': baselines,
    'evidence': 'Saved XML read-only; native catch, purchase, sale, sleep and cold reload require the separate logs and screenshots.',
    'limits': 'One polar cod caught and sold; three-capelin delivery, four consecutive quests and three complete game days remain unverified.'
}
(ROOT/'docs/StarterSaveState_078.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
print('PASS saved spring 5 / guesthouse / 660g / one purchased rod and ticket / polar cod native catch record / sold fish absent / arrival reward cleared / first shipment active / four old QA dates and balances retained.')
