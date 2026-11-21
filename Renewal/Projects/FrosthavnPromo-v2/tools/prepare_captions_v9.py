# coding: utf-8
from pathlib import Path
import json
from PIL import Image,ImageDraw,ImageFont,ImageFilter
R=Path(__file__).resolve().parents[1];T=json.loads((R/'voice/script/voice-timing-v9.json').read_text());old=json.loads((R/'voice/script/captions-v7.json').read_text());c=T['cues'][0];out=R/'voice/captions-v9';out.mkdir(exist_ok=True)
font=ImageFont.truetype('/System/Library/Fonts/STHeiti Medium.ttc',40);im=Image.new('RGBA',(1800,144));shadow=Image.new('RGBA',im.size);d=ImageDraw.Draw(im);sd=ImageDraw.Draw(shadow);text=c['zh'];sd.text((901,48),text,font=font,anchor='ma',fill=(0,0,0,230),stroke_width=3,stroke_fill=(0,0,0,150));d.text((900,45),text,font=font,anchor='ma',fill=(250,247,236,255),stroke_width=2,stroke_fill=(13,29,40,235));shadow=shadow.filter(ImageFilter.GaussianBlur(3));shadow.alpha_composite(im);f=out/'vo-01.png';shadow.save(f)
first={**c,'displayEnd':c['end']+.35,'lines':[text],'png':str(f.relative_to(R)),'overlayX':60,'overlayY':936};caps=[first]+[c for c in old if c['id']not in ['vo-01','vo-02','vo-03']]
assert not any(c['start']<24.41 and c['displayEnd']>10.8 for c in caps)
(R/'voice/script/captions-v9.json').write_text(json.dumps(caps,ensure_ascii=False,indent=2))
def stamp(t):
 ms=round(t*1000);return f'{ms//3600000:02d}:{ms//60000%60:02d}:{ms//1000%60:02d},{ms%1000:03d}'
for lang,key in [('zh-CN','zh'),('en','en')]:
 s='\n'.join(f'{i+1}\n{stamp(c["start"])} --> {stamp(c["displayEnd"])}\n{c[key]}\n'for i,c in enumerate(caps));(R/f'voice/Frosthavn-v9.{lang}.srt').write_text(s,encoding='utf-8-sig')
p=json.loads((R/'voice/script/story-v8.json').read_text());p.update(edition='V9 / Welcome aboard and captain cabin PA',voice='af_heart + am_michael',voiceType='synthetic English narrator and separate male captain cabin PA',status='Approved aviation welcome and fast calm male captain announcement with microphone/static texture; no subtitles during PA.',cues=T['cues'],cueTimingSource='voice/script/voice-timing-v9.json')
for s in p['shots']:
 if s['id']=='window':s['file']='renders/mg-v9/window.mp4'
(R/'voice/script/story-v9.json').write_text(json.dumps(p,ensure_ascii=False,indent=2));print(len(caps),'subtitle cues; captain broadcast omitted from both hard captions and SRT')
