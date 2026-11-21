"""Read only named QA saves; audit the optional order's real overnight state.

This is evidence for a prepared seasonal-order scenario, not normal new play.
"""
from pathlib import Path
import json
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SAVES = Path.home() / '.config/StardewValley/Saves'
PREFIX = 'ArcticPassage_'
names = ['ArcticQA_451755789', 'ArcticFlowQA_451755789',
         'ArcticWinterQA_451755789', 'ArcticShipmentQA_451755789']
report = {}
for name in names:
    root = ET.parse(SAVES / name / name).getroot()
    player = root.find('player')
    items = []
    for slot, item in enumerate(player.findall('./items/Item')):
        items.append({'slot': slot, 'id': item.findtext('itemId'),
                      'stack': item.findtext('stack'), 'quality': item.findtext('quality'),
                      'type': item.get('{http://www.w3.org/2001/XMLSchema-instance}type')})
    quests = []
    for quest in player.findall('./questLog/Quest'):
        quests.append({**{key: quest.findtext(key) for key in
                         ['id', 'completed', 'moneyReward', 'item', 'number', 'target']},
                       'nextQuests': [node.text for node in quest.findall('./nextQuests/int')],
                       'modData': {node.findtext('./key/string'): node.findtext('./value/string')
                                   for node in quest.findall('./modData/item')}})
    report[name] = {'day': root.findtext('dayOfMonth'), 'season': root.findtext('currentSeason'),
                    'money': player.findtext('money'), 'lastSleepLocation': player.findtext('lastSleepLocation'),
                    'items': items, 'quests': quests}

original, flow, winter, shipment = (report[name] for name in names)
for save, expected in [(original, ('6', 'spring', '1618')),
                       (flow, ('10', 'spring', '1683')),
                       (winter, ('7', 'winter', '1618')),
                       (shipment, ('8', 'winter', '1618'))]:
    assert (save['day'], save['season'], save['money']) == expected
assert shipment['items'] == winter['items'], 'Rebooking or overnight changed inventory'
assert shipment['lastSleepLocation'] == PREFIX + 'Guesthouse'
orders = [q for q in shipment['quests'] if (q['id'] or '').startswith(PREFIX)]
assert len(orders) == 1, orders
order = orders[0]
assert (order['id'], order['completed'], order['moneyReward'], order['item'], order['number'], order['target']) == (
    PREFIX + 'FirstCatch_winter', 'false', '400', '(O)' + PREFIX + 'PolarCod', '3', PREFIX + 'Ada')
assert order['nextQuests'] == [PREFIX + 'Shed']
assert order['modData']['WhiteBay.ArcticPassage/RebookedFrom'] == PREFIX + 'FirstCatch_summer'
assert any(q['id'] == '9' for q in shipment['quests']), 'Unrelated native quest missing'
(ROOT / 'docs/ShipmentSaveState_076.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
print('PASS: isolated winter 8 native save retains one uncompleted PolarCod order, 400 pending contract, original inventory and 1618 gold; spring/flow/winter source dates and balances unchanged.')
