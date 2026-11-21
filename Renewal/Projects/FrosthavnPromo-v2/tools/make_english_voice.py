"""Local open-model narration; keep actual per-phrase audio and timings."""
from pathlib import Path
import json,hashlib,time,sys
import numpy as np
import soundfile as sf
import onnxruntime as ort
from kokoro_onnx import Kokoro
R=Path(__file__).resolve().parents[1];P=json.loads((R/'voice/script/story-v4.json').read_text());model=R/'voice/models/kokoro-v1.0.onnx';voices=R/'voice/models/voices-v1.0.bin';opts=ort.SessionOptions();opts.intra_op_num_threads=4;opts.inter_op_num_threads=1
session=ort.InferenceSession(str(model),sess_options=opts,providers=['CPUExecutionProvider']);k=Kokoro.from_session(session,str(voices));out=R/'voice/segments-final';out.mkdir(exist_ok=True);voice=P['voice'];sr=24000;mix=np.zeros(round(P['duration']*sr),np.float32);report=[]
for c in P['cues']:
 f=out/(c['id']+'.wav')
 if f.exists():samples,rate=sf.read(f,dtype='float32')
 else:
  text=c['en'].replace('Frosthavn','Frost-havn').replace('Stardew','Star dew')
  samples,rate=k.create(text,voice=voice,speed=P['speed'],lang='en-us');sf.write(f,samples,rate,subtype='PCM_24')
 assert rate==sr
 duration=len(samples)/sr
 # Measure only; do not silently stretch the voice into a slot.
 c={**c,'duration':duration,'end':round(c['start']+duration,4),'file':str(f.relative_to(R)),'fitsSlot':duration<=c['slotEnd']-c['start']+.05}
 i=round(c['start']*sr);n=min(len(samples),len(mix)-i);mix[i:i+n]+=samples[:n];report.append(c);print(c['id'],round(duration,2),'slot',round(c['slotEnd']-c['start'],2),c['fitsSlot'],flush=True)
sf.write(R/'voice/EnglishNarration-166s.wav',mix,sr,subtype='PCM_24');(R/'voice/script/voice-timing.json').write_text(json.dumps({'voice':voice,'engine':'Kokoro-82M / kokoro-onnx','synthetic':True,'modelSha256':hashlib.sha256(model.read_bytes()).hexdigest(),'cues':report,'subjectiveListeningVerified':False},ensure_ascii=False,indent=2));print('Voice stem complete',flush=True)
