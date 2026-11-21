# coding: utf-8
"""Review final encoded film with 2fps contacts and 10fps transitions."""
import subprocess,json,concurrent.futures,re,math,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];P=json.loads((R/'voice/script/story-v5.json').read_text());V=R/'renders/Frosthavn-一条线带你回家-导演精修版.mp4';E=R/'evidence'
def sheet(task):
 start,d,fps,layout,name=task
 subprocess.run(['ffmpeg','-y','-v','error','-ss',str(start),'-i',str(V),'-vf',f'trim=duration={d},setpts=PTS-STARTPTS,fps={fps},scale=320:180,tile={layout}','-frames:v','1',str(E/name)],check=True)
tasks=[(s,min(30,P['duration']-s),2,'8x8',f'v5-review-{s:03d}.jpg')for s in range(0,math.ceil(P['duration']),30)]
ids=[s['id'] for s in P['shots'][1:]]
tasks +=[(max(0,s['start']-.4),1.2,10,'4x3',f'v5-transition-{s["id"]}.jpg')for s in P['shots']if s['id']in ids]
tasks +=[(160.5,6,10,'10x6','v5-window-dolly-10fps.jpg')]
if '--tail-only' in sys.argv:tasks=[t for t in tasks if t[0]>=150]
with concurrent.futures.ThreadPoolExecutor(max_workers=3)as p:list(p.map(sheet,tasks))
meta=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(V)]))
a=subprocess.run(['ffmpeg','-hide_banner','-i',str(V),'-af','loudnorm=I=-16:TP=-1.5:LRA=9:print_format=json','-vf','blackdetect=d=0.12:pix_th=0.025','-f','null','-'],capture_output=True,text=True,check=True)
meta['encodedAudioLoudness']=json.JSONDecoder().raw_decode(a.stderr[a.stderr.rfind('{'):])[0];meta['blackIntervals']=re.findall(r'black_start:[^\n]+',a.stderr)
meta['limits']='Visual review via final MP4 full-film 2fps contacts, selected 10fps transition strips, and full-size detail frames. Not subjective listening or frame-by-frame realtime playback certification. Sheet padding is not black video frames.'
(E/'director-v5-probe.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2));print(meta['format']['duration'],meta['encodedAudioLoudness'],meta['blackIntervals'])
