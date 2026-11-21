# coding: utf-8
"""Review corrected window only and verify source/audio continuity against V7."""
from pathlib import Path
import json,subprocess,concurrent.futures,hashlib
R=Path(__file__).resolve().parents[1];E=R/'evidence';V=R/'renders/Frosthavn-飞越四季-机翼修正版.mp4'
def sheet(a):
 start,d,fps,layout,name=a
 subprocess.run(['ffmpeg','-y','-v','error','-ss',str(start),'-i',str(V),'-vf',f'trim=duration={d},setpts=PTS-STARTPTS,fps={fps},scale=320:180,tile={layout}','-frames:v','1',str(E/name)],check=True)
tasks=[(0,32,2,'8x8','v8-intro-2fps.jpg'),(3.3,1.2,10,'4x3','v8-cut-window-10fps.jpg'),(31,1.2,10,'4x3','v8-cut-native-10fps.jpg'),(11.4,3.2,10,'8x4','v8-base-turn-10fps.jpg'),(18.4,3.2,10,'8x4','v8-final-turn-10fps.jpg'),(27.7,3.2,10,'8x4','v8-rollout-10fps.jpg')]
with concurrent.futures.ThreadPoolExecutor(max_workers=3)as pool:list(pool.map(sheet,tasks))
for t in [7,16.7,24.7,30.7]:subprocess.run(['ffmpeg','-y','-v','error','-ss',str(t),'-i',str(V),'-frames:v','1',str(E/f'v8-detail-{t}.jpg')],check=True)
P=json.loads((R/'voice/script/story-v8.json').read_text());O=json.loads((R/'voice/script/story-v7.json').read_text());delta=[]
for s,o in zip(P['shots'],O['shots']):
 for k in set(s)|set(o):
  if s.get(k)!=o.get(k):delta.append({'shot':s['id'],'field':k,'old':o.get(k),'new':s.get(k)})
assert len(delta)==1 and delta[0]['shot']=='window'and delta[0]['field']=='file'
def ah(v):return subprocess.check_output(['ffmpeg','-v','error','-i',str(v),'-map','0:a','-c','copy','-f','hash','-hash','sha256','-']).decode().strip()
h=ah(V);assert h==ah(R/'renders/Frosthavn-飞越四季-实机标识精修版.mp4')
meta=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(V)]));meta.update(changesFromV7=delta,audioIdenticalToV7=True,audioPacketHash=h,subjectiveListeningVerified=False,reviewScope='Corrected first 32 seconds at 2fps; entry and exit at 10fps; two turns and rollout at 10fps; four full-size frames. Remaining source selections/caption configuration/hallmark/audio unchanged.')
(E/'director-v8-probe.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2));print(meta['format']['duration'],'only window source changed; audio identical',flush=True)
