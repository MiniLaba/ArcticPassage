"""Narrative edit, upgraded code MG, synthetic English VO and Chinese captions."""
from pathlib import Path
import subprocess,json,concurrent.futures,hashlib,sys
R=Path(__file__).resolve().parents[1];P=json.loads((R/'voice/script/story-v4.json').read_text());old=json.loads((R/'cut-v3.json').read_text());caps=json.loads((R/'voice/script/captions.json').read_text());D=P['duration'];O=R/'renders/director-edition-parts';O.mkdir(exist_ok=True)
oldparts={s['id']:R/f'renders/full-edition-parts/{i:02}-{s["id"]}.mp4'for i,s in enumerate(old['shots'])}
def ff(a):subprocess.run(['ffmpeg','-y','-hide_banner','-loglevel','error']+list(map(str,a)),check=True)
def prepare(s):
 if s['id']not in ['window','four-seasons','outro']:return oldparts[s['id']]
 shot='panorama'if s['id']=='four-seasons'else s['id'];f=O/(shot+'.mp4');
 if '--resume-picture' in sys.argv and f.exists():return f
 vf=f'scale=1920:1080,setpts=(PTS-STARTPTS)/{s["speed"]},fps=30,setsar=1,setparams=range=tv:color_primaries=bt709:color_trc=bt709:colorspace=bt709,tpad=stop_mode=clone:stop_duration=0.067'
 ff(['-i',R/f'renders/mg-v4/{shot}.mp4','-t',s['duration'],'-an','-vf',vf,'-c:v','libx264','-preset','fast','-crf','17','-pix_fmt','yuv420p','-threads','2',f]);return f
with concurrent.futures.ThreadPoolExecutor(max_workers=3)as pool:parts=list(pool.map(prepare,P['shots']))
args=[];filters=[]
for i,part in enumerate(parts):args+=['-i',part];filters.append(f'[{i}:v]settb=AVTB,setpts=PTS-STARTPTS[v{i}]')
prev='v0'
for i,s in enumerate(P['shots'][1:],1):
 o=s.get('overlap',0);out=f'c{i}'
 filters.append(f'[{prev}][v{i}]xfade=transition=fade:duration={o}:offset={s["start"]}[{out}]'if o else f'[{prev}][v{i}]concat=n=2:v=1:a=0[{out}]');prev=out
picture=O/'picture.mp4'
if '--resume-picture' not in sys.argv:ff(args+['-filter_complex_threads','2','-filter_complex',';'.join(filters),'-map',f'[{prev}]','-t',D,'-r','30','-an','-c:v','libx264','-preset','fast','-crf','17','-pix_fmt','yuv420p','-threads','4',picture]);print('Narrative picture complete',flush=True)
args=['-i',picture];fg=[];prev='0:v'
for i,c in enumerate(caps,1):
 args+=['-i',R/c['png']];n=f't{i}';fg.append(f'[{prev}][{i}:v]overlay={c["overlayX"]}:{c["overlayY"]}:eof_action=repeat:enable=\'gte(t,{c["start"]})*lt(t,{c["displayEnd"]})\'[{n}]');prev=n
args+=['-i',R/'voice/Director-master.wav'];audioIndex=len(caps)+1
final=R/'renders/Frosthavn-从一张机票到一段生活-英文解说中字版.mp4'
ff(args+['-filter_complex_threads','2','-filter_complex',';'.join(fg),'-map',f'[{prev}]','-map',f'{audioIndex}:a','-t',D,'-r','30','-c:v','libx264','-preset','fast','-crf','17','-pix_fmt','yuv420p','-threads','4','-c:a','aac','-b:a','256k','-ar','48000','-movflags','+faststart','-metadata','title=Frosthavn — From a ticket to a life','-metadata','comment=Original code-generated theme animation and genuine native gameplay. Synthetic English narration: Kokoro-82M af_heart. Chinese subtitles. Music: Life in Silico by Scott Buckley, CC BY 4.0, www.scottbuckley.com.au. Edited excerpt.',final])
report={'file':str(final.relative_to(R)),'duration':D,'sourcePlan':'voice/script/story-v4.json','captions':'voice/script/captions.json','syntheticNarration':True,'master':'voice/Director-master.wav','masterSha256':hashlib.sha256((R/'voice/Director-master.wav').read_bytes()).hexdigest(),'videoSha256':hashlib.sha256(final.read_bytes()).hexdigest(),'sourceShotOrder':[s['id']for s in P['shots']],'captionSha256':hashlib.sha256((R/'voice/script/captions.json').read_bytes()).hexdigest(),'subjectiveListeningVerified':False}
(R/'evidence/director-edition-edit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(final,flush=True)
