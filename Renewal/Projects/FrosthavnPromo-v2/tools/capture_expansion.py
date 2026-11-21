"""Native footage only. Scene setup remains in a disposable in-memory save."""
from pathlib import Path
import subprocess,json,time,datetime,hashlib,argparse
R=Path(__file__).resolve().parents[1];M=R/'.film-mods/FilmDirector';K='/private/tmp/frosthavn-game-key'
def cmd(kind,**kw):
 c={'Id':str(time.time_ns()),'Kind':kind,**kw};p=M/'command.json';tmp=M/'command.tmp';tmp.write_text(json.dumps(c));tmp.replace(p)
 for _ in range(40):
  time.sleep(.15)
  try:
   if json.loads((M/'state.json').read_text()).get('lastCommand')==c['Id']:return
  except (OSError,ValueError):pass
 raise RuntimeError('Filming helper did not acknowledge command')
def key(k,d=.10):
 args=[K,k.split('@')[0],*k.split('@')[1:]] if '@' in k else [K,k,str(d)]
 subprocess.run(args,check=True,stdout=subprocess.DEVNULL)
def scene(loc,x,y,facing=2,timeOfDay=1200,zoom=.75):
 cmd('scene',Location=loc,X=x,Y=y,Time=timeOfDay,Facing=facing,Zoom=zoom);time.sleep(1)
def record(name,seconds,actions):
 wins=json.loads(subprocess.check_output(['/private/tmp/frosthavn-window-info']));w=next(x for x in wins if x['onScreen'] and 'Stardew Valley' in x['title']);b=w['bounds'];rect=f"{round(b['X'])},{round(b['Y'])+28},{round(b['Width'])},{round(b['Height'])-28}"
 stamp=datetime.datetime.now().strftime('%Y%m%d-%H%M%S');out=R/f'raw/gameplay/{stamp}-{name}.mov';print('RECORD',name,out.name,flush=True)
 p=subprocess.Popen(['/usr/sbin/screencapture','-v','-V',str(seconds),'-A','-R',rect,str(out)],stdout=subprocess.DEVNULL,stderr=subprocess.PIPE);start=time.monotonic();events=[]
 for at,k,d in actions:
  time.sleep(max(0,at-(time.monotonic()-start)));key(k,d);events.append({'at':round(time.monotonic()-start-d,3),'key':k,'held':d})
 err=p.communicate()[1].decode();
 if p.returncode:raise RuntimeError(err)
 probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration,size','-show_entries','stream=codec_name,codec_type,width,height,avg_frame_rate,nb_frames','-of','json',str(out)]))
 report={'file':str(out.relative_to(R)),'scene':name,'probe':probe,'events':events,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'method':'macOS native screencapture region, real engine','staging':'Disposable FilmHarbor in-memory setup; location, time and some unlocked prerequisites staged. No automatic completion or replacement game animation.','stateAtEnd':json.loads((M/'state.json').read_text()),'visualVerified':False}
 (R/f'evidence/{stamp}-{name}-recording.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print('DONE',name,flush=True);return out
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('group');a=p.parse_args();key('english')
 if a.group=='camp':
  cmd('prep',Day=7);scene('WinterCamp',19,38,0);record('camp-walk-v3',12,[(2,'w',.7),(4,'d',.6),(7,'a',.5)])
  scene('WinterCamp',20,36,0);record('snow-lesson-v3',18,[(1,'up',.05),(2,'x',.1),(5,'right',.1),(6,'return',.1),(9,'left',.1),(10,'return',.1),(13,'right',.1),(14,'return',.1)])
 elif a.group=='sled':
  scene('Tundra',28,39,0);record('sled-trip-v3',18,[(1,'up',.05),(2,'x',.1),(5,'click@160@598',.1),(6,'c',.12)])
 elif a.group=='journal':
  scene('ResearchStation',12,12,0);record('research-guide-v3',20,[(2,'k',.1),(5,'4',.1),(8,'down',.1),(10,'5',.1),(13,'6',.1),(17,'escape',.1)])
 elif a.group=='glacier':
  scene('Glacier',39,22,0);record('glacier-walk-v3',16,[(2,'w',.8),(6,'d',.8),(10,'a',.6)])

 elif a.group=='market':
  scene('Fishery',8,7,0);cmd('item',Item='(O)ArcticPassage_PolarCod',Count=3)
  record('market-sale-v3',15,[(1,'w',.05),(2,'x',.1),(5,'tab',.1),(6,'tab',.1),(7,'return',.1),(9,'return',.1),(11,'return',.1),(13,'escape',.1)])
 elif a.group=='icework':
  scene('Icefjord',40,34,2);key('4',.1)
  record('ice-opening-v3',13,[(1,'s',.05),(2,'x',.1),(6,'6',.1),(8,'c',.9)])
 elif a.group=='community':
  scene('CommunityHouse',12,13,0);record('community-house-v3',12,[(2,'w',.9),(5,'d',.7),(8,'a',.5)])
 elif a.group=='nora':
  scene('Airstrip',31,33,0);cmd('npc',Npc='ArcticPassage_Nora',X=31,Y=32)
  record('nora-dialogue-v3',15,[(.7,'w',.05),(1.5,'x',.1),(9,'x',.1),(12,'escape',.1)])

 elif a.group=='residents':
  cmd('item',Item='(T)Axe')
  for loc,npc,x,y in [('Fishery','Ida',6,12),('Harbor','Roan',25,24),('Tundra','Mira',25,33),('ResearchStation','Levin',12,14)]:
   scene(loc,x,y,0);cmd('npc',Npc='ArcticPassage_'+npc,X=x,Y=y-1)
   record(npc.lower()+'-dialogue-v3',9,[(.6,'w',.05),(1.5,'x',.1)])
