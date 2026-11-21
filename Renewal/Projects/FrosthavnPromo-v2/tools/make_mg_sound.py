"""Original restrained cabin, landing and arctic-air sound layers. No bird sounds."""
from array import array
from pathlib import Path
import math,random,wave,json
R=Path(__file__).resolve().parents[1];sr=48000;D=78.3;N=round(D*sr);left=array('f',[0])*N;right=array('f',[0])*N;rng=random.Random(271029)
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
layer(3.7,16,'cabin',.018)
layer(4,13.5,'wind',.027,-.1)
layer(15.1,.75,'touchdown',.075)
layer(25.4,17.7,'wind',.021,.1)
layer(54.9,7,'wind',.015)
layer(66.9,6,'wind',.013,-.2)
out=array('h')
for l,r in zip(left,right):out.append(round(max(-1,min(1,l))*32767));out.append(round(max(-1,min(1,r))*32767))
p=R/'public/mg-atmosphere-sfx.wav'
with wave.open(str(p),'wb')as w:w.setnchannels(2);w.setsampwidth(2);w.setframerate(sr);w.writeframes(out.tobytes())
(R/'evidence/mg-sound-design.json').write_text(json.dumps({'duration':D,'seed':271029,'source':'original procedural sound design','recordedGameAudio':False,'cues':[{'at':3.7,'role':'cabin air and propeller bed'},{'at':15.1,'role':'gentle touchdown','visual':'window t=11.4'},{'at':25.4,'role':'fjord air'},{'at':54.9,'role':'harbour air'}],'paperGain':0.9,'subjectiveListeningVerified':False},indent=2))
print(p)
