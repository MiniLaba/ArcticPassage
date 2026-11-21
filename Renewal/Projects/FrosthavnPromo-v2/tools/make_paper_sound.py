"""Original deterministic paper-fold sound design for CG, not recorded game audio."""
import numpy as np, wave, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SR=48000;D=6
rng=np.random.default_rng(27028)
out=np.zeros((SR*D,2),dtype=np.float64)
def rustle(at,duration,level,pan):
 n=int(duration*SR);t=np.arange(n)/SR
 noise=rng.standard_normal(n)
 # Band-shaped friction with tiny independent fibre transients.
 f=np.fft.rfftfreq(n,1/SR);shape=(f/(f+700))*np.exp(-f/5500)
 noise=np.fft.irfft(np.fft.rfft(noise)*shape,n=n)
 env=np.sin(np.pi*t/duration)**2
 grain=np.zeros(n)
 for _ in range(int(duration*48)):
  start=int(rng.uniform(0,max(1,n-250)));length=min(250,n-start)
  grain[start:start+length]+=rng.uniform(.02,.09)*rng.standard_normal(length)*np.exp(-np.arange(length)/65)
 sig=(noise*.36+grain)*env*level
 start=int(at*SR);end=min(start+n,len(out));sig=sig[:end-start]
 out[start:end,0]+=sig*np.sqrt((1-pan)/2);out[start:end,1]+=sig*np.sqrt((1+pan)/2)
rustle(1.08,1.2,.3,-.3);rustle(2.1,1.25,.22,.15);rustle(3.35,.9,.16,.4)
dest=ROOT/'public/paper-fold-sfx.wav'
with wave.open(str(dest),'wb') as f:
 f.setnchannels(2);f.setsampwidth(2);f.setframerate(SR);f.writeframes((np.clip(out,-1,1)*32767).astype('<i2').tobytes())
(ROOT/'evidence/cg-sound.json').write_text(json.dumps({'file':'public/paper-fold-sfx.wav','source':'original deterministic noise/granular synthesis','seed':27028,'recording':False,'role':'CG paper folds only','cues':[1.08,2.1,3.35],'subjectiveListeningVerified':False},indent=2))
print(dest)
