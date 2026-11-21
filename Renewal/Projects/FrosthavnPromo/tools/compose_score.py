"""60-second original Frosthavn promo arrangement. No third-party music recording.
The shared site-theme motif is reharmonized/arranged to the shot boundaries.
GeneralUser GS is used only for rendering, never bundled.
"""
from pathlib import Path
import argparse,json,struct,subprocess,tempfile,wave
import numpy as np
R=Path(__file__).resolve().parents[1];SR=48000;PPQ=480;BPM=72;BEAT=60/BPM
def vlq(n):
 out=[n&127]
 while n>>7:n>>=7;out.insert(0,(n&127)|128)
 return bytes(out)
def make_midi(p,plan):
 events=[(0,b'\xff\x51\x03'+int(60000000/BPM).to_bytes(3,'big'))]
 for ch,prog in enumerate([0,48,8,24,42]):
  events.extend([(0,bytes([0xc0|ch,prog])),(0,bytes([0xb0|ch,10,[56,74,82,43,67][ch]])),(0,bytes([0xb0|ch,91,60]))])
 def note(ch,sec,length,pitch,vel):
  tick=round(sec/BEAT*PPQ);end=round((sec+length)/BEAT*PPQ)
  events.extend([(tick,bytes([0x90|ch,pitch,vel])),(end,bytes([0x80|ch,pitch,0]))])
 chords=[[47,54,59,61],[43,50,54,59],[50,57,61,66],[45,52,57,64],[40,47,54,59],[43,50,54,59],[50,57,61,66],[45,52,57,64]]
 phrases=[[(.5,2.1,66)],[(0,1.35,69),(2.6,.9,73)],[(.5,2,71)],[(0,1.25,69),(2.1,1.3,66)],[(.5,2.3,64)],[(0,1.4,66),(2.6,.9,69)],[(.5,2.1,66)],[(0,2.7,62)]]
 for bar in range(17):
  at=bar*4*BEAT;chord=chords[(bar//2)%8];warm=at>=plan['shots'][2]['start'];people=33<=at<41
  for off,length,pitch in phrases[bar%8]:
   if at+off*BEAT>54:continue
   note(0,at+off*BEAT,length*BEAT,pitch,48 if warm else 42)
  note(4,at,3.8*BEAT,chord[0]-12,23 if warm else 18)
  if bar%2==0:
   for j,pitch in enumerate(chord[1:]):note(1,at+.07*j,7.6*BEAT,pitch,28 if warm else 19)
  if warm and at<52:
   for k,pitch in enumerate([chord[1],chord[2]+12,chord[3],chord[2]]):note(3,at+(.13+k*.88)*BEAT,1.6*BEAT,pitch,33 if people else 29)
  if bar%4==2 and at<50:note(2,at+2*BEAT,1.6*BEAT,chord[-1]+12,24)
 # Final D chord is composed at the final title, followed by natural tail.
 for j,pitch in enumerate([50,57,62,66]):
  note(0,56.1+j*.055,2.3,pitch,37 if j else 43);note(1,56.1+j*.06,2.5,pitch,24)
 note(2,56.4,1.8,74,22);note(4,56.1,2.5,38,21)
 events.append((round(60/BEAT*PPQ),b'\xff\x2f\x00'));events.sort(key=lambda x:(x[0],0 if x[1][0]&0xf0==0x80 else 1))
 track=bytearray();prev=0
 for t,e in events:track.extend(vlq(t-prev));track.extend(e);prev=t
 p.write_bytes(b'MThd'+struct.pack('>IHHH',6,0,1,PPQ)+b'MTrk'+struct.pack('>I',len(track))+track)
def wav(p,sound):
 sound=np.asarray(sound)
 if sound.ndim==1:sound=np.stack([sound*.97,sound],axis=1)
 sound=np.clip(sound,-.92,.92)
 with wave.open(str(p),'wb') as f:f.setnchannels(2);f.setsampwidth(2);f.setframerate(SR);f.writeframes((sound*32767).astype('<i2').tobytes())
def sfx():
 rng=np.random.default_rng(1028);out=R/'assets/sfx';out.mkdir(parents=True,exist_ok=True)
 for name,dur in [('water',.65),('snow',1.2),('wood',.25),('paper',.55),('chime',.9),('softbell',.65),('resolve',2.5)]:
  t=np.arange(round(dur*SR))/SR;env=np.minimum(1,t/.009)*np.maximum(0,1-t/dur)**1.5
  noise=rng.normal(0,1,len(t));low=np.convolve(noise,np.ones(24)/24,mode='same')
  if name=='water':x=(.22*np.sin(2*np.pi*(430*t-220*t*t))*np.exp(-t*12)+.19*low)*env
  elif name=='snow':x=.28*low*env*(.65+.35*np.sin(t*18)**2)
  elif name=='wood':x=(.18*np.sin(2*np.pi*170*t)+.08*np.sin(2*np.pi*337*t)+.1*low)*np.exp(-t*24)*env
  elif name=='paper':x=.20*low*env*(np.sin(np.pi*t/dur)**2)
  else:
   notes=[587.33,880] if name=='chime' else [739.99] if name=='softbell' else [293.66,440,587.33,739.99]
   x=np.zeros_like(t)
   for i,hz in enumerate(notes):
    tt=t-i*.07;gate=(tt>=0);tt=np.maximum(0,tt);x+=.065*np.sin(2*np.pi*hz*tt)*np.exp(-tt*3.7)*np.minimum(1,tt/.007)*gate
   x*=env
  wav(out/(name+'.wav'),x)
 # Existing, clearly sourced mod engine audio. Finite duration and fades.
 src=R/'assets/source/propeller.wav'
 subprocess.run(['ffmpeg','-v','error','-y','-stream_loop','-1','-i',str(src),'-t','6','-af','volume=0.50,lowpass=f=4500,afade=t=in:d=0.2,afade=t=out:st=4.8:d=1.2','-ar',str(SR),'-ac','2',str(out/'engine.wav')],check=True)
def main():
 a=argparse.ArgumentParser();a.add_argument('--soundfont',type=Path,required=True);args=a.parse_args();plan=json.loads((R/'plan.json').read_text())
 (R/'assets').mkdir(exist_ok=True);m=R/'assets/frosthavn-north.mid';make_midi(m,plan)
 with tempfile.TemporaryDirectory() as d:
  raw=Path(d)/'raw.wav'
  subprocess.run(['fluidsynth','-ni','-q','-R','yes','-C','no','-o','synth.reverb.room-size=0.65','-o','synth.reverb.damp=0.58','-o','synth.reverb.level=0.30','-r',str(SR),'-F',str(raw),'-T','wav',str(args.soundfont.resolve()),str(m)],check=True)
  subprocess.run(['ffmpeg','-v','error','-y','-i',str(raw),'-t','60','-af','highpass=f=42,lowpass=f=10000,afade=t=in:d=0.8,afade=t=out:st=58.4:d=1.6','-ar',str(SR),'-ac','2','-c:a','pcm_s24le',str(R/'assets/music.wav')],check=True)
 # Match the quiet MIDI rendering to a useful music bed before SFX mixing.
 # A master limiter alone would otherwise make transient SFX dominate the score.
 pcm=subprocess.check_output(['ffmpeg','-v','error','-i',str(R/'assets/music.wav'),'-f','f32le','-'])
 samples=np.frombuffer(pcm,dtype='<f4');rms=float(np.sqrt(np.mean(samples*samples)));peak=float(np.max(np.abs(samples)))
 gain=min(.04/max(rms,1e-8),.58/max(peak,1e-8))
 with tempfile.TemporaryDirectory() as d:
  normalized=Path(d)/'music.wav'
  subprocess.run(['ffmpeg','-v','error','-y','-i',str(R/'assets/music.wav'),'-af',f'volume={gain:.9f}','-c:a','pcm_s24le',str(normalized)],check=True)
  (R/'assets/music.wav').write_bytes(normalized.read_bytes())
 sfx()
 record=dict(music=dict(source='code-original',file='assets/music.wav',script='tools/compose_score.py',motif='Original Frosthavn website theme by the same project; newly arranged to the film.',bpm=BPM,key='B minor, D major resolution',duration=60,renderer='FluidSynth / GeneralUser GS 2.0.3',sections=[dict(start=s['start'],end=s['end'],shot=s['id']) for s in plan['shots']]),sfx=[dict(file=str(p.relative_to(R)),source='Native mod synthesized engine audio, MIT project' if p.stem=='engine' else 'Original deterministic waveform/noise synthesis for this film',license='Frosthavn project MIT',recording=False) for p in (R/'assets/sfx').glob('*.wav')],selection='Existing clearly sourced project music motif and native propeller were preferred. Other sounds authored specifically for snow, water, wood, paper and warm chimes; no external SFX recording is used or claimed.',listeningStatus='Not subjectively auditioned by this script.')
 (R/'evidence/audio-selection.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
 print('Composed 60-second score and eight independent action sound files.')
if __name__=='__main__':main()
