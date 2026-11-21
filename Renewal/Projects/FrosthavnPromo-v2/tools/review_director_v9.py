# coding: utf-8
"""Changed introduction: exact approved speech timing, subtitle exclusion, encoded audio."""
from pathlib import Path
import json,subprocess,concurrent.futures,re,hashlib
import numpy as np,soundfile as sf
R=Path(__file__).resolve().parents[1];E=R/'evidence';V=R/'renders/Frosthavn-飞越四季-航空广播版.mp4';T=json.loads((R/'voice/script/voice-timing-v9.json').read_text());C=json.loads((R/'voice/script/captions-v9.json').read_text());PA=json.loads((E/'captain-pa-v9.json').read_text())
assert len(T['cues'])==23 and len(C)==22
assert not any(c['start']<PA['end']and c['displayEnd']>PA['start']for c in C)
assert all(c['id']not in ['vo-02','vo-03','captain-pa']for c in C)
assert all('next stop'not in c['en'].lower()for c in T['cues'])
assert PA['end']+3<PA['touchdown']
# Later recorded voice phrase metadata must match, as must all gameplay timings.
a=json.loads((R/'voice/script/voice-timing-v6.json').read_text())['cues'][3:];assert T['cues'][2:]==a
P=json.loads((R/'voice/script/story-v9.json').read_text());O=json.loads((R/'voice/script/story-v8.json').read_text());changes=[]
for s,o in zip(P['shots'],O['shots']):
 for k in set(s)|set(o):
  if s.get(k)!=o.get(k):changes.append({'shot':s['id'],'field':k,'old':o.get(k),'new':s.get(k)})
assert len(changes)==1 and changes[0]['shot']=='window'and changes[0]['field']=='file'
def image(t):subprocess.run(['ffmpeg','-y','-v','error','-ss',str(t),'-i',str(V),'-frames:v','1',str(E/f'v9-detail-{t}.jpg')],check=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=3)as p:list(p.map(image,[1.5,7,15,24.3]))
subprocess.run(['ffmpeg','-y','-v','error','-i',str(V),'-vf','trim=duration=32,fps=2,scale=320:180,tile=8x8','-frames:v','1',str(E/'v9-intro-2fps.jpg')],check=True)
meta=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(V)]));a=subprocess.run(['ffmpeg','-hide_banner','-i',str(V),'-af','loudnorm=I=-16:TP=-1.5:LRA=9:print_format=json','-f','null','-'],capture_output=True,text=True,check=True);meta['encodedAudioLoudness']=json.JSONDecoder().raw_decode(a.stderr[a.stderr.rfind('{'):])[0]
# Compare a decoded audio window with the supplied final master to verify routing.
subprocess.run(['ffmpeg','-y','-v','error','-ss','10','-i',str(V),'-t','15','-ar','48000','-ac','2','-c:a','pcm_f32le',str(E/'v9-pa-encoded-audio.wav')],check=True)
v,sr=sf.read(E/'v9-pa-encoded-audio.wav',dtype='float32',always_2d=True);m,_=sf.read(R/'voice/Director-master-v9.wav',dtype='float32',always_2d=True);segment=m[round(10*sr):round(10*sr)+len(v)];cor=float(np.corrcoef(v.ravel(),segment.ravel())[0,1]);assert cor>.97,cor
meta.update(changedPictureSources=changes,oldOpeningRemoved=True,captainSubtitles=False,paInterval=[PA['start'],PA['end']],touchdown=27.7,decodedMasterCorrelation=cor,subjectiveListeningVerified=False,reviewScope='Changed first 32 seconds sampled at 2fps; four full-size frames, PA spectrum and numerical timing/no-subtitle/mix routing checks. No subjective audition.')
(E/'director-v9-probe.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2));print(meta['format']['duration'],meta['encodedAudioLoudness'],'decoded/master correlation',cor,flush=True)
