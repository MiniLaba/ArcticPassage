"""Original aligned website score: cold fjord / warm harbour arrangements.
Same pulse, harmony, melody and loop length; no random notes or drums.
Render using the separately installed GeneralUser GS soundfont.
"""
from pathlib import Path
import argparse,struct,subprocess,tempfile,json,wave
import numpy as np
R=Path(__file__).resolve().parents[1]; PPQ=480; BPM=68; BEATS=4; BARS=32
SECONDS=BARS*BEATS*60/BPM
CHORDS=[[47,54,59,61],[43,50,54,59],[50,57,61,64],[45,52,57,62],
        [40,47,54,59],[43,50,54,59],[50,57,61,66],[45,52,57,64]]
PHRASES=[[(.5,2.5,66)],[(0,1.5,69),(2.5,1,73)],[(.5,2,71)],[(0,1.5,69),(2,1.5,66)],
         [(.5,2.5,64)],[(0,1.5,66),(2.5,1,69)],[(.5,2.5,66)],[(0,2,62)]]
def vlq(n):
 out=[n&127]
 while n>>7:n>>=7;out.insert(0,(n&127)|128)
 return bytes(out)
def midi(p,warm):
 events=[(0,b'\xff\x51\x03'+int(60000000/BPM).to_bytes(3,'big'))]
 for ch,program in enumerate([0,48,8,24,42]):
  events.extend([(0,bytes([0xc0|ch,program])),(0,bytes([0xb0|ch,10,[58,76,83,42,64][ch]])),(0,bytes([0xb0|ch,91,56]))])
 def note(ch,beat,length,pitch,vel):
  at=round(beat*PPQ);events.extend([(at,bytes([0x90|ch,pitch,vel])),(at+round(length*PPQ),bytes([0x80|ch,pitch,0]))])
 for bar in range(BARS*3):
  i=bar%BARS;at=bar*BEATS;chord=CHORDS[(i//2)%len(CHORDS)]
  # Unchanged, sparse piano motif makes both arrangements one composition.
  phrase=PHRASES[i%8]
  if i in [0,7,15,23,31]:phrase=phrase[:1]
  for offset,length,pitch in phrase:note(0,at+offset,length*.92,pitch,43 if i<16 else 46)
  if i%2==0:
   note(4,at,BEATS*1.92,chord[0]-12,23 if not warm else 27)
   for j,pitch in enumerate(chord[1:]):note(1,at+.08*j,BEATS*1.94,pitch,22 if not warm else 25)
  if i%8 in [2,6]:note(2,at+2,1.65,chord[-1]+12,23 if not warm else 18)
  if warm:
   # Timber warmth after landing: quiet nylon-string detail, no added beat.
   for k,pitch in enumerate([chord[1],chord[2]+12,chord[3],chord[2]]):note(3,at+.15+k*.85,2.1,pitch,30+[0,3,1,-2][k])
  elif i%4==0:note(2,at+.2,2.9,chord[1]+12,16)
 events.append((max(t for t,_ in events)+PPQ,b'\xff\x2f\x00'))
 events.sort(key=lambda e:(e[0],0 if e[1][0]&0xf0==0x80 else 1,e[1]));track=bytearray();prev=0
 for tick,event in events:track.extend(vlq(tick-prev));track.extend(event);prev=tick
 p.write_bytes(b'MThd'+struct.pack('>IHHH',6,0,1,PPQ)+b'MTrk'+struct.pack('>I',len(track))+track)
def run():
 ap=argparse.ArgumentParser();ap.add_argument('--soundfont',type=Path,required=True);a=ap.parse_args()
 source=R/'art/music';source.mkdir(parents=True,exist_ok=True);out=R/'public/assets/music';out.mkdir(parents=True,exist_ok=True)
 with tempfile.TemporaryDirectory(prefix='frosthavn-score-') as tmp:
  tmp=Path(tmp);loops=[]
  for name,warm in [('ice-letter',False),('harbour-light',True)]:
   m=source/(name+'.mid');midi(m,warm);raw=tmp/(name+'-raw.wav');loop=tmp/(name+'.wav')
   subprocess.run(['fluidsynth','-ni','-q','-R','yes','-C','no','-o','synth.reverb.room-size=0.55','-o','synth.reverb.damp=0.62','-o','synth.reverb.level=0.27','-r','44100','-F',str(raw),'-T','wav',str(a.soundfont.resolve()),str(m)],check=True)
   subprocess.run(['ffmpeg','-v','error','-y','-ss',str(SECONDS),'-i',str(raw),'-t',str(SECONDS),'-ar','44100','-ac','2','-c:a','pcm_s16le',str(loop)],check=True)
   with wave.open(str(loop)) as f:audio=np.frombuffer(f.readframes(f.getnframes()),dtype='<i2').astype(np.float64)/32768
   loops.append((name,loop,float(np.sqrt(np.mean(audio**2))),float(np.abs(audio).max())))
  rms=max(v[2] for v in loops);peak=max(v[3] for v in loops);gain=min(.058/max(rms,1e-8),.62/max(peak,1e-8))
  report={'title':'冰海来信 / A Letter from the Ice','warmArrangement':'霜灯归港 / Harbour Light','bpm':BPM,'bars':BARS,'meter':'4/4','loopSeconds':SECONDS,'sharedGain':gain,'notes':'One authored melody in two synchronized arrangements. Mastered with shared gain so the motif stays balanced through the landing crossfade. Original MIDI; GeneralUser GS rendered instruments.','files':{}}
  for name,loop,rms,peak in loops:
   dest=out/(name+'.mp3');subprocess.run(['ffmpeg','-v','error','-y','-i',str(loop),'-af',f'volume={gain:.9f},highpass=f=38,lowpass=f=9400,afade=t=in:st=0:d=0.04,afade=t=out:st={SECONDS-.06:.9f}:d=0.06','-c:a','libmp3lame','-b:a','128k','-ar','44100',str(dest)],check=True)
   # Decode the distributed asset to check duration, peak and both loop edges.
   pcm=tmp/(name+'-decoded.wav');subprocess.run(['ffmpeg','-v','error','-y','-i',str(dest),'-c:a','pcm_s16le',str(pcm)],check=True)
   with wave.open(str(pcm)) as f:
    channels=f.getnchannels();rate=f.getframerate();samples=np.frombuffer(f.readframes(f.getnframes()),dtype='<i2').reshape(-1,channels).astype(float)/32768
   seam=float(np.max(np.abs(samples[0]-samples[-1])))
   report['files'][dest.name]={'bytes':dest.stat().st_size,'seconds':len(samples)/rate,'rms':float(np.sqrt(np.mean(samples**2))),'peak':float(np.abs(samples).max()),'loopBoundaryDifference':seam}
   assert abs(len(samples)/rate-SECONDS)<.06 and np.abs(samples).max()<.8 and seam<.001
  (source/'website-score.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
  print(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=='__main__':run()
