# coding: utf-8
"""Narrative edit, upgraded code MG, synthetic English VO and Chinese captions."""
from pathlib import Path
import subprocess,json,concurrent.futures,hashlib,sys
R=Path(__file__).resolve().parents[1];P=json.loads((R/'voice/script/story-v9.json').read_text());old=json.loads((R/'cut-v3.json').read_text());caps=json.loads((R/'voice/script/captions-v9.json').read_text());D=P['duration'];O=R/'renders/director-v9-parts';O.mkdir(exist_ok=True)
oldparts={s['id']:R/f'renders/full-edition-parts/{i:02}-{s["id"]}.mp4'for i,s in enumerate(old['shots'])}
def ff(a):subprocess.run(['ffmpeg','-y','-hide_banner','-loglevel','error']+list(map(str,a)),check=True)
def prepare(s):
 if s['id']=='window':
  f=O/'window.mp4'
  if '--resume-picture'in sys.argv and f.exists():return f
  ff(['-i',R/'renders/mg-v9/window.mp4','-t',s['duration'],'-an','-vf','scale=1920:1080,setsar=1,fps=30,setparams=range=tv:color_primaries=bt709:color_trc=bt709:colorspace=bt709','-c:v','libx264','-preset','fast','-crf','17','-pix_fmt','yuv420p','-threads','2',f]);return f
 if s['id']=='sled':return R/'renders/director-v7-parts/sled.mp4'
 if s['type']!='cg':return oldparts[s['id']]
 shot='panorama'if s['id']=='four-seasons'else s['id'];return R/f'renders/director-v6-parts/{shot}.mp4'
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
events=json.loads((R/'evidence/v6-line-transitions.json').read_text())
for i,e in enumerate(events,len(caps)+1):
 args+=['-i',R/e['file']];n=f'line{i}';fg.append(f'[{i}:v]setpts=PTS+{e["start"]}/TB[l{i}]');fg.append(f'[{prev}][l{i}]overlay=0:0:eof_action=pass:enable=\'gte(t,{e["start"]})*lt(t,{e["start"]+e["duration"]})\'[{n}]');prev=n
# One alpha stream is split into three placement anchors, used only on native ranges.
badge=json.loads((R/'evidence/gameplay-badge-v7.json').read_text());badgeIndex=len(caps)+len(events)+1
args+=['-i',R/badge['video']];fg.append(f'[{badgeIndex}:v]split=3[badgeLeft][badgeCenter][badgeBottom]')
for anchor,label in [('left','badgeLeft'),('center','badgeCenter'),('bottom','badgeBottom')]:
 rs=[r for r in badge['ranges']if r['anchor']==anchor];expr='+'.join(f'gte(t,{r["start"]})*lt(t,{r["end"]})'for r in rs);x,y=rs[0]['x'],rs[0]['y'];n='marked'+anchor
 fg.append(f"[{prev}][{label}]overlay={x}:{y}:eof_action=pass:enable='{expr}'[{n}]");prev=n
# New approved welcome, captain speech and microphone static use the V9 master.
args+=['-i',R/'voice/Director-master-v9.wav'];audioIndex=badgeIndex+1
final=R/'renders/Frosthavn-飞越四季-航空广播版.mp4'
ff(args+['-filter_complex_threads','2','-filter_complex',';'.join(fg),'-map',f'[{prev}]','-map',f'{audioIndex}:a','-t',D,'-r','30','-c:v','libx264','-preset','fast','-crf','17','-pix_fmt','yuv420p','-threads','4','-c:a','aac','-b:a','256k','-ar','48000','-movflags','+faststart','-metadata','title=Frosthavn — A journey through the Arctic year','-metadata','comment=Original code-generated theme animation and genuine native gameplay. Synthetic English narration: Kokoro-82M af_heart; captain PA: am_michael with authored static. Chinese subtitles. Music: Life in Silico by Scott Buckley, CC BY 4.0, www.scottbuckley.com.au. Edited excerpt.',final])
report={'file':str(final.relative_to(R)),'duration':D,'sourcePlan':'voice/script/story-v9.json','captions':'voice/script/captions-v9.json','syntheticNarration':True,'master':'voice/Director-master-v9.wav','masterSha256':hashlib.sha256((R/'voice/Director-master-v9.wav').read_bytes()).hexdigest(),'videoSha256':hashlib.sha256(final.read_bytes()).hexdigest(),'sourceShotOrder':[s['id']for s in P['shots']],'captionSha256':hashlib.sha256((R/'voice/script/captions-v9.json').read_bytes()).hexdigest(),'subjectiveListeningVerified':False,'nativeHallmark':'evidence/gameplay-badge-v7.json','captainPA':'evidence/captain-pa-v9.json','captainSubtitles':False}
(R/'evidence/director-v9-edit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(final,flush=True)
