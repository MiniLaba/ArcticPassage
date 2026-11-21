"""Original print art for the physical CG paper; no game stills or generated images."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import random, math

ROOT=Path(__file__).resolve().parents[1]
W,H=3600,1464
im=Image.new('RGB',(W,H),'#f1ecdf');d=ImageDraw.Draw(im)
INK='#163642';MUTED='#6b8185';ORANGE='#d57e48';WHITE='#f1ecdf'
FONT='/System/Library/Fonts/Supplemental/Arial.ttf'
BOLD='/System/Library/Fonts/Supplemental/Arial Bold.ttf'
ZH='/System/Library/Fonts/STHeiti Medium.ttc'
def text(x,y,s,size=40,c=INK,bold=False,zh=False):
 d.text((x,y),s,font=ImageFont.truetype(ZH if zh else BOLD if bold else FONT,size),fill=c)
def spaced(x,y,s,size,gap,c=INK):
 font=ImageFont.truetype(FONT,size)
 for ch in s:
  d.text((x,y),ch,font=font,fill=c);x+=d.textlength(ch,font=font)+gap

# Very light contour engraving, drawn from seeded curves, not geographic data.
for j in range(22):
 pts=[]
 for k in range(550):
  x=1800+k*3.1;y=170+j*37+58*math.sin(k*.012+j*.16)+20*math.sin(k*.037+j*.4)
  if x<3500:pts.append((x,y))
 d.line(pts,fill='#d9dfd7',width=2)
d.rectangle((0,0,W,25),fill=ORANGE)
d.rectangle((120,1270,3470,1275),fill=INK)
spaced(130,105,'MOONBIRD AIR',44,8)
text(130,175,'月月鸟航空',48,zh=True)
spaced(130,350,'NEXT STOP',36,9,MUTED)
text(115,420,'霜灯港',176,zh=True)
spaced(130,655,'FROSTHAVN',83,10)
text(140,900,'CAN',140,bold=True)
text(1600,900,'FHV',140,bold=True)
d.arc((510,760,1520,1110),192,348,fill=ORANGE,width=10)
d.ellipse((510,969,534,993),fill=ORANGE)
d.polygon([(1506,981),(1464,954),(1471,982),(1453,1011)],fill=ORANGE)
spaced(130,1160,'BOARDING PASS',36,7,MUTED)
text(1785,1160,'MM027',50,bold=True)
text(130,1320,'一张机票，把日常送到北极。',50,zh=True)

# Two different side-by-side stubs echo the actual print design family.
for x in [2700,3150]:d.line((x,70,x,1390),fill='#8a9b97',width=2)
d.rectangle((2730,70,3120,1245),fill=INK)
spaced(2770,115,'MM027',49,3,WHITE)
text(2770,460,'FHV',94,WHITE,True)
text(2770,840,'27 OCT',42,WHITE,True)
text(2770,900,'2026',42,WHITE)
spaced(3195,110,'MM',49,3)
text(3190,430,'027',95,bold=True)
text(3190,835,'FHV',65,bold=True)
r=random.Random(27);x=3200
while x<3440:
 width=r.choice([3,4,6,9]);d.rectangle((x,1030,x+width,1170),fill=INK);x+=width+r.choice([4,6,9])
text(2770,1320,'01',48,bold=True);text(3200,1320,'02',48,bold=True)
out=ROOT/'public/ticket-print.png';im.save(out)
print(out)
