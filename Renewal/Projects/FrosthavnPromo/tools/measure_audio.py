from pathlib import Path
import json,subprocess,numpy as np
r=Path(__file__).resolve().parents[1];plan=json.loads((r/'plan.json').read_text());mix=json.loads((r/'evidence/audio-mix.json').read_text())
def raw(name):return np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',str(r/name),'-f','f32le','-ar','48000','-ac','2','-']),dtype='<f4').reshape(-1,2)
m=raw('assets/master.wav');s=raw('assets/sfx-stem.wav');b=raw('assets/music-ducked.wav');rows=[]
for c in plan['audio']['cues']:
 a=int((c['at']+c['syncOffset'])*48000);z=min(a+14400,len(s));sp=float(np.max(np.abs(s[a:z])));bp=float(np.max(np.abs(b[a:z])))
 rows.append(dict(action=c['actionId'],at=c['at']+c['syncOffset'],sfxPeak=sp,musicPeak=bp,sfxMinusMusicDb=round(20*np.log10(max(sp,1e-8)/max(bp,1e-8)),2)))
per=[]
for sec in range(60):
 x=m[sec*48000:(sec+1)*48000];per.append(dict(second=sec,rms=float(np.sqrt(np.mean(x*x))),peak=float(np.max(np.abs(x)))))
report=dict(duration=len(m)/48000,peak=float(np.max(np.abs(m))),normalization=mix['normalization']['output'],cueWindows=rows,perSecond=per,listening='Numerical review only; not subjective listening.')
(r/'evidence/audio-measurements.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='perSecond'},indent=2))
