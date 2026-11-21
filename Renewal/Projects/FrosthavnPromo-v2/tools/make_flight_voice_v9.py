# coding: utf-8
"""Two newly approved English phrases, same narrator plus separate captain preset."""
from pathlib import Path
import json,hashlib
import numpy as np,soundfile as sf,onnxruntime as ort
from kokoro_onnx import Kokoro
R=Path(__file__).resolve().parents[1];O=R/'voice/flight-v9';O.mkdir(exist_ok=True)
model=R/'voice/models/kokoro-v1.0.onnx';voices=R/'voice/models/voices-v1.0.bin';opt=ort.SessionOptions();opt.intra_op_num_threads=4;opt.inter_op_num_threads=1
k=Kokoro.from_session(ort.InferenceSession(str(model),sess_options=opt,providers=['CPUExecutionProvider']),str(voices))
items=[{'id':'welcome','voice':'af_heart','speed':.90,'text':'Welcome aboard this Moonbird Air flight to Frosthavn.'},{'id':'captain','voice':'am_michael','speed':1.18,'text':"Ladies and gentlemen, we're now on our final approach to Frosthavn. Please fasten your seat belts, return your seat backs to the upright position, and stow your tray tables. Cabin crew, please prepare for landing."}]
for c in items:
 f=O/(c['id']+'-dry.wav');
 if c['id']=='welcome'and f.exists():a,sr=sf.read(f,dtype='float32')
 else:a,sr=k.create(c['text'].replace('Frosthavn','Frost-havn'),voice=c['voice'],speed=c['speed'],lang='en-us')
 assert sr==24000;sf.write(f,a,sr,subtype='PCM_24');c.update(file=str(f.relative_to(R)),duration=len(a)/sr,sampleRate=sr,words=len(c['text'].split()),sha256=hashlib.sha256(f.read_bytes()).hexdigest());c['wordsPerMinute']=round(c['words']*60/c['duration'],1);print(c['id'],c['duration'],c['wordsPerMinute'],'wpm',flush=True)
(R/'evidence/flight-voice-v9.json').write_text(json.dumps({'engine':'Kokoro-82M local presets','synthetic':True,'modelSha256':hashlib.sha256(model.read_bytes()).hexdigest(),'cloning':False,'subjectiveListeningVerified':False,'items':items},indent=2))
