"""Differentiate the existing daily trades; retain all dated receipt/save IDs."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / 'ContentPack'
TAG = 'R01 daily: '


def main():
    path = PACK / 'content.json'
    content = json.loads(path.read_text())
    content['Changes'] = [p for p in content['Changes'] if not p.get('LogName', '').startswith(TAG)]
    locales = {locale: json.loads((PACK / f'i18n/{locale}.json').read_text())
               for locale in ('default', 'zh')}
    prices = {}
    payments = {}
    for patch in content['Changes']:
        if patch.get('Target') == 'Data/Objects':
            prices.update({key: value['Price'] for key, value in patch.get('Entries', {}).items()
                           if 'Price' in value})
    for patch in content['Changes']:
        if patch.get('Target') != 'Data/Shops':
            continue
        shop = patch.get('Entries', {}).get('ArcticPassage_Orders')
        if shop is None:
            continue
        for item in shop['Items']:
            if item['ItemId'] == '(O)ArcticPassage_RestaurantReceipt':
                # Daily fixed price with a premium over iridium base value.
                pay = round(prices[item['TradeItemId'].removeprefix('(O)')] * 2 * 2.2)
                item['ActionsOnPurchase'] = [f'AddMoney {pay}' if a.startswith('AddMoney ') else a
                                             for a in item['ActionsOnPurchase']]
            payments[item['Id']] = next(int(a.split()[1]) for a in item['ActionsOnPurchase'] if a.startswith('AddMoney '))
    texts = {
        'order.Restaurant.name': ('Restaurant order · silver+', '餐馆订单 · 银星起'),
        'order.Restaurant.desc': (
            'Deliver 2 seasonal fish of silver quality or better. Silver fish are used first. Premium payment is immediate; Mira gains 25 friendship. Once per day.',
            '提交2条银星或更高品质的当季鱼，优先使用较低星级。货款立即入账，米拉友谊增加25点；每天限交一次。'),
        'order.Research.desc': (
            'Deliver 1 seasonal fish of any quality. Payment is immediate and the first delivered sample of this species is recorded. Once per day.',
            '提交1条任意品质的当季鱼，货款立即入账，并保存该鱼种首次交样日期；每天限交一次。'),
        'shop.orders': (
            'Daily deliveries: regular orders accept 3 seasonal fish of any quality; the guesthouse needs 2 silver-or-better fish and thanks you with Mira friendship; research records 1 sample. Each type can be delivered once per day.',
            '每日交货：普通订单收3条任意品质当季鱼；旅舍餐馆收2条银星以上当季鱼，另增加米拉友谊；研究订单收1条并登记样本。每类每天限交一次。')
    }
    for key, (en, zh) in texts.items():
        locales['default'][key] = en
        locales['zh'][key] = zh
    # Display the actual fixed reward before a player hands over fish. Keep
    # the same receipt object IDs; only its description follows the season.
    for season in ('spring', 'summer', 'fall', 'winter'):
        fields = {}
        for kind in ('Regular', 'Restaurant', 'Research'):
            pay = payments[season + '_' + kind]
            key = f'order.{kind}.{season}.desc'
            if kind == 'Restaurant':
                en = f'Deliver 2 silver-or-better seasonal fish: {pay}g and +25 Mira friendship. Lower eligible quality is used first. Once per day.'
                zh = f'交2条银星或更高品质的当季鱼：{pay}金，米拉友谊+25。优先收较低星级的合格鱼；每天限一次。'
            elif kind == 'Research':
                en = f'Deliver 1 seasonal fish of any quality: {pay}g. The first delivered sample of this species is recorded. Once per day.'
                zh = f'交1条任意品质当季鱼：{pay}金，并保存该鱼种首次交样日期；每天限一次。'
            else:
                en = f'Deliver 3 seasonal fish of any quality: {pay}g. Payment is immediate; once per day.'
                zh = f'交3条任意品质当季鱼：{pay}金。货款立即入账，每天限一次。'
            locales['default'][key] = en
            locales['zh'][key] = zh
            fields['ArcticPassage_' + kind + 'Receipt'] = {'Description': '{{i18n:' + key + '}}'}
        content['Changes'].append({'Action': 'EditData', 'Target': 'Data/Objects',
                                   'LogName': TAG + season, 'Fields': fields, 'When': {'Season': season}})
    path.write_text(json.dumps(content, ensure_ascii=False, indent=2) + '\n')
    for locale, data in locales.items():
        (PACK / f'i18n/{locale}.json').write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
    print('Updated existing daily orders: quality restaurant deliveries and recorded research samples; old receipt IDs retained.')


if __name__ == '__main__':
    main()
