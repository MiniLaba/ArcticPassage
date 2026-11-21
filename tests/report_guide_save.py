"""Read only the two named QA saves; report minimal persistent notebook state."""
from pathlib import Path
import xml.etree.ElementTree as ET
import json

root=Path('/Users/moonmoonbird/.config/StardewValley/Saves')
report={}
for name in ['ArcticQA_451755789','ArcticFlowQA_451755789']:
 doc=ET.parse(root/name/name).getroot();player=doc.find('player')
 notes={}
 for item in player.findall('./modData/item'):
  key=item.findtext('./key/string')
  if key and key.startswith('WhiteBay.ArcticPassage/FieldGuide/'):
   notes[key]=item.findtext('./value/string')
 report[name]={'day':doc.findtext('dayOfMonth'),'season':doc.findtext('currentSeason'),
               'money':player.findtext('money'),'notes':notes}
assert report['ArcticQA_451755789']['day']=='6'
assert report['ArcticQA_451755789']['money']=='1618'
assert not report['ArcticQA_451755789']['notes']
flow=report['ArcticFlowQA_451755789']
assert flow['day']=='8' and flow['money']=='1683'
assert all('WhiteBay.ArcticPassage/FieldGuide/'+k in flow['notes'] for k in ['rock','harbor','ice'])
out=Path(__file__).resolve().parents[1]/'docs/GuideSaveState_074.json'
out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('PASS: three original observation stamps serialized on spring 8; wallet unchanged. Original QA spring 6 has no notes.')
