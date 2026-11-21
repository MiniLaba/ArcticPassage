# coding: utf-8
from pathlib import Path
import json,numpy as np,soundfile as sf
R=Path(__file__).resolve().parents[1];T=json.loads((R/'voice/script/voice-timing-v6.json').read_text());sr=24000;a=np.zeros(round(T['duration']*sr),np.float32)
for c in T['cues']:
 v,r=sf.read(R/c['file'],dtype='float32');assert r==sr
 i=round(c['start']*sr);a[i:i+len(v)]+=v
sf.write(R/'voice/EnglishNarration-v6.wav',a,sr,subtype='PCM_24')
print('24 cached narration segments retimed without stretching')
