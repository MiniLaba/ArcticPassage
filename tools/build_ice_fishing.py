"""R03 fixed surveyed fjord ice opening: code art and native winter fish data."""
from pathlib import Path
import json
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[1];P=R/'ContentPack'
def main():
 p=P/'content.json';c=json.loads(p.read_text());c['Changes']=[x for x in c['Changes'] if not x.get('LogName','').startswith('R03 ice: ')]
 for patch in c['Changes']:
  loc=patch.get('Entries',{}).get('ArcticPassage_Icefjord') if patch.get('Target')=='Data/Locations' else None
  if not loc:continue
  loc['Fish']=[f for f in loc['Fish'] if not f['Id'].startswith('ArcticPassage_IceFishing_')]
  for fish,chance,level,precedence in [('Halibut',.35,4,-110),('PolarCod',1,0,-100)]:
   loc['Fish'].append({'Id':'ArcticPassage_IceFishing_'+fish,'ItemId':'(O)ArcticPassage_'+fish,
    'Season':'winter','Chance':chance,'MinFishingLevel':level,'Precedence':precedence,
    'BobberPosition':{'X':41,'Y':34,'Width':3,'Height':2},'CanUseTrainingRod':fish=='PolarCod'})
 c['Changes'].append({'LogName':'R03 ice: existing platform marker','Action':'EditMap','Target':'Maps/ArcticPassage_Icefjord',
  'When':{'Season':'winter'},'MapTiles':[{'Position':{'X':40,'Y':35},'Layer':'Buildings','SetProperties':{'Action':'ArcticPassageIceFishing'}}]})
 p.write_text(json.dumps(c,ensure_ascii=False,indent=2)+'\n')
 a=R/'Code/ArcticPassage/Runtime/assets/ice';a.mkdir(parents=True,exist_ok=True)
 for opened in (False,True):
  im=Image.new('RGBA',(48,32));d=ImageDraw.Draw(im)
  d.polygon([(1,11),(6,4),(15,1),(28,0),(40,5),(47,13),(45,24),(37,30),(24,31),(10,27),(1,21)],fill='#6b91ad')
  d.polygon([(1,10),(7,3),(16,0),(28,0),(40,4),(46,12),(43,23),(35,28),(23,29),(10,25),(2,20)],fill='#dceaf1')
  if opened:
   d.polygon([(8,9),(15,4),(26,3),(36,6),(41,13),(38,22),(28,26),(15,24),(7,18)],fill='#7094aa')
   d.polygon([(9,10),(16,6),(26,5),(35,8),(39,14),(36,20),(27,23),(16,22),(9,17)],fill='#142e48')
   d.line((13,17,17,19,25,20,33,18),fill='#2c536b');d.line((15,9,21,7),fill='#60889c')
   for x,y in [(6,7),(12,2),(34,3),(43,13),(32,27)]:d.polygon([(x,y),(x+3,y),(x+2,y+3),(x,y+2)],fill='#f1f4e7')
   for x,y in [(3,10),(9,3),(32,3),(43,17),(28,27)]:d.rectangle((x,y,x+2,y+1),fill='#fbf7de')
  else:
   d.ellipse((5,4,42,25),fill='#b9d1de');d.line((10,9,19,15,27,12,37,18),fill='#7499b1')
   d.line((19,15,17,22),fill='#94b4c8');d.line((27,12,29,7),fill='#8eacbe')
  im.save(a/('open.png' if opened else 'sealed.png'))
 im=Image.new('RGBA',(16,16));d=ImageDraw.Draw(im)
 d.rectangle((6,4,7,15),fill='#6b665d');d.rectangle((3,0,11,8),fill='#263f51',outline='#d4bd82')
 d.line((5,2,9,2),fill='#eee0ab');d.line((5,5,9,5),fill='#9cbdc8');d.line((0,13,14,13),fill='#c1d0cf')
 im.save(a/'marker.png')
 texts={
 'ice.season':('This surveyed ice-fishing station opens in winter. Stay on the timber platform.','固定冰钓点只在冬季开放。请留在木平台上。'),
 'ice.locked':('The fjord boat must be repaired before the ice station can open.','请先修好峡湾渔船，再使用冰钓点。'),
 'ice.ready':('The opening is clear for today. From the end of the timber platform, cast a short distance east into the dark opening. Polar cod; halibut requires fishing level 4. Sea ice is never a footpath.','当天冰洞已清理。从木平台尽头向东短投，落在深色冰洞内。可钓北极鳕，钓鱼4级可遇比目鱼。请勿踏上海冰。'),
 'ice.host':('Ask the host to check and clear the opening. Everyone can fish here once it is open.','请房主检查并清理冰洞，开放后大家都可使用。'),
 'ice.tool':('Hold your pickaxe and interact with this marker to clear the surveyed opening. Repeat the inspection each winter day. Keep both feet on the timber platform.','手持十字镐与此标记互动，检查并凿开固定冰洞。每个冬日需重新清理；全程留在木平台上。'),
 'ice.opened':('The surveyed opening is ready. Cast east from the platform; do not step onto sea ice.','固定冰洞已清理。请站在平台向东短投，不要走上海冰。')}
 for l in ('default','zh'):
  p=R/f'Code/ArcticPassage/Runtime/i18n/{l}.json';d=json.loads(p.read_text())
  for k,v in texts.items():d[k]=v[l=='zh']
  p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
 print('Built R03 surveyed winter ice site: exact 3x2 target; native level-gated fish; code-drawn sprites; no walkable ice.')
if __name__=='__main__':main()
