"""Actual voice-aware music automation with separate, inspectable stems."""
from pathlib import Path
import subprocess,json,hashlib
import numpy as np
import soundfile as sf
R=Path(__file__).resolve().parents[1];P=json.loads((R/'voice/script/story-v4.json').read_text());T=json.loads((R/'voice/script/voice-timing.json').read_text());sr=48000;D=P['duration'];N=round(D*sr)
def ff(a):return subprocess.run(['ffmpeg','-y','-hide_banner','-loglevel','error']+list(map(str,a)),check=True)
def prep(file,out,extra=[]):
 ff(extra+['-i',R/file,'-t',D,'-ar',sr,'-ac','2','-c:a','pcm_f32le',R/out]);a,_=sf.read(R/out,dtype='float32',always_2d=True);b=np.zeros((N,2),np.float32);b[:min(N,len(a))]=a[:N];return b
music=prep('raw/music/LifeInSilico-ScottBuckley.mp3','voice/Music-source.wav',['-ss','10'])*.75
ff(['-i',R/'voice/EnglishNarration-166s.wav','-af','highpass=f=75,lowpass=f=10500,loudnorm=I=-18:TP=-3:LRA=7','-ar',sr,'-ac','2','-c:a','pcm_f32le',R/'voice/Narration-master.wav']);voice,_=sf.read(R/'voice/Narration-master.wav',dtype='float32',always_2d=True)
paper=prep('public/paper-fold-sfx.wav','voice/Paper-source.wav')*.9
atmo=prep('voice/DirectorAtmosphere.wav','voice/Air-source.wav');env=np.ones(N,np.float32)
for c in T['cues']:
 a=max(0,round((c['start']-.22)*sr));b=min(N,round((c['end']+.65)*sr));idx=np.arange(a,b)/sr
 ramp=np.minimum(np.clip((idx-(c['start']-.22))/.22,0,1),np.clip(((c['end']+.65)-idx)/.65,0,1));env[a:b]=np.minimum(env[a:b],1-ramp*.70)
fade=np.minimum(np.clip(np.arange(N)/sr/.4,0,1),np.clip((D-np.arange(N)/sr)/3.2,0,1));music*= (env*fade)[:,None];sf.write(R/'voice/Music-ducked.wav',music,sr,subtype='PCM_24');sf.write(R/'voice/Independent-SFX.wav',paper+atmo,sr,subtype='PCM_24');mix=music+paper+atmo+voice[:N];sf.write(R/'voice/Director-raw-mix.wav',mix,sr,subtype='PCM_24')
m=subprocess.run(['ffmpeg','-hide_banner','-i',str(R/'voice/Director-raw-mix.wav'),'-af','loudnorm=I=-16:TP=-1.5:LRA=9:print_format=json','-f','null','-'],capture_output=True,text=True,check=True);x=json.JSONDecoder().raw_decode(m.stderr[m.stderr.rfind('{'):])[0]
f=f'loudnorm=I=-16:TP=-1.5:LRA=9:measured_I={x["input_i"]}:measured_TP={x["input_tp"]}:measured_LRA={x["input_lra"]}:measured_thresh={x["input_thresh"]}:offset={x["target_offset"]}:linear=true'
ff(['-i',R/'voice/Director-raw-mix.wav','-af',f,'-ar',sr,'-c:a','pcm_s24le',R/'voice/Director-master.wav'])
def digest(file):return hashlib.sha256((R/file).read_bytes()).hexdigest()
report={'duration':D,'syntheticVoice':'Kokoro-82M af_heart, local preset, no voice cloning','musicDuckingDb':-10.46,'attackSeconds':.22,'releaseSeconds':.65,'voiceTargetLUFS':-18,'mixTargetLUFS':-16,'subjectiveListeningVerified':False,'measurement':x,'assets':[{'file':f,'sha256':digest(f)}for f in ['voice/Director-master.wav','voice/Narration-master.wav','voice/Music-ducked.wav','voice/Independent-SFX.wav']]};(R/'evidence/director-audio-mix.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print('Narration + ducked music + independent SFX ready',flush=True)
