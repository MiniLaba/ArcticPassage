import sys,time,json,subprocess,datetime
from pathlib import Path
sys.path.insert(0,str(Path('FrosthavnPromo-v2/tools').resolve()));from capture_expansion import *
key('english');scene('Harbor',32,24,2);cmd('item',Item='(T)TrainingRod');key('s',.05);key('c',.9);out=R/f'raw/gameplay/{datetime.datetime.now():%Y%m%d-%H%M%S}-fishing-native-action-v3.mov'
p=subprocess.Popen(['/usr/sbin/screencapture','-v','-V','65','-A','-R','0,118,1261,720',str(out)],stdout=subprocess.DEVNULL,stderr=subprocess.PIPE);start=time.monotonic();events=[];prev=False
while time.monotonic()-start<64:
 s=json.loads((M/'state.json').read_text());menu=s.get('menu')or''
 if s.get('nibbling') and not prev:
  key('c',.08);events.append({'at':time.monotonic()-start,'action':'native hook on detected nibble'});print('HOOK',flush=True)
 elif 'BobberBar' in menu:
  key('c',.18);time.sleep(.30);events.append({'at':time.monotonic()-start,'action':'native reel input'})
 elif s.get('caught',1)>1:
  print('CAUGHT',s,flush=True);time.sleep(2);key('c',.1);break
 prev=s.get('nibbling');time.sleep(.08)
p.communicate();(R/f'evidence/{out.stem}-recording.json').write_text(json.dumps({'file':str(out.relative_to(R)),'events':events,'stateAtEnd':json.loads((M/'state.json').read_text()),'staging':'No fish granted; real existing cast, native nibble and keyboard minigame input. Source-save fish count started at1.'},ensure_ascii=False,indent=2));print(out,flush=True)
