"""Read only named test saves; verify the camp overnight's persisted state."""
from pathlib import Path
import xml.etree.ElementTree as ET
import json

ROOT=Path(__file__).resolve().parents[1]
SAVES=Path('/Users/moonmoonbird/.config/StardewValley/Saves')
report={}
for name in ['ArcticQA_451755789','ArcticFlowQA_451755789','ArcticWinterQA_451755789']:
    doc=ET.parse(SAVES/name/name).getroot();p=doc.find('player')
    notes={item.findtext('./key/string'):item.findtext('./value/string')
           for item in p.findall('./modData/item')
           if (item.findtext('./key/string') or '').startswith('WhiteBay.ArcticPassage/FieldGuide/')}
    report[name]={'day':doc.findtext('dayOfMonth'),'season':doc.findtext('currentSeason'),
                  'money':p.findtext('money'),'location':p.findtext('currentLocation'),
                  'lastSleepLocation':p.findtext('lastSleepLocation'),'notes':notes}
original=report['ArcticQA_451755789'];winter=report['ArcticWinterQA_451755789'];flow=report['ArcticFlowQA_451755789']
assert (original['day'],original['season'],original['money'],original['notes'])==('6','spring','1618',{})
assert (winter['day'],winter['season'],winter['money'],winter['notes'])==('7','winter','1618',{})
assert (flow['day'],flow['season'],flow['money'])==('10','spring','1683')
assert flow['lastSleepLocation']=='ArcticPassage_ResearchStation'
assert flow['notes']['WhiteBay.ArcticPassage/FieldGuide/camp']=='1|spring|8|1840'
for key,value in {'harbor':'1|spring|7|1010','ice':'1|spring|7|1150','rock':'1|spring|7|1250'}.items():
    assert flow['notes']['WhiteBay.ArcticPassage/FieldGuide/'+key]==value
(ROOT/'docs/CampSaveState_075.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print('PASS: Flow spring 10, research-station bed, 1683 gold, four original note stamps. Original spring and winter QA saves remain unchanged.')
