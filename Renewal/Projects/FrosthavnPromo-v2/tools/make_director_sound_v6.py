"""Original restrained cabin, landing and arctic-air sound layers. No bird sounds."""
from array import array
from pathlib import Path
import math,random,wave,json
R=Path(__file__).resolve().parents[1];sr=48000;plan=json.loads((R/'voice/script/story-v6.json').read_text());D=plan['duration'];N=round(D*sr);left=array('f',[0])*N;right=array('f',[0])*N;rng=random.Random(271029)
def smooth(x):x=max(0,min(1,x));return x*x*(3-2*x)
def layer(start,duration,kind,level,pan=0):
 state=0;prev=0;starti=int(start*sr);n=int(duration*sr)
 for i in range(n):
  j=starti+i
  if j>=N:break
  t=i/sr;white=rng.random()*2-1;state=.987*state+.013*white;env=smooth(t/1.1)*smooth((duration-t)/1.4)
  if kind=='cabin':v=(.55*math.sin(2*math.pi*53*t)+.18*math.sin(2*math.pi*106.5*t)+state*3)*(1+.025*math.sin(t*2.4))*env
  elif kind=='wind':v=(white*.03+state*3.5)*env*(.65+.35*math.sin(t*.7+.5)**2)
  elif kind=='touchdown':v=(math.sin(2*math.pi*(43*t-7*t*t))*.7+state*2.2)*math.exp(-t*9)*smooth(t/.012)
  else:v=(white-prev)*.15*math.sin(math.pi*t/duration)**2
  prev=white;v*=level;left[j]+=v*math.sqrt((1-pan)/2);right[j]+=v*math.sqrt((1+pan)/2)
shot={s['id']:s for s in plan['shots']};win=shot['window'];pano=shot['four-seasons']
layer(win['start'],win['duration']+5.7,'cabin',.018)
layer(win['start']+.3,win['duration']-1,'wind',.027,-.1)
layer(win['start']+24,.75,'touchdown',.075)
layer(pano['start'],pano['duration'],'wind',.021,.1)
for name in ['harbour','camp','glacier','night','harbour-reveal','camp-reveal','glacier-reveal']:
 s=shot[name];layer(s['start'],s['duration'],'wind',.014,-.1)
out=array('h')
for l,r in zip(left,right):out.append(round(max(-1,min(1,l))*32767));out.append(round(max(-1,min(1,r))*32767))
p=R/'voice/DirectorAtmosphere-v6.wav'
with wave.open(str(p),'wb')as w:w.setnchannels(2);w.setsampwidth(2);w.setframerate(sr);w.writeframes(out.tobytes())
(R/'evidence/director-v6-sound-design.json').write_text(json.dumps({'duration':D,'seed':271029,'source':'original procedural sound design','recordedGameAudio':False,'cues':[{'at':win['start'],'role':'cabin air'},{'at':win['start']+24,'role':'touchdown'},{'at':pano['start'],'role':'four seasons fjord air'}],'paperGain':0.9,'subjectiveListeningVerified':False},indent=2))
print(p)
