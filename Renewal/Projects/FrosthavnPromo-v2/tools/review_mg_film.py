"""Inspect the encoded delivery, not just intermediate frames."""
import subprocess,json,concurrent.futures,re
from pathlib import Path
R=Path(__file__).resolve().parents[1];V=R/'renders/Frosthavn-穿过机窗抵达北极-MG提升版-78s.mp4';E=R/'evidence'
def sheet(task):
 start,d,fps,layout,name=task
 subprocess.run(['ffmpeg','-y','-v','error','-ss',str(start),'-i',str(V),'-t',str(d),'-vf',f'fps={fps},scale=320:180,tile={layout}','-frames:v','1',str(E/name)],check=True)
tasks=[(s,26,2,'8x7',f'mg-review-{s:02d}.jpg')for s in (0,26,52)]
tasks +=[(s-.5,1.5,10,'5x3',f'mg-transition-{s:.1f}.jpg') for s in (3.7,19.4,25.4,42.9,72.3)]
with concurrent.futures.ThreadPoolExecutor(max_workers=3)as p:list(p.map(sheet,tasks))
meta=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(V)]))
a=subprocess.run(['ffmpeg','-hide_banner','-i',str(V),'-af','loudnorm=I=-16:TP=-1.5:LRA=9:print_format=json','-vf','blackdetect=d=0.12:pix_th=0.025','-f','null','-'],capture_output=True,text=True,check=True)
meta['encodedAudioLoudness']=json.JSONDecoder().raw_decode(a.stderr[a.stderr.rfind('{'):])[0]
meta['blackIntervals']=re.findall(r'black_start:[^\n]+',a.stderr)
meta['limits']='Full-film 2fps visual contact sheets and 10fps transition strips; encoded media checks. Not a frame-by-frame real-time playback or subjective listening approval. Sheet padding is not video black frames.'
(E/'mg-edition-probe.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2));print(meta['format']['duration'],meta['encodedAudioLoudness'],meta['blackIntervals'])
