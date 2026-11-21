# coding: utf-8
from pathlib import Path
import json,re
from PIL import Image,ImageFont,ImageDraw,ImageFilter
R=Path(__file__).resolve().parents[1];t=json.loads((R/'voice/script/voice-timing-v6.json').read_text());out=R/'voice/captions-v6';out.mkdir(exist_ok=True);font=ImageFont.truetype('/System/Library/Fonts/STHeiti Medium.ttc',40);small=ImageFont.truetype('/System/Library/Fonts/STHeiti Medium.ttc',36);rows=[]
def stamp(x):
 ms=round(x*1000);return f'{ms//3600000:02d}:{ms//60000%60:02d}:{ms//1000%60:02d},{ms%1000:03d}'
def wrap(text,n):
 if len(text)<=n:return[text]
 candidates=[i+1 for i,c in enumerate(text)if c in '，。、；' and 5<i and i+1<=n and i+1<len(text)]
 at=candidates[-1]if candidates else n
 return [v for v in [text[:at],text[at:]] if v]
srtzh=[];srten=[]
for i,c in enumerate(t['cues']):
 end=min(c['slotEnd'],max(c['end']+.28,c['start']+1.8));lines=wrap(c['zh'],18 if c['position']=='top' else 22)
 fnt=small if c['position']=='top' else font
 img=Image.new('RGBA',(1800,144));shadow=Image.new('RGBA',img.size);sd=ImageDraw.Draw(shadow);d=ImageDraw.Draw(img);top=72-len(lines)*27
 for j,line in enumerate(lines):
  anchor='ra'if c['position']=='top'else'ma';x=1680 if c['position']=='top'else 900;y=top+j*54
  sd.text((x+1,y+3),line,font=fnt,anchor=anchor,fill=(0,0,0,230),stroke_width=3,stroke_fill=(0,0,0,150))
  d.text((x,y),line,font=fnt,anchor=anchor,fill=(250,247,236,255),stroke_width=2,stroke_fill=(13,29,40,235))
 shadow=shadow.filter(ImageFilter.GaussianBlur(3));shadow.alpha_composite(img);f=out/(c['id']+'.png');shadow.save(f)
 srtzh.append(f'{i+1}\n{stamp(c["start"])} --> {stamp(end)}\n'+ '\n'.join(lines)+'\n');srten.append(f'{i+1}\n{stamp(c["start"])} --> {stamp(end)}\n{c["en"]}\n')
 rows.append({**c,'displayEnd':end,'lines':lines,'png':str(f.relative_to(R)),'overlayX':60,'overlayY':28 if c['position']=='top'else 936})
(R/'voice/Frosthavn-v6.zh-CN.srt').write_text('\n'.join(srtzh),encoding='utf-8-sig');(R/'voice/Frosthavn-v6.en.srt').write_text('\n'.join(srten),encoding='utf-8-sig');(R/'voice/script/captions-v6.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2));print('24 bilingual subtitle cues and readable caption layers')
