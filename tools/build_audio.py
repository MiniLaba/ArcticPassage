"""Original periodic, non-tonal environmental sound design; no field recordings.

Uses spectral noise and slow periodic envelopes for seamless coastal wind/surf,
open tundra wind, and a quiet indoor wind-through-walls bed. No bird/insect cues.
"""
from pathlib import Path
import wave
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
RATE=22050;SECONDS=36;N=RATE*SECONDS
T=np.arange(N)/RATE

def noise(seed,low,high):
 rng=np.random.default_rng(seed);f=np.fft.rfftfreq(N,1/RATE)
 spectrum=(rng.normal(size=len(f))+1j*rng.normal(size=len(f)))
 shape=(f+35)**-.55*(1-np.exp(-(f/low)**4))*np.exp(-(f/high)**2)
 shape[0]=0
 a=np.fft.irfft(spectrum*shape,n=N)
 return a/np.sqrt(np.mean(a*a))

def envelope(cycles,phase=0):
 return (.5+.5*np.cos(2*np.pi*cycles*T/SECONDS+phase))**2

def render(name,kind,rms):
 channels=[]
 for side in range(2):
  wind=noise(120+side,65,1150)
  gust=.36+.22*envelope(2,.4)+.18*envelope(5,1.2)+.08*envelope(11,side*.1)
  a=wind*gust
  if kind=='coast':
   surf=noise(540+side,120,2400)
   a+=surf*(.1+.52*envelope(7,.2)+.16*envelope(13,1.4))
  elif kind=='tundra':
   a+=noise(720+side,140,1500)*(.03+.12*envelope(4,1.3))
  else:
   a=noise(980+side,65,420)*(.45+.10*envelope(3,.5))
  channels.append(a)
 stereo=np.stack(channels,axis=1)
 # Mostly shared low wind avoids an exaggerated headphone-wide stereo hiss.
 mono=stereo.mean(axis=1);stereo=.35*stereo+.65*mono[:,None]
 stereo*=rms/np.sqrt(np.mean(stereo*stereo))
 assert np.max(np.abs(stereo))<.85
 pcm=(np.clip(stereo,-1,1)*32767).astype('<i2')
 path=ROOT/f'ContentPack/assets/audio/{name}.wav';path.parent.mkdir(parents=True,exist_ok=True)
 with wave.open(str(path),'wb') as w:
  w.setnchannels(2);w.setsampwidth(2);w.setframerate(RATE);w.writeframes(pcm.tobytes())
 print(name, '36s stereo loop', f'RMS={np.sqrt(np.mean(stereo*stereo)):.3f}', f'peak={np.max(np.abs(stereo)):.3f}')

if __name__=='__main__':
 render('CoastalWind','coast',.045)
 render('TundraWind','tundra',.033)
 render('IndoorWind','indoor',.012)
