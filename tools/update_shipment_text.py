"""Structured metadata update for the optional native first-order rebooking."""
from pathlib import Path
import json
R=Path(__file__).resolve().parents[1]
entries={
 'default':{
  'guide.changeHelp':'The requested fish is out of season. Keep this order if you have stored fish, or change it to three seasonal fish. Reward and next step stay the same. New fish:',
  'guide.changeButton':'U  Change to this season',
  'guide.changed':'Order changed. Give Ada three of the new fish in one stack. No items or money were exchanged.',
  'guide.changeUnavailable':'No eligible out-of-season first order. Completed orders and pending rewards stay unchanged.',
  'guide.changeFailed':'The order data could not be verified. Your existing order was kept.'},
 'zh':{
  'guide.changeHelp':'本单鱼种已不在当前鱼季。有存鱼可继续交原单，也可改订当季三条鱼，奖励和后续不变。新鱼种：',
  'guide.changeButton':'U　改订当季鱼',
  'guide.changed':'已改订。手持同一堆叠的三条新鱼交给艾达。本次未交换物品或金币。',
  'guide.changeUnavailable':'目前没有可改订的跨季首单。已完成任务和未领奖励保持不变。',
  'guide.changeFailed':'订单数据暂时无法核实，原订单已保留。'}
}
for locale,values in entries.items():
 p=R/f'Code/ArcticPassage/Runtime/i18n/{locale}.json';data=json.loads(p.read_text());data.update(values)
 p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
for p in [R/'Code/ArcticPassage/Runtime/manifest.json']:
 data=json.loads(p.read_text());data['Version']='0.7.6'
 p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
p=R/'Code/ArcticPassage/ArcticPassage.Runtime.csproj';p.write_text(p.read_text().replace('<Version>0.7.5</Version>','<Version>0.7.6</Version>'))
p=R/'tools/build_content.py';p.write_text(p.read_text().replace("'Version':'0.7.5'","'Version':'0.7.6'").replace("'MinimumVersion':'0.7.5'","'MinimumVersion':'0.7.6'"))
