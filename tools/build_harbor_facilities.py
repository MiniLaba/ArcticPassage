"""R01: code-drawn construction states and native local repair supplies/mail.

Idempotent extension, also called by build_content. No saves or game binaries.
"""
from pathlib import Path
import json
import xml.etree.ElementTree as E
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / 'ContentPack'
SEASONS = ('spring', 'summer', 'fall', 'winter')
TAG = 'R01 facilities: '


def dump(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')


def scaffold(image):
    d = ImageDraw.Draw(image)
    # Closed seasonal work area, entirely outside the already-walkable quay.
    for x in (111, 174, 246, 301):
        d.rectangle((x, 417, x+3, 548), fill='#3d4241')
        d.line((x+1, 418, x+1, 542), fill='#b49a75')
        d.rectangle((x-4, 543, x+8, 547), fill='#777c73')
    for y in (445, 484, 521):
        d.rectangle((108, y, 307, y+3), fill='#7b6550')
        d.line((110, y, 305, y), fill='#baa17b')
    for x in (112, 176, 248):
        d.line((x, 519, x+51, 447), fill='#716252', width=2)
        d.line((x+1, 519, x+52, 447), fill='#ac9472')
    # Braced, closed doorway and a small, legible warning chevron.
    d.rectangle((173, 494, 198, 537), fill='#39434b', outline='#a18b6a')
    d.line((174, 496, 197, 536), fill='#b49b73', width=3)
    d.line((197, 496, 174, 536), fill='#b49b73', width=3)
    d.rectangle((278, 524, 298, 536), fill='#d8b46c', outline='#4b4d4b')
    for x in range(281, 297, 5):
        d.line((x, 526, x-4, 533), fill='#554e45', width=2)


def working_details(image):
    d = ImageDraw.Draw(image)
    # Season-neutral work fittings, not another building/interior.
    # Preserve the existing carefully shaded door and masonry proportions.
    d.rectangle((213, 511, 222, 518), fill='#d4c29a', outline='#62564a')
    d.line((215, 513, 220, 513), fill='#596862')
    d.line((215, 516, 218, 516), fill='#596862')
    for x in (240, 285):
        d.rectangle((x, 523, x+2, 553), fill='#695645')
        d.line((x, 522, x+2, 522), fill='#c3a479')
    d.line((239, 528, 287, 528), fill='#c4ad80', width=2)
    for x in range(248, 283, 7):
        d.line((x, 528, x, 533), fill='#74604c')
        d.polygon([(x, 533), (x+2, 536), (x+1, 545), (x-2, 547), (x-2, 536)], fill='#c4b99b', outline='#746f61')
        d.point((x, 536), fill='#e3d4af')
    # Stacked clean crates on the working apron.
    for x, y in ((314, 527), (325, 533)):
        d.rectangle((x, y, x+13, y+12), fill='#567c80', outline='#364d56')
        d.line((x+2, y+3, x+11, y+3), fill='#a4babc')
        d.line((x+2, y+8, x+11, y+8), fill='#304c58')


def main():
    content = json.loads((PACK/'content.json').read_text())
    content['Changes'] = [p for p in content['Changes'] if not p.get('LogName', '').startswith(TAG)]
    # CP Load is exclusive: the base and completed sources must never both
    # match. Otherwise CP rejects both instead of choosing the last patch.
    for p in content['Changes']:
        if p.get('Action') == 'Load' and p.get('Target') == 'Maps/ArcticPassage_Harbor':
            p['When'] = {**p.get('When',{}), 'HasFlag |contains=ArcticPassage_Shed': False}
    def patch(action, target, **kwargs):
        content['Changes'].append(dict(Action=action, Target=target, LogName=TAG+target, **kwargs))
    locales = {l: json.loads((PACK/f'i18n/{l}.json').read_text()) for l in ('default','zh')}
    def tr(key, en, zh):
        locales['default'][key] = en; locales['zh'][key] = zh
        return '{{i18n:'+key+'}}'
    # Load different real TMX sources. Every collision, Warp and instance action
    # is retained; only the scene sheet changes after the existing saved flag.
    for s in SEASONS:
        original = Image.open(ROOT/f'art/source/harbor-{s}-master.png').convert('RGBA').resize((1024,768),Image.Resampling.NEAREST)
        closed = original.copy(); scaffold(closed)
        closed.save(PACK/f'assets/maps/Harbor_{s}_scene.png')
        ready = original.copy(); working_details(ready)
        ready.save(PACK/f'assets/maps/HarborReady_{s}_scene.png')
        tree = E.parse(PACK/f'assets/maps/Harbor_{s}.tmx')
        for im in tree.findall('./tileset/image'):
            if im.get('source') == f'Harbor_{s}_scene.png':
                im.set('source', f'HarborReady_{s}_scene.png')
        tree.write(PACK/f'assets/maps/HarborReady_{s}.tmx',encoding='utf-8',xml_declaration=True)
        # Honest side-by-side code-art inspection, not an in-game screenshot.
        preview = Image.new('RGBA',(1024,256))
        preview.paste(closed.crop((64,368,576,624)),(0,0))
        preview.paste(ready.crop((64,368,576,624)),(512,0))
        preview.save(ROOT/f'previews/HarborConstruction_{s}.png')
    patch('Load','Maps/ArcticPassage_Harbor',FromFile='assets/maps/HarborReady_{{MapSeason}}.tmx',When={'HasFlag |contains=ArcticPassage_Shed':True})
    # The guesthouse's writing desk doubles as a native forwarding mailbox.
    # Native mailbox() owns read flags, attachments and overflow UI.
    patch('EditMap','Maps/ArcticPassage_Guesthouse',MapTiles=[{'Position':{'X':17,'Y':7},'Layer':'Buildings','SetProperties':{'Action':'Mailbox'}}])
    for s in SEASONS:
        path = PACK/f'assets/maps/Guesthouse_{s}_scene.png'
        im = Image.open(ROOT/'art/source/guesthouse-interior-master.png').convert('RGBA').resize((384,288),Image.Resampling.NEAREST); d = ImageDraw.Draw(im)
        d.rectangle((279,82,287,88),fill='#e6d9bb',outline='#67594d')
        d.line((280,83,283,85,286,83),fill='#a39373')
        im.save(path)
    # Imported supplies cost at least their Valley inputs. They are an optional
    # source for visitors who prefer fishing to returning to mine/chop at home.
    # Existing unlimited farm resources remain the cheaper route.
    for p in content['Changes']:
        if p.get('Target') != 'Data/Shops': continue
        market = p.get('Entries',{}).get('ArcticPassage_Market')
        if market is not None and 'id_o_smokedfish' not in market['SalableItemTags']:
            # SmokedFish is an artisan product, not category_fish. Accept its
            # native qualified-ID tag so the workshop's output can be sold.
            market['SalableItemTags'].append('id_o_smokedfish')
        shop = p.get('Entries',{}).get('ArcticPassage_Supplies')
        if shop is None: continue
        items = shop['Items']
        ids = {'RepairWood','RepairStone','RepairIron','CrabPot','BaitMaker'}
        items[:] = [i for i in items if i.get('Id') not in ids and not i.get('Id','').startswith('LocalRepairIron_')]
        items.extend([
            {'Id':'RepairWood','ItemId':'(O)388','Price':15,'AvailableStock':40},
            {'Id':'RepairStone','ItemId':'(O)390','Price':30,'AvailableStock':40},
            {'Id':'RepairIron','ItemId':'(O)335','Price':1000,'AvailableStock':2,'Condition':'PLAYER_HAS_MAIL Current ArcticPassage_Shed'},
            {'Id':'CrabPot','ItemId':'(O)710','Price':1500,'AvailableStock':2},
            {'Id':'BaitMaker','ItemId':'(BC)BaitMaker','Price':10000,'AvailableStock':1,'Condition':'PLAYER_FISHING_LEVEL Current 6'},
        ])
        # A finite local repair contribution keeps the fishing-led introduction
        # playable without requiring a return to the Valley mines. Two bars per
        # farmer for the entire save, not daily/seasonal restock or free grants.
        for season,fish in [('spring','Capelin'),('summer','Capelin'),('fall','AtlanticCod'),('winter','PolarCod')]:
            for number in (1,2):
                receipt=f'ArcticPassage_LocalRepairIron_{number}'
                items.append({'Id':f'LocalRepairIron_{season}_{number}','ItemId':'(O)335','Price':0,
                    'TradeItemId':'(O)ArcticPassage_'+fish,'TradeItemAmount':3,'AvailableStock':1,
                    'AvailableStockLimit':'Player',
                    'Condition':f'SEASON {season}, PLAYER_HAS_MAIL Current ArcticPassage_Shed, !PLAYER_HAS_MAIL Current ArcticPassage_IronDelivered, !PLAYER_HAS_MAIL Current ArcticPassage_Boat, !PLAYER_HAS_MAIL Current {receipt}',
                    'ActionsOnPurchase':[f'AddMail Current {receipt} received']})
    sign = tr('r01.workshop','Give Roan 40 wood; the shed opens the next morning. For the boat, the supplies counter offers two iron bars per visitor: each costs 3 seasonal fish (capelin in spring/summer, cod in fall, polar cod in winter). This local contribution never restocks. Imported bars still cost 1000g; home-mined materials also work. Mail is forwarded to the guesthouse desk.',
              '把40份木材交给罗安，隔夜开棚。修船可在材料柜台以当季鱼货换铁锭：每块3条，春夏毛鳞鱼、秋季鳕鱼、冬季北极鳕；每位旅客整个存档限换两块，不随日或季节刷新。外运铁锭仍售1000金，自采材料也可使用。旅舍写字台转寄信件。')
    patch('EditData','Strings/StringsFromMaps',Entries={'ArcticPassage_Workshop':sign})
    line1 = tr('r01.opening.1','Last nail, last check. These boards should stand up to salt and wind.','最后一颗钉子，再检查一遍。这些木板要经得起盐雾和风。')
    line2 = tr('r01.opening.2','A smoker for quick batches, a rack for slow drying. I sent the equipment and plans to your mail. The guesthouse desk will have them.','急着出货就熏制，不赶时间就风干。我把设备和图纸寄给你了，旅舍写字台可以收信。')
    line3 = tr('r01.opening.3','Keep the walkway clear. A working harbor needs room for everyone.','把通道留出来。忙起来的港口，得给每个人留条路。')
    # Native TryGetLocationEvents first calls DoesAssetExist. EditData alone
    # doesn't make a new event asset exist, so register its empty base first.
    dump(PACK/'assets/data/Harbor_events.json', {})
    patch('Load','Data/Events/ArcticPassage_Harbor',FromFile='assets/data/Harbor_events.json')
    patch('EditData','Data/Events/ArcticPassage_Harbor',Entries={
        'ArcticPassage_WorkshopOpening/LocalMail ArcticPassage_Shed/Time 600 2200':
        'continue/21 33/farmer 21 35 0 ArcticPassage_Roan 21 33 2/skippable/pause 500/playSound crafting/pause 500/speak ArcticPassage_Roan "'+line1+'"/pause 500/speak ArcticPassage_Roan "'+line2+'"/speak ArcticPassage_Roan "'+line3+'"/end'
    })
    dump(PACK/'content.json', content)
    index_path = ROOT/'docs/build-index.json'
    index = json.loads(index_path.read_text())
    index['maps']['HarborReady'] = index['maps']['Harbor']
    dump(index_path, index)
    for l, data in locales.items(): dump(PACK/f'i18n/{l}.json',data)
    print('Built R01 four-season construction states, native forwarding mailbox, imported repair supplies and opening scene.')


if __name__ == '__main__': main()
