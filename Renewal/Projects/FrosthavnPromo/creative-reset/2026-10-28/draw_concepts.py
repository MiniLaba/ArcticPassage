from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageFilter
import math,random
R=Path(__file__).resolve().parent;W,H=1920,1080
ZH='/System/Library/Fonts/STHeiti Medium.ttc';ZHL='/System/Library/Fonts/STHeiti Light.ttc';EN='/System/Library/Fonts/Supplemental/Georgia.ttf';ENS='/System/Library/Fonts/Supplemental/Arial.ttf'
def font(n,en=False,light=False):return ImageFont.truetype(EN if en else ZHL if light else ZH,n)
def gradient(a,b):
 im=Image.new('RGB',(W,H));d=ImageDraw.Draw(im)
 for y in range(H):
  t=y/(H-1);d.line((0,y,W,y),fill=tuple(round(a[i]*(1-t)+b[i]*t) for i in range(3)))
 return im.convert('RGBA')
def txt(im,xy,s,n=36,c='#e9e6d8',en=False,light=False):ImageDraw.Draw(im).text(xy,s,font=font(n,en,light),fill=c,spacing=18)
def line(im,pts,fill,width=2):ImageDraw.Draw(im).line(pts,fill=fill,width=width,joint='curve')
def curve(a,b,c,d,n=130):
 out=[]
 for i in range(n):
  t=i/(n-1);u=1-t;out.append((u**3*a[0]+3*u*u*t*b[0]+3*u*t*t*c[0]+t**3*d[0],u**3*a[1]+3*u*u*t*b[1]+3*u*t*t*c[1]+t**3*d[1]))
 return out
def foot(im,index,name,words):
 txt(im,(104,70),index+' / FROSTHAVN',26,c='#233f4a' if index=='B' else '#e9e6d8',en=True);txt(im,(104,942),words,32,c='#526e74' if index=='B' else '#e9e6d8',light=True)
 txt(im,(104,1002),name+'  ·  原创分镜概念，不代表游戏画面',23,c='#a0aeb0' if index!='B' else '#707a77',light=True)
def save(im,name):im.convert('RGB').save(R/(name+'.jpg'),quality=96)
# A: a warm light traverses a cold fjord. Original graphic construction only.
im=gradient((16,35,48),(38,66,79));d=ImageDraw.Draw(im)
d.polygon([(910,700),(1110,486),(1250,566),(1430,330),(1590,455),(1730,303),(1920,442),(1920,1080),(1170,1080)],fill='#263f4c')
d.polygon([(980,668),(1110,486),(1186,551),(1110,544)],fill='#c4d5da');d.polygon([(1290,512),(1430,330),(1570,439),(1436,399),(1375,464)],fill='#d2dedf');d.polygon([(1600,455),(1730,303),(1920,442),(1790,387),(1750,384)],fill='#b7ccd3')
d.polygon([(1100,858),(1340,704),(1520,755),(1710,626),(1920,748),(1920,1080),(900,1080)],fill='#68818c');d.polygon([(1170,861),(1340,704),(1520,755),(1710,626),(1920,748),(1854,782),(1690,700),(1520,828),(1360,779)],fill='#d5e0e1')
for x,y,c in [(1400,705,'#a46755'),(1535,735,'#b49d6b'),(1690,670,'#5c7f8a')]:
 d.rectangle((x,y,x+76,y+72),fill=c);d.polygon([(x-9,y),(x+38,y-38),(x+87,y)],fill='#e6e8dc')
 for xx in [x+15,x+46]:d.rectangle((xx,y+21,xx+14,y+40),fill='#f0cc80')
