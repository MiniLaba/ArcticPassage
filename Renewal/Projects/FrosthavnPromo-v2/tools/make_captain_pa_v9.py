# coding: utf-8
"""Cabin PA treatment, timed intelligible speech and restrained microphone static."""
from pathlib import Path
import json,subprocess,hashlib
import numpy as np,soundfile as sf
R=Path(__file__).resolve().parents[1];O=R/'voice/flight-v9';sr=48000;report=json.loads((R/'evidence/flight-voice-v9.json').read_text());items={c['id']:c for c in report['items']};D=199.7;N=round(D*sr)
def ff(args):subprocess.run(['ffmpeg','-y','-v','error']+list(map(str,args)),check=True)
# Welcome retains the same clean narrator timbre. Captain is a separate male preset.
ff(['-i',R/items['welcome']['file'],'-af','highpass=f=75,lowpass=f=10500,loudnorm=I=-18:TP=-3:LRA=7','-ar',sr,'-ac','2','-c:a','pcm_f32le',O/'welcome-clean.wav'])
ff(['-i',R/items['captain']['file'],'-af','highpass=f=250,lowpass=f=3600,acompressor=threshold=0.065:ratio=2.6:attack=8:release=110:makeup=1.6','-ar',sr,'-ac','1','-c:a','pcm_f32le',O/'captain-bandlimited.wav'])
a,_=sf.read(O/'captain-bandlimited.wav',dtype='float32');a=np.tanh(a*1.18)/1.18
# Short cabin reflections, without a long radio echo.
for delay,gain in [(round(.032*sr),.045),(round(.068*sr),.018)]:a[delay:]+=a[:-delay].copy()*gain
sf.write(O/'captain-speaker.wav',a,sr,subtype='FLOAT')
ff(['-i',O/'captain-speaker.wav','-af','loudnorm=I=-19:TP=-3:LRA=6','-ar',sr,'-ac','1','-c:a','pcm_f32le',O/'captain-pa-voice.wav'])
v,_=sf.read(O/'captain-pa-voice.wav',dtype='float32');pre=.18;post=.15;n=round(pre*sr)+len(v)+round(post*sr);speech=np.zeros(n,np.float32);speech[round(pre*sr):round(pre*sr)+len(v)]=v
# Stable seeded band-limited air/static; SNR is based on active speech, not silence.
rng=np.random.default_rng(27102909);noise=rng.normal(size=n).astype(np.float32);spec=np.fft.rfft(noise);freq=np.fft.rfftfreq(n,1/sr);weight=np.clip((freq-320)/350,0,1)*np.clip((6100-freq)/1300,0,1);noise=np.fft.irfft(spec*weight,n).astype(np.float32)
active=np.abs(v)>.025;vrms=float(np.sqrt(np.mean(v[active]**2)));nrms=vrms/10**(24/20);noise*=nrms/np.sqrt(np.mean(noise**2));x=np.arange(n)/sr;envelope=np.minimum(np.clip(x/.025,0,1),np.clip((n/sr-x)/.04,0,1));noise*=envelope
# Microphone switch fuzz at each end, rather than a notification chime.
for start,length,gain in [(0,.105,1.9),(n/sr-.13,.105,1.6)]:
 i=round(start*sr);m=min(round(length*sr),n-i);noise[i:i+m]+=rng.normal(size=m).astype(np.float32)*nrms*gain*np.sin(np.linspace(0,np.pi,m))**2
for pos in rng.uniform(.2,n/sr-.2,round(n/sr*1.8)):
 i=round(pos*sr);m=min(round(.004*sr),n-i);noise[i:i+m]+=rng.uniform(-1,1)*nrms*2*np.exp(-np.arange(m)/(sr*.0009))
noise=noise.astype(np.float32);combined=speech+noise;sf.write(O/'captain-static.wav',noise,sr,subtype='PCM_24');sf.write(O/'captain-broadcast.wav',combined,sr,subtype='PCM_24')
start=10.8;end=start+n/sr;assert end<27.7-2
# Preserve all later original narrator phrases at their exact previous timings.
normal,_=sf.read(R/'voice/Narration-master-v6.wav',dtype='float32',always_2d=True);normal=normal[:N].copy();normal[:round(37.9*sr)]=0
welcome,_=sf.read(O/'welcome-clean.wav',dtype='float32',always_2d=True);i=round(.3*sr);normal[i:i+len(welcome)]+=welcome
capt=np.zeros((N,2),np.float32);static=np.zeros_like(capt);i=round(start*sr);capt[i:i+n]=speech[:,None];static[i:i+n]=noise[:,None]
sf.write(R/'voice/Narration-master-v9.wav',normal+capt,sr,subtype='PCM_24');sf.write(R/'voice/Captain-static-v9.wav',static,sr,subtype='PCM_24');sf.write(R/'voice/Captain-voice-v9.wav',capt,sr,subtype='PCM_24')
t=json.loads((R/'voice/script/voice-timing-v6.json').read_text());old=t['cues'];w={'id':'vo-01','start':.3,'slotEnd':5.0,'en':items['welcome']['text'],'zh':'欢迎搭乘月月鸟航空，前往霜灯港。','position':'bottom','duration':len(welcome)/sr,'end':.3+len(welcome)/sr,'file':'voice/flight-v9/welcome-clean.wav','voice':'af_heart','subtitle':True,'fitsSlot':True}
c={'id':'captain-pa','start':start,'speechStart':start+pre,'slotEnd':26.0,'en':items['captain']['text'],'zh':'','position':'none','duration':n/sr,'end':end,'file':'voice/flight-v9/captain-broadcast.wav','voice':'am_michael','subtitle':False,'fitsSlot':end<26.0,'musicReductionDb':14}
t.update(voice='af_heart + am_michael (captain PA)',cues=[w,c]+old[3:]);(R/'voice/script/voice-timing-v9.json').write_text(json.dumps(t,ensure_ascii=False,indent=2))
pa={'voice':'am_michael','generationSpeed':items['captain']['speed'],'measuredDryWpm':items['captain']['wordsPerMinute'],'bandpassHz':[250,3600],'activeSpeechToStaticDb':24,'staticRmsDbFS':20*np.log10(float(np.sqrt(np.mean(noise**2)))),'start':start,'speechStart':start+pre,'end':end,'touchdown':27.7,'clearanceBeforeTouchdown':27.7-end,'subtitles':False,'seed':27102909,'subjectiveListeningVerified':False,'files':{str(f.relative_to(R)):hashlib.sha256(f.read_bytes()).hexdigest()for f in [O/'captain-broadcast.wav',O/'captain-static.wav',O/'welcome-clean.wav',R/'voice/Narration-master-v9.wav',R/'voice/Captain-static-v9.wav']}}
(R/'evidence/captain-pa-v9.json').write_text(json.dumps(pa,indent=2));print('Captain PA:',round(start,2),'to',round(end,3),'seconds; landing gap',round(27.7-end,3),flush=True)
ff(['-i',O/'captain-broadcast.wav','-c:a','libmp3lame','-q:a','2',O/'Captain-PA-preview.mp3'])
