# coding: utf-8
"""Final visual audit of native hallmark boundaries, revised source and caption clearance."""
import subprocess,json,concurrent.futures,re,math,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];P=json.loads((R/'voice/script/story-v7.json').read_text());B=json.loads((R/'evidence/gameplay-badge-v7.json').read_text());V=R/'renders/Frosthavn-飞越四季-实机标识精修版.mp4';E=R/'evidence'
def sheet(task):
 start,d,fps,layout,name=task
 subprocess.run(['ffmpeg','-y','-v','error','-ss',str(start),'-i',str(V),'-vf',f'trim=duration={d},setpts=PTS-STARTPTS,fps={fps},scale=256:144,tile={layout}','-frames:v','1',str(E/name)],check=True)
tasks=[(s,min(30,P['duration']-s),2,'8x8',f'v7-review-{s:03d}.jpg')for s in range(0,math.ceil(P['duration']),30)]
points=sorted(set([r[k]for r in B['ranges']for k in ['start','end']]+[124.5,133.2]))
tasks +=[(max(0,t-.4),1.2,10,'4x3',f'v7-boundary-{t:.2f}.jpg')for t in points]
if '--market-only' in sys.argv:tasks=[t for t in tasks if 'review-060' in t[4]or'review-090'in t[4]or 83<t[0]<91]
with concurrent.futures.ThreadPoolExecutor(max_workers=3)as pool:list(pool.map(sheet,tasks))
def detail(t):subprocess.run(['ffmpeg','-y','-v','error','-ss',str(t),'-i',str(V),'-frames:v','1',str(E/f'v7-detail-{t}.jpg')],check=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=3)as pool:list(pool.map(detail,[85,87,90.4]if '--market-only'in sys.argv else[33,39,49,74,85,126,132.9,145,168,181,188,197]))
meta=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(V)]))
b=subprocess.run(['ffmpeg','-hide_banner','-i',str(V),'-vf','blackdetect=d=0.12:pix_th=0.025','-an','-f','null','-'],capture_output=True,text=True,check=True);meta['blackIntervals']=re.findall(r'black_start:[^\n]+',b.stderr)
# Packet hashes prove audio is exactly the verified prior AAC stream.
def audiohash(v):return subprocess.check_output(['ffmpeg','-v','error','-i',str(v),'-map','0:a','-c','copy','-f','hash','-hash','sha256','-']).decode().strip()
old=audiohash(R/'renders/Frosthavn-飞越四季-航拍与实录完整版.mp4');new=audiohash(V);assert old==new
meta['audioStreamIdenticalToV6']=True;meta['audioPacketHash']=new;meta['encodedAudioLoudness']=json.loads((E/'director-v6-probe.json').read_text())['encodedAudioLoudness'];meta['subjectiveListeningVerified']=False
(E/'director-v7-probe.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2));print(meta['format']['duration'],meta['blackIntervals'],'audio identical',flush=True)