g=Image.new('RGBA',(W,H));pts=curve((850,1000),(1010,700),(1260,1020),(1435,743));line(g,pts,'#e0b46b',8);glow=g.filter(ImageFilter.GaussianBlur(17));im.alpha_composite(glow);im.alpha_composite(g)
txt(im,(102,230),'北方，\n为你留灯。',112);txt(im,(108,535),'A light in the north.',67,c='#d6b984',en=True)
foot(im,'A','叙事电影方向','冰海与暖灯  /  光线连接航空、渔港与居民');save(im,'A-light-in-the-north')
# B: custom airline paper architecture, not a reused passenger boarding pass.
im=gradient((233,228,208),(220,221,203));d=ImageDraw.Draw(im)
d.polygon([(880,824),(1200,326),(1370,680),(1580,361),(1840,850)],fill='#c0c9bf');d.polygon([(1200,326),(1150,736),(1370,680)],fill='#f6f3e4');d.polygon([(1580,361),(1456,755),(1840,850)],fill='#f4eedc');d.polygon([(1150,736),(1370,680),(1456,755),(1840,850),(1390,952),(880,824)],fill='#859b9d')
paper=Image.new('RGBA',(1060,420),'#f6f0dc');p=ImageDraw.Draw(paper);p.rectangle((0,0,1060,15),fill='#233f4a');p.line((810,0,810,420),fill='#8b9b95',width=2)
p.text((48,42),'MOONBIRD AIR',font=font(29,True),fill='#233f4a');p.text((46,115),'MM 027',font=font(83,True),fill='#233f4a');p.text((48,228),'THE VALLEY',font=font(27,True),fill='#6b817f');p.text((395,228),'FROSTHAVN',font=font(37,True),fill='#233f4a');p.arc((170,175,576,361),180,340,fill='#af7864',width=3);p.text((48,350),'A NORTHERN CHAPTER',font=font(23,True),fill='#6b817f');p.text((850,53),'027',font=font(51,True),fill='#233f4a')
for j in range(15):p.rectangle((851+j*10,170,854+j*10,308),fill='#233f4a')
paper=paper.rotate(-14,Image.Resampling.BICUBIC,expand=True);shadow=Image.new('RGBA',paper.size);shadow.paste('#213d4560',(0,0,paper.width,paper.height),paper.getchannel('A'));im.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(22)),(765,364));im.alpha_composite(paper,(750,340))
txt(im,(104,190),'下一站，\n霜灯港。',111,c='#233f4a');txt(im,(109,502),'Flight MM027',63,c='#a56b55',en=True)
foot(im,'B','航空品牌方向','折纸地形  /  航线字效  /  一张会展开世界的机票');save(im,'B-flight-mm027')
# C: actions and sound as the story; original illustrative water / float.
im=gradient((56,87,94),(24,55,68));d=ImageDraw.Draw(im)
for i in range(7):
 y=610+i*52;pts=[(x,y+math.sin(x/180+i)*9) for x in range(870,1920,8)];d.line(pts,fill=(94+i*3,125+i*3,128+i*3,110),width=2)
line(im,curve((1460,-90),(1090,260),(1780,425),(1460,687)),'#e6d8b6',3)
for rad in [85,149,225]:d.ellipse((1460-rad,701-rad*.2,1460+rad,701+rad*.2),outline='#a7beb8',width=2)
d.ellipse((1442,667,1478,713),fill='#d7c69b');d.pieslice((1442,667,1478,713),180,360,fill='#b97255');d.line((1460,651,1460,669),fill='#efe2ba',width=4)
for j,s in enumerate(['抛竿','咬钩','收鱼','炉火','相遇']):
 x=960+j*168;d.line((x,826,x+52,826),fill='#d1b87b',width=2);d.text((x,851),s,font=font(25),fill='#dfe3d7')
txt(im,(104,224),'先过好，\n北方的今天。',104);txt(im,(108,508),'A day worth staying for.',61,c='#dbc58e',en=True)
foot(im,'C','实录生活方向','用真实操作推进故事  /  让水、木头与脚步组成节奏');save(im,'C-a-day-in-the-north')
# D: macro ice facets and warm core as a brand film motif.
im=gradient((8,16,24),(15,33,43));d=ImageDraw.Draw(im);random.seed(27)
facets=[[(1080,170),(1440,96),(1320,532)],[(1440,96),(1810,270),(1320,532)],[(1810,270),(1850,728),(1320,532)],[(1850,728),(1490,955),(1320,532)],[(1490,955),(1040,812),(1320,532)],[(1040,812),(1080,170),(1320,532)]]
colors=['#2b5165','#4b7687','#1a3a50','#315d70','#1d4258','#375e6e']
for f,c in zip(facets,colors):d.polygon(f,fill=c);d.line(f+[f[0]],fill='#92c9d066',width=2)
for j in range(45):
 x=random.randint(1050,1840);y=random.randint(150,920);d.line((x,y,x+random.randint(-50,50),y+random.randint(20,100)),fill='#98c2ca28',width=1)
g=Image.new('RGBA',(W,H));gd=ImageDraw.Draw(g);gd.rectangle((1377,485,1447,591),fill='#e6b66b');im.alpha_composite(g.filter(ImageFilter.GaussianBlur(50)));im.alpha_composite(g);d=ImageDraw.Draw(im);d.line((1412,485,1412,591),fill='#382f2b',width=6);d.line((1377,536,1447,536),fill='#382f2b',width=6)
txt(im,(104,253),'霜与灯',145);txt(im,(111,481),'Where the cold\nfinds its light.',68,c='#b6cfd1',en=True)
foot(im,'D','实验视觉方向','冰晶折射  /  霜纹生长  /  冷色材质里的一点暖光');save(im,'D-frost-and-light')
# Four distinct, original concept frames in one board.
contact=Image.new('RGB',(1920,1080),'#142b36')
for i,n in enumerate(['A-light-in-the-north','B-flight-mm027','C-a-day-in-the-north','D-frost-and-light']):contact.paste(Image.open(R/(n+'.jpg')).resize((960,540),Image.Resampling.LANCZOS),((i%2)*960,(i//2)*540))
contact.save(R/'Frosthavn-four-directions.jpg',quality=96)
print(R/'Frosthavn-four-directions.jpg')
