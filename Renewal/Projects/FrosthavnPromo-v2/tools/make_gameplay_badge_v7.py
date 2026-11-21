# coding: utf-8
"""Original vector-like lighthouse hallmark, supersampled, native-footage ranges only."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,subprocess,math
R=Path(__file__).resolve().parents[1];E=R/'evidence';W,H=284,78;S=4
im=Image.new('RGBA',(W*S,H*S));d=ImageDraw.Draw(im)
def line(pts,fill,width=1):d.line([(round(x*S),round(y*S))for x,y in pts],fill=fill,width=round(width*S),joint='curve')
def ellipse(b,fill=None,outline=None,width=1):d.ellipse(tuple(round(v*S)for v in b),fill=fill,outline=outline,width=round(width*S))
navy=(12,36,47,211);ivory=(239,243,234,255);gold=(204,175,117,255);dim=(182,204,207,255)
d.rounded_rectangle((S, S,283*S,77*S),radius=13*S,fill=navy,outline=(207,224,221,85),width=S)
# Lighthouse seal: a tapering tower, lantern, horizon and single polar glint.
ellipse((13,14,62,63),outline=(205,180,126,120),width=.8)
line([(19,53),(29,53),(32,49),(43,49),(46,53),(57,53)],dim,.9)
d.polygon([(32*S,48*S),(35*S,31*S),(41*S,31*S),(44*S,48*S)],fill=ivory)
line([(33,31),(43,31)],gold,1.2);line([(34,30),(34,25),(42,25),(42,30)],ivory,1)
d.polygon([(32*S,24*S),(38*S,20*S),(44*S,24*S)],fill=gold)
line([(25,29),(18,31)],gold,.9);line([(49,29),(56,31)],gold,.9)
line([(38,35),(38,45)],(44,78,90,255),1.5)
line([(57,16),(57,22)],gold,.9);line([(54,19),(60,19)],gold,.9)
line([(73,18),(91,18)],gold,1)
zh=ImageFont.truetype('/System/Library/Fonts/STHeiti Medium.ttc',26*S)
en=ImageFont.truetype('/System/Library/Fonts/Supplemental/Avenir Next.ttc',12*S)
d.text((74*S,17*S),'实机画面',font=zh,fill=ivory)
x=75*S
for c in 'NATIVE GAMEPLAY':
 d.text((x,51*S),c,font=en,fill=dim);x+=d.textlength(c,font=en)+.8*S
im=im.resize((W,H),Image.Resampling.LANCZOS);im.save(R/'public/gameplay-badge-v7.png')
p=json.loads((R/'voice/script/story-v6.json').read_text());ranges=[]
# Stable groups: fade off before CG begins, reveal after native takes visual ownership.
for s in p['shots']:
 if s['type']!='native':continue
 start=s['start']+s.get('overlap',0)/2;end=s['end'];anchor='center'if s['id']in ['snow-lesson','research']else'bottom'if s['id']=='market'else'left'
 nxt=next((v for v in p['shots']if v['start']>s['start']),None)
 if nxt and nxt['type']=='cg':end=nxt['start']
 if ranges and ranges[-1]['anchor']==anchor and abs(start-ranges[-1]['end'])<.001:ranges[-1]['end']=end;ranges[-1]['shots'].append(s['id'])
 else:ranges.append({'start':start,'end':end,'anchor':anchor,'shots':[s['id']]})
# No extra fading when position changes at an ordinary hard cut.
for i,r in enumerate(ranges):
 r['fadeIn']=0 if i and abs(r['start']-ranges[i-1]['end'])<.001 else .20
 r['fadeOut']=0 if i+1<len(ranges)and abs(r['end']-ranges[i+1]['start'])<.001 else .18
 r['x'],r['y']=(818,32)if r['anchor']=='center'else(48,944)if r['anchor']=='bottom'else(48,40)
report={'badge':'public/gameplay-badge-v7.png','video':'renders/gameplay-badge-v7.mov','size':[W,H],'duration':p['duration'],'ranges':ranges,'source':'original code drawing; no stock logo or generated image'}
(E/'gameplay-badge-v7.json').write_text(json.dumps(report,indent=2))
cmd=['ffmpeg','-y','-v','error','-f','rawvideo','-pixel_format','rgba','-video_size',f'{W}x{H}','-framerate','30','-i','-','-an','-c:v','qtrle','-pix_fmt','argb',str(R/'renders/gameplay-badge-v7.mov')]
proc=subprocess.Popen(cmd,stdin=subprocess.PIPE);empty=bytes(W*H*4);cache={0:empty}
for k in range(round(p['duration']*30)):
 t=k/30;r=next((r for r in ranges if r['start']<=t<r['end']),None);alpha=0
 if r:
  a=1 if not r['fadeIn'] else min(1,(t-r['start'])/r['fadeIn']);b=1 if not r['fadeOut']else min(1,(r['end']-t)/r['fadeOut']);q=min(a,b);alpha=round(255*q*q*(3-2*q))
 if alpha not in cache:
  out=im.copy();out.putalpha(im.getchannel('A').point(lambda a:round(a*alpha/255)));cache[alpha]=out.tobytes()
 proc.stdin.write(cache[alpha])
proc.stdin.close();assert proc.wait()==0
print('Authored hallmark and alpha movie ready;',len(ranges),'native intervals')
