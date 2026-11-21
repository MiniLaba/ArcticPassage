"""Authored pixel scenery for the website prologue. No image-generation service.

One coastline, building plan and runway underpin every light state and vignette.
These are website illustrations, not gameplay screenshots or exact stitched maps.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import random, math, json, argparse

R = Path(__file__).resolve().parents[1]
A = R / 'public/assets/prologue'
A.mkdir(parents=True, exist_ok=True)
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--mod',type=Path,default=R.parent/'ArcticPassage',help='Local candidate mod source; portraits/wildlife only')
MOD=parser.parse_args().mod.resolve()
W,H = 800,500
PALETTES = {
 'dusk': ['#182f40','#84939b','#405b6b','#183446','#bac7ce','#8ba0b0','#596b79','#324957','#d8b985'],
 'noon': ['#66899c','#d4deda','#7394a0','#2d5367','#e6e8df','#b3c6cd','#748087','#465d6a','#ead7a4'],
 'summer': ['#637b88','#e7c5a1','#a4ad9f','#395e68','#929b82','#6d8175','#766f64','#4b6261','#f0ce96'],
 'aurora': ['#0c2130','#425f71','#284b5b','#102f41','#88a8b8','#54788f','#405969','#223e50','#f0c78b'],
 'storm': ['#5a6d78','#a7b8bf','#738a93','#354f60','#cbd4d5','#a4b8c0','#75868d','#526775','#ecd7ae'],
}

def rgb(c): return tuple(bytes.fromhex(c[1:]))
def blend(a,b,t): return tuple(round(x*(1-t)+y*t) for x,y in zip(rgb(a),rgb(b)))

def world(mode):
 rng=random.Random(7183)
 sky, horizon, far, sea, snow, shade, rock, dark, lamp=PALETTES[mode]
 summer=mode=='summer'
 im=Image.new('RGB',(W,H)); d=ImageDraw.Draw(im)
 for y in range(H): d.line((0,y,W,y),fill=blend(sky,horizon,min(y/230,1)))
 if mode in ('summer','noon'):
  x,y=(164,103) if summer else (162,60)
  d.ellipse((x-12,y-12,x+12,y+12), fill='#f1d5a1' if summer else '#eee7c8')
 else:
  for i in range(58):
   x=rng.randrange(W);y=rng.randrange(10,125)
   if rng.random()>.35:d.point((x,y), fill='#a6b8bf')
  if mode!='storm': d.ellipse((142,35,151,44),fill='#e7d9b7');d.ellipse((146,32,155,41),fill=sky)
 if mode=='aurora':
  overlay=Image.new('RGBA',(W,H)); od=ImageDraw.Draw(overlay)
  for band in range(3):
   pts=[(x,35+band*12+int(14*math.sin(x/105+band))) for x in range(0,W+1,4)]
   od.line(pts,fill=(100,199,158,65-band*12),width=7+band*4)
   for x,y in pts: od.line((x,y,x,y+16),fill=(90,189,160,15),width=3)
  im=Image.alpha_composite(im.convert('RGBA'),overlay).convert('RGB');d=ImageDraw.Draw(im)
 # Low, glacially worn distant rock. No conifers or repeated alpine cones.
 ridge=[(0,161),(0,139),(32,141),(45,125),(70,123),(90,109),(114,115),(141,128),(177,127),(201,142),(239,147),(278,132),(305,134),(333,148),(365,139),(390,145),(421,151),(451,142),(482,152),(511,146),(552,157),(580,144),(606,147),(631,160),(665,152),(694,158),(730,149),(771,157),(800,151),(800,202)]
 d.polygon(ridge,fill=far)
 d.polygon([(0,141),(45,128),(90,112),(114,118),(138,131),(88,125),(66,129),(46,140),(0,152)],fill=shade)
 d.polygon([(0,160),(32,153),(73,155),(120,147),(166,160),(207,154),(253,163),(310,160),(360,174),(412,164),(466,174),(520,167),(581,178),(645,165),(708,177),(759,170),(800,179),(800,500),(0,500)],fill=sea)
 for i in range(330):
  x=rng.randrange(W);y=rng.randrange(174,H); length=rng.randrange(3,18)
  d.line((x,y,x+length,y),fill=blend(sea,far,rng.uniform(.1,.35)))
 # Monumental iceberg, with blue undercut and broken vertical faces.
 def berg(x,y,s=1):
  def pts(p):return [(x+round(a*s),y+round(b*s)) for a,b in p]
  d.polygon(pts([(-55,0),(-47,-25),(-34,-27),(-27,-52),(-5,-59),(9,-47),(24,-51),(39,-30),(49,-25),(63,-1),(40,12),(5,16),(-33,10)]),fill=shade)
  d.polygon(pts([(-55,0),(-47,-25),(-34,-27),(-27,-52),(-5,-59),(9,-47),(24,-51),(39,-30),(49,-25),(63,-1),(8,-8),(-16,-4)]),fill='#d0e1e2' if mode in ('aurora','dusk') else '#ecede2')
  d.polygon(pts([(9,-47),(24,-51),(39,-30),(49,-25),(63,-1),(19,6),(8,-8)]),fill='#91afbf' if mode!='summer' else '#b7cdd0')
  for a,b,c in [(-30,-27,-7),(-12,-42,0),(6,-31,7),(25,-22,9),(42,-15,0)]:d.line(pts([(a,b),(a+2,c)]),fill=shade,width=1)
  d.line(pts([(-65,14),(61,17)]),fill=far,width=2)
 berg(676,217,1.05);berg(760,179,.34);berg(550,175,.24)
 # Main landmass: connected terraces, weathered rock faces and a working inlet.
 coast=[(0,179),(49,165),(94,173),(128,160),(174,172),(211,180),(241,194),(278,192),(313,211),(350,209),(376,232),(412,231),(441,252),(472,256),(488,276),(526,277),(553,302),(551,325),(578,350),(566,372),(595,392),(578,422),(615,449),(610,500),(0,500)]
 face=[(x+3,y+13) for x,y in coast[:-2]]+[(610,500),(0,500)]
 d.polygon(face,fill=dark); d.polygon(coast,fill=rock)
 top=[(x-3,y-5) for x,y in coast[:-2]]+[(600,500),(0,500)]
 d.polygon(top,fill=snow)
 landmask=Image.new('1',(W,H));ImageDraw.Draw(landmask).polygon(top,fill=1)
 for i in range(2100):
  x=rng.randrange(0,610);y=rng.randrange(165,500)
  if not landmask.getpixel((x,y)):continue
  color=blend(snow,shade,rng.uniform(.15,.6))
  if rng.random()<.6:d.line((x,y,x+rng.randrange(1,5),y),fill=color)
  elif summer:d.rectangle((x,y,x+1,y+1),fill=rng.choice(['#b5a178','#687f71','#b2ac89']))
 # Two sculpted rock ribs structure the settlement rather than confetti rocks.
 for x,y,scale in [(74,211,1.2),(278,245,.8),(452,373,1.1),(52,458,1.4),(333,409,1)]:
  pp=[(x+int(a*scale),y+int(b*scale)) for a,b in [(0,0),(15,-15),(48,-22),(65,-13),(78,-4),(70,10),(31,16)]]
  d.polygon(pp,fill=rock)
  d.line(pp[:5],fill=shade,width=3)
  for j in range(4):d.line((x+16+j*10,y-7,x+11+j*10,y+9),fill=dark)
 # Camp promontory and marked high trail.
 d.polygon([(440,224),(464,208),(500,213),(529,234),(558,234),(580,254),(557,277),(524,270),(489,251),(463,251)],fill=dark)
 d.polygon([(438,217),(465,201),(501,206),(531,226),(559,227),(577,246),(557,266),(523,260),(488,241),(461,243)],fill=snow)
 def path(points,width=7):
  d.line(points,fill=shade,width=width+3,joint='curve');d.line(points,fill='#b4b9b0' if summer else '#d3d9d4',width=width,joint='curve')
 path([(130,383),(231,350),(312,329),(373,296),(430,294),(510,339),(550,390)])
 path([(374,296),(337,263),(294,226),(252,205)],5)
 path([(294,226),(366,215),(422,194),(471,163)],4)
 path([(366,215),(462,229),(528,242)],4)
 # A compact glacier ledge beyond the high trail.
 d.polygon([(421,178),(446,145),(465,135),(486,140),(500,159),(477,186)],fill=shade)
 d.polygon([(432,168),(451,143),(467,140),(478,146),(489,156),(469,167),(453,162)],fill='#e5e8df' if mode in ('noon','summer') else '#bfced5')
 # Snow runway shares the geometry used by the landing illustration.
 runway=[(47,357),(216,325),(255,343),(83,379)]
 d.polygon([(x,y+6) for x,y in runway],fill=shade);d.polygon(runway,fill='#b4c4c9' if not summer else '#8d9c97')
 d.line([runway[0],runway[1]],fill='#e7e6d8',width=2);d.line([runway[3],runway[2]],fill='#e7e6d8',width=2)
 for i in range(9):
  x=68+i*18;y=363-i*3.5;d.line((x,y,x+9,y-2),fill='#f1eedb',width=1)
 for i in range(8):
  x=48+i*24;y=351-i*4.5;d.line((x,y,x,y-4),fill=dark);d.rectangle((x-1,y-5,x+1,y-4),fill=lamp)
 # Native-scale Scandinavian timber architecture, with roofs, pilings and stairs.
 def house(x,y,w=27,h=23,color='#a95e4c',s=1,lit=True):
  w=int(w*s);h=int(h*s);dep=max(5,int(7*s)); roof=max(7,int(10*s))
  d.ellipse((x-5,y+h-1,x+w+dep+8,y+h+7),fill=shade)
  d.rectangle((x+2,y+h-4,x+w+dep-1,y+h+2),fill=rock)
  d.polygon([(x+w,y),(x+w+dep,y-5),(x+w+dep,y+h-4),(x+w,y+h)],fill=blend(color,dark,.35))
  d.rectangle((x,y,x+w,y+h),fill=color)
  for yy in range(y+3,y+h,3):d.line((x,yy,x+w,yy),fill=blend(color,dark,.17))
  d.polygon([(x-3,y),(x+w//2,y-roof),(x+w+3,y),(x+w+dep+4,y-5),(x+w//2+dep,y-roof-5),(x+w//2,y-roof)],fill=dark)
  d.polygon([(x-4,y-2),(x+w//2,y-roof-2),(x+w+3,y-2),(x+w+dep+4,y-7),(x+w//2+dep,y-roof-7),(x+w//2,y-roof-2)],fill=snow if not summer else '#83948e')
  d.line((x-2,y,x+w//2,y-roof,x+w+2,y),fill='#dedcc9',width=1)
  for xx in [x+4,x+w-9]:
   d.rectangle((xx-1,y+5,xx+6,y+13),fill='#d8d8c4')
   d.rectangle((xx,y+6,xx+5,y+12),fill=lamp if lit else '#405e68')
   d.line((xx+2,y+6,xx+2,y+12),fill='#8b7158');d.line((xx,y+9,xx+5,y+9),fill='#8b7158')
  d.rectangle((x+w//2-3,y+h-13,x+w//2+3,y+h),fill=dark)
  d.rectangle((x+w//2-4,y+h,x+w//2+5,y+h+2),fill='#8a8171')
  d.rectangle((x+w//2-6,y+h+3,x+w//2+7,y+h+4),fill='#a4a491')
  d.rectangle((x+w-6,y-roof-3,x+w-3,y-roof+5),fill=dark)
  if lit:d.line((x+w-4,y-roof-6,x+w-7,y-roof-15,x+w-4,y-roof-20),fill=shade,width=2)
  return x+w//2,y+h
 buildings=[(331,253,31,26,'#a25649'),(382,236,29,25,'#bc9561'),(431,260,30,24,'#497585'),(292,291,29,24,'#687f75'),(353,305,34,27,'#b15f4d'),(405,318,28,24,'#c1a46d'),(458,300,27,25,'#718990'),(483,343,35,27,'#426d7c'),(318,355,27,22,'#9a765d'),(230,309,26,21,'#a9795a'),(154,386,25,20,'#9c6757'),(211,389,33,24,'#536d78')]
 for args in sorted(buildings,key=lambda b:b[1]):house(*args,lit=mode!='noon')
 house(520,238,22,18,'#8c6a55',lit=True)
 house(271,220,18,16,'#586d70',lit=False)
 # Small snow shelter, not every northern home is an igloo.
 if not summer:
  d.pieslice((550,249,573,266),180,360,fill='#d2dddd');d.rectangle((550,258,573,265),fill='#d2dddd');d.rectangle((561,258,567,265),fill=dark)
 else:d.polygon([(550,265),(561,246),(574,265)],fill='#b99f75');d.polygon([(562,253),(565,265),(558,265)],fill=dark)
 # Active working harbour: decks, piles, gear, fish racks, two moored boats.
 for rect in [(524,378,575,386),(562,378,571,439),(546,424,609,432),(592,423,600,465)]:
  d.rectangle(rect,fill='#6e6d68')
  x0,y0,x1,y1=rect
  for xx in range(x0+1,x1,4):d.line((xx,y0,xx,y1),fill='#a1a294')
  for xx,yy in [(x0,y0),(x1,y1)]:d.line((xx,yy,xx,yy+12),fill=dark,width=2)
 def boat(x,y,c):
  d.ellipse((x-5,y+6,x+35,y+14),fill=far)
  d.polygon([(x,y),(x+32,y-5),(x+35,y+3),(x+28,y+9),(x+5,y+10)],fill=c)
  d.polygon([(x+5,y-1),(x+28,y-4),(x+28,y+2),(x+8,y+5)],fill=dark)
  d.rectangle((x+12,y-13,x+25,y),fill='#ddd7bf');d.rectangle((x+15,y-11,x+23,y-5),fill='#456374');d.line((x+19,y-13,x+19,y-26),fill=dark)
 boat(582,401,'#ae604b');boat(608,443,'#9bb7b4')
 for x,y in [(510,377),(528,362),(392,350)]:
  d.rectangle((x,y,x+11,y+7),fill='#8b7357');d.rectangle((x+2,y+2,x+9,y+4),fill='#485357');d.line((x+5,y,x+5,y+7),fill='#b09b78')
 for x in range(488,511,5):
  d.line((x,374,x,361),fill=dark);d.line((x,362,x+5,362),fill='#c4b79a');d.line((x+2,363,x+2,369),fill='#a19379',width=2)
 # Path lamps lead the eye; their amber exists only locally.
 for x,y in [(234,350),(288,336),(339,315),(386,296),(443,301),(489,329),(532,363),(549,395)]:
  d.line((x,y,x,y-11),fill=dark,width=1);d.rectangle((x-2,y-14,x+2,y-11),fill=lamp)
  if mode!='noon':d.line((x-5,y+2,x+6,y+2),fill=blend(snow,lamp,.38),width=2)
 # A few authentic-scale people and tiny footprints provide scale.
 for x,y,c in [(376,292,'#a66b52'),(511,367,'#718f8f'),(307,263,'#b9956f'),(180,396,'#9e715c')]:
  d.ellipse((x-3,y+7,x+4,y+9),fill=shade);d.rectangle((x-1,y,x+2,y+5),fill=c);d.rectangle((x,y-3,x+1,y-1),fill='#c6ac91');d.line((x,y+5,x-1,y+8),fill=dark);d.line((x+2,y+5,x+3,y+8),fill=dark)
  for j in range(3):d.point((x-6-j*3,y+9+j),fill=shade)
 # Near foreground rocks frame rather than conceal the harbour.
 d.polygon([(0,461),(24,442),(44,449),(61,473),(100,467),(127,486),(173,480),(194,500),(0,500)],fill=dark)
 d.polygon([(0,457),(24,439),(44,446),(61,469),(99,463),(126,482),(173,476),(192,493),(154,488),(122,494),(91,478),(58,482),(23,452),(0,470)],fill=shade)
 if mode=='storm':
  for i in range(320):
   x=rng.randrange(W);y=rng.randrange(H);d.line((x,y,x+7,y-2),fill='#d4dedf',width=1)
 return im

for mode in PALETTES:
 im=world(mode)
 im.resize((2400,1500),Image.Resampling.NEAREST).save(A/f'bay-{mode}.webp',quality=94,method=6)

# The landing uses the same runway surface, palette, village and geology.
# Pixel aircraft is drawn separately, so position and shadow can animate coherently.
plane=Image.new('RGBA',(150,56)); p=ImageDraw.Draw(plane)
p.polygon([(9,20),(5,1),(17,1),(31,21),(118,23),(138,32),(139,39),(64,42),(22,37),(8,28)],fill='#e6dfc6',outline='#2c4655')
p.polygon([(7,2),(16,2),(29,22),(15,21)],fill='#ad604c')
p.polygon([(14,29),(33,34),(138,33),(137,38),(63,40),(22,35)],fill='#a75d4c')
p.polygon([(45,22),(67,9),(98,10),(114,24)],fill='#80999e',outline='#344d59')
p.polygon([(54,20),(69,12),(96,13),(106,22)],fill='#d1d5c6')
for x in range(35,105,11):p.rectangle((x,25,x+6,30),fill='#395f71')
p.polygon([(112,25),(123,26),(133,31),(113,31)],fill='#34556a')
p.line((135,22,135,45),fill='#b4c1bd',width=2)
p.line((38,39,33,48),fill='#324b58',width=2);p.line((106,40,109,48),fill='#324b58',width=2)
p.line((16,50,54,50),fill='#b8c9ca',width=2);p.line((94,50,129,50),fill='#b8c9ca',width=2)
plane.resize((600,224),Image.Resampling.NEAREST).save(A/'aircraft.webp',lossless=True)

# Native portraits and wildlife are reused accurately, not regenerated.
for name in ['Ada','Mira','Roan','Nora','Levin','Amma']:
 Image.open(MOD/f'ContentPack/assets/portraits/{name}.png').crop((0,0,64,64)).save(A/f'{name.lower()}.webp',lossless=True)
atlas=Image.open(MOD/'Code/ArcticPassage/Runtime/assets/wildlife/sightings.png')
for name,col in [('fox',1),('seal',3),('whale',8)]:atlas.crop((col*32,0,col*32+32,24)).save(A/f'{name}.webp',lossless=True)

# Authored occupation vignettes share one quiet room and the same bay beyond.
bg=world('dusk')
for index,name in enumerate(['ada','mira','roan','nora','levin','amma']):
 room=Image.new('RGB',(400,250),'#3c4c50');q=ImageDraw.Draw(room)
 for y in range(250):q.line((0,y,400,y),fill=blend('#414f50','#1e353e',y/250))
 room.paste(bg.crop((230,165,650,428)).resize((260,165),Image.Resampling.NEAREST),(117,12));q=ImageDraw.Draw(room)
 q.rectangle((111,5,383,184),outline='#8b8770',width=6)
 q.line((248,10,248,180),fill='#88836c',width=5);q.line((115,98,380,98),fill='#88836c',width=4)
 q.rectangle((108,178,386,187),fill='#b2a17d');q.rectangle((0,211,400,250),fill='#615d4e')
 for x in range(-100,450,39):q.line((x,250,x+120,211),fill='#4a514b')
 q.rectangle((14,46,83,159),fill='#313f42',outline='#8d8066',width=2)
 q.rectangle((21,53,76,149),fill='#b9b498')
 for j in range(5):q.line((28,69+j*12,65-j*3,69+j*12),fill='#6f827a')
 q.rectangle((28,184,343,201),fill='#9b8060');q.rectangle((34,202,338,207),fill='#4b4e44')
 for x in [45,313]:q.polygon([(x,202),(x+12,202),(x+14,246),(x+3,246)],fill='#6a6250')
 # Lamp, ceramic mug and papers are shared visual grammar.
 q.rectangle((315,140,319,184),fill='#c1ac7d');q.polygon([(302,139),(307,119),(325,119),(332,139)],fill='#e6c17e')
 q.rectangle((269,173,281,184),fill='#bdc5b3');q.arc((278,174,288,182),-90,90,fill='#bdc5b3',width=2)
 q.polygon([(83,166),(132,169),(123,185),(76,180)],fill='#d9d3b3')
 for j in range(4):q.line((86,170+j*3,118-j*2,172+j*3),fill='#91a296')
 if name=='ada':
  for x in [145,184]:
   q.rectangle((x,163,x+34,185),fill='#8a6f51',outline='#c0a17a');q.line((x+4,173,x+30,173),fill='#534f45',width=3)
   q.polygon([(x+8,165),(x+16,158),(x+25,160),(x+28,167)],fill='#9bb5b6')
 elif name=='mira':
  q.polygon([(135,160),(218,166),(209,188),(129,180)],fill='#b9c2a4');q.line((143,170,159,165,177,179,202,170),fill='#a86b50',width=2)
  for x in [232,245]:q.rectangle((x,161,x+8,182),fill='#765b45');q.rectangle((x,179,x+13,185),fill='#765b45')
 elif name=='roan':
  for j in range(3):q.rectangle((139+j*3,165-j*5,237+j*3,173-j*5),fill='#bb9870',outline='#695946')
  q.line((245,162,258,180),fill='#c6ad82',width=4);q.rectangle((237,155,255,163),fill='#718a8a')
 elif name=='nora':
  q.rectangle((147,145,208,183),fill='#6a7f78',outline='#b6b49a',width=2);q.rectangle((154,152,193,166),fill='#243d46')
  q.line((161,160,170,155,179,162,188,156),fill='#d3bc88');q.line((204,146,212,109),fill='#9daea3',width=2)
  for x in [160,176,193]:q.ellipse((x,173,x+5,178),fill='#d8c28d')
 elif name=='levin':
  q.rectangle((151,156,197,184),fill='#c4c7a5',outline='#6a7a6b');q.line((174,156,174,183),fill='#7b8f80')
  q.ellipse((220,153,239,172),outline='#bcb995',width=3);q.line((234,170,243,183),fill='#bcb995',width=4)
 else:
  q.polygon([(144,181),(149,168),(161,163),(175,167),(181,181)],fill='#d2d9ca');q.rectangle((161,173,168,182),fill='#4c686d')
  q.arc((202,148,245,184),0,350,fill='#c2a578',width=5);q.line((212,174,226,161),fill='#c2a578',width=3)
 room.resize((1200,750),Image.Resampling.NEAREST).save(A/f'room-{name}.webp',quality=94,method=6)

(A/'manifest.json').write_text(json.dumps({'source':'tools/draw_prologue.py','kind':'Code-drawn website illustrations; portraits/wildlife from the mod. Not gameplay captures.','size':[2400,1500],'modes':list(PALETTES),'places':{'airport':[22,76],'town':[48,61],'harbour':[70,79],'fjord':[87,48],'tundra':[32,42],'camp':[67,49],'trail':[52,38],'glacier':[59,31]}},indent=2)+'\n')
print('Drew five shared-coast light states, aircraft, six workrooms; extracted native portraits and wildlife.')

# Share card: same coastline, restrained editorial typography. System fonts are
# rasterized locally; no font binaries are copied into the website.
card=Image.new('RGB',(1200,630),'#142f3c')
bay=world('dusk').resize((1008,630),Image.Resampling.NEAREST)
card.paste(bay,(500,0))
mask=Image.new('RGBA',card.size)
md=ImageDraw.Draw(mask)
for x in range(1200):
 a=255 if x<420 else max(0,255-int((x-420)*.7))
 md.line((x,0,x,630),fill=(20,47,60,a))
card=Image.alpha_composite(card.convert('RGBA'),mask).convert('RGB');cd=ImageDraw.Draw(card)
serif='/System/Library/Fonts/Supplemental/Times New Roman.ttf'
sans='/System/Library/Fonts/Helvetica.ttc'
cd.text((65,82),'MOONBIRD AIR / SOMEWHERE NORTH',font=ImageFont.truetype(sans,15),fill='#d2c5a6')
cd.text((60,197),'FROSTHAVN',font=ImageFont.truetype(serif,81),fill='#eee7d4')
cd.text((65,314),'A light left on for you.',font=ImageFont.truetype(serif,32),fill='#e2d2ad')
cd.line((65,480,420,480),fill='#536b72')
cd.text((65,506),'A NORTHERN CHAPTER FOR STARDEW VALLEY',font=ImageFont.truetype(sans,12),fill='#adbcb8')
card.save(R/'public/assets/social.jpg',quality=92,optimize=True)
