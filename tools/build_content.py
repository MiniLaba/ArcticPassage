"""Rebuild original pixel assets, Tiled maps and Content Patcher data. Python 3 + Pillow."""
from pathlib import Path
from PIL import Image, ImageDraw
import json, random, math, xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]; PACK=ROOT/'ContentPack'
PREFIX='ArcticPassage'; MOD='WhiteBay.ArcticPassage'; rng=random.Random(415)
def write(path,data):
 p=PACK/path; p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
EN={}; ZH={}
def tr(k,en,zh):
 if k.startswith('sign.camp.'):
  en+=' Enter: continue.'; zh+=' Enter：继续。'
 EN[k]=en.replace('Lumenhaven','Frosthavn').replace('LUMENHAVEN','FROSTHAVN'); ZH[k]=zh.replace('栖光湾','霜灯港')
 if k in ['sign.town','event.arrival2']:
  EN[k]+=' Press K for routes, your next step and nature notes.'
  ZH[k]+=' 按 K 打开随身手记，查看路线、下一步行程与自然笔记。'
 return '{{i18n:'+k+'}}'
def loc(n): return PREFIX+'_'+n
def obj(n): return PREFIX+'_'+n
# Deterministic native tiles plus retained original generated scene textures.
class Atlas:
 def __init__(self,season):
  self.im=Image.new('RGBA',(512,8192)); self.d=ImageDraw.Draw(self.im); self.used=0; self.tiles={}; self.props={}; self.season=season
 def add(self,name,w,h,paint,props=None):
  # Tile rows are allocated independently so every composite can be placed by GID.
  row=self.used; self.used+=h; x,y=0,row*16
  layer=Image.new('RGBA',(w*16,h*16)); paint(ImageDraw.Draw(layer),w*16,h*16); self.im.paste(layer,(x,y))
  ids=[[1+(row+j)*32+i for i in range(w)] for j in range(h)]; self.tiles[name]=ids
  if props: self.props[ids[0][0]-1]=props
  return ids
 def tile(self,name,base,typ=None,water=False):
  def paint(d,w,h):
   d.rectangle((0,0,15,15),fill=base)
   rr=random.Random(13+len(self.tiles))
   for _ in range(7):
    x,y=rr.randrange(16),rr.randrange(16); c=tuple(max(0,min(255,v+rr.choice([-8,8]))) for v in base); d.point((x,y),fill=c)
   if water:
    d.line((1,5,5,5),fill='#477e97'); d.line((9,12,13,12),fill='#477e97')
  p={'Type':typ or 'Stone','NoSpawn':'All'}
  if water: p.update(Water='T',Passable='T')
  return self.add(name,1,1,paint,p)
 def save(self): self.im.crop((0,0,512,self.used*16)).save(PACK/f'assets/tilesheets/ArcticPassage_{self.season}.png')

def make_atlas(season):
 a=Atlas(season); winter=season=='winter'; spring=season=='spring'
 ground=(210,227,232) if winter else (170,185,181) if spring else (132,132,112) if season=='fall' else (151,155,121)
 a.tile('ground',ground); a.tile('snow',(219,234,234)); a.tile('rock',(88,111,123)); a.tile('path',(183,167,135),'Dirt'); a.tile('water',(30,79,107),water=True); a.tile('floor',(161,121,80),'Wood')
 def pier(d,w,h):
  d.rectangle((0,0,w-1,h-1),fill='#9d7655')
  for y in [0,4,9,14]:d.line((0,y,w,y),fill='#684f42')
  d.line((1,1,1,15),fill='#c6a077'); d.point((13,2),fill='#4c4949'); d.point((13,11),fill='#4c4949')
 a.add('pier',1,1,pier,{'Type':'Wood','NoSpawn':'All'})
 def stone(d,w,h):
  d.polygon([(0,8),(3,2),(11,0),(15,7),(13,14),(3,15)],fill='#536979',outline='#3d5162');d.line((3,4,10,2,13,7),fill='#87999f')
 a.add('boulder',1,1,stone)
 def shrub(d,w,h):
  c='#747766' if season=='fall' else '#6f8b70'; c='#b3ced6' if winter else c
  d.line((8,15,7,6),fill='#655f56'); d.ellipse((2,4,12,11),fill=c);d.ellipse((6,1,14,8),fill=c);d.point((4,6),fill='#a6b38a')
 a.add('shrub',1,1,shrub)
 def sign(d,w,h):
  d.rectangle((7,9,9,15),fill='#4b5359');d.rectangle((0,1,15,11),fill='#3b4b54');d.rectangle((1,2,14,10),fill='#9e8058');d.rectangle((2,3,13,9),fill='#625348');d.line((3,4,12,4),fill='#8e7355');d.line((4,6,11,6),fill='#ddc796');d.line((4,8,8,8),fill='#ddc796');d.point((1,2),fill='#c2b99b');d.point((14,10),fill='#c2b99b')
 a.add('sign',1,1,sign)
 def crate(d,w,h):
  d.rectangle((1,2,14,15),fill='#9a7453',outline='#574d43');d.rectangle((3,4,12,12),outline='#cea47c');d.line((3,4,12,12),fill='#694f3b');d.line((12,4,3,12),fill='#694f3b')
 a.add('crate',1,1,crate)
 def lamp(d,w,h):
  d.rectangle((7,8,8,31),fill='#405163');d.rectangle((3,3,12,12),fill='#374d5c');d.rectangle((5,5,10,10),fill='#ffd48c');d.line((5,2,10,2),fill='#374d5c')
 a.add('lamp',1,2,lamp)
 for i,color in enumerate(['#b4534c','#497f9e','#cfaa53','#678776']):
  def house(d,w,h,c=color):
   d.rectangle((4,34,w-5,h-1),fill='#384d60');d.rectangle((3,27,w-4,h-7),fill=c)
   for y in range(31,h-6,5):d.line((4,y,w-5,y),fill='#ffffff22')
   d.polygon([(0,29),(w//2,3),(w-1,29)],fill='#394b60',outline='#293f51')
   d.polygon([(3,25),(w//2,5),(w-4,25)],fill='#e3e9e7' if winter or spring else '#63747b')
   for x in [11,w-24]:
    d.rectangle((x,35,x+12,48),fill='#3a4a50');d.rectangle((x+2,37,x+10,46),fill='#f4ce88');d.line((x+6,37,x+6,46),fill='#956c54')
   d.rectangle((w//2-7,h-29,w//2+6,h-7),fill='#473e39');d.rectangle((w//2-5,h-27,w//2+4,h-8),fill='#bd956e');d.point((w//2+2,h-17),fill='#f5dc9e')
   d.rectangle((w//2-10,h-6,w//2+9,h-1),fill='#b0b9b5');d.rectangle((w-20,1,w-13,16),fill='#776858')
  a.add('house'+str(i),5,5,house)
 def boat(d,w,h):
  d.ellipse((0,h-13,w-1,h-1),fill='#173e59');d.polygon([(2,29),(w-3,29),(w-11,45),(13,45)],fill='#b25e4d',outline='#493e3c');d.line((9,32,w-9,32),fill='#e2c496',width=2)
  d.rectangle((21,12,47,29),fill='#e4d7b7');d.rectangle((24,15,32,23),fill='#436c82');d.rectangle((36,15,44,23),fill='#436c82');d.line((18,11,49,11),fill='#3b4d5d',width=3);d.line((16,4,16,29),fill='#504a43');d.line((16,5,32,5),fill='#b8ada0')
 a.add('boat',5,3,boat)
 for i,(w,h) in enumerate([(6,4),(4,5),(7,3)]):
  def berg(d,W,H,n=i):
   points=[(0,H-11),(W//5,H//3),(W//3,H//2),(W//2,1),(W*3//4,H//3),(W-1,H-10),(W*3//4,H-1),(W//4,H-1)]
   d.polygon(points,fill='#c5e5e9',outline='#6ca5bd');d.polygon([(W//2,2),(W*3//4,H//3),(W-1,H-10),(W//2,H-7)],fill='#9dcbdc');d.polygon([(3,H-12),(W//5,H//3),(W//3,H//2),(W//2,2),(W//2,H-7)],fill='#ebf5ee');d.line((W//4,H-6,W*3//4,H-6),fill='#578da7')
  a.add('berg'+str(i),w,h,berg)
 def bed(d,w,h):
  d.rectangle((2,0,w-3,h-1),fill='#72513c');d.rectangle((3,2,w-4,h-3),fill='#b9cfd0');d.rectangle((4,3,w-5,10),fill='#e9e4ca');d.rectangle((3,13,w-4,h-4),fill='#a44f50');d.line((5,15,w-6,15),fill='#d88775')
 a.add('bed',2,3,bed)
 def table(d,w,h):
  d.rectangle((4,9,w-5,h-2),fill='#694c39');d.rectangle((1,2,w-2,h-6),fill='#c49b68',outline='#76583f');d.ellipse((9,8,20,15),fill='#e8d8b5');d.ellipse((12,10,18,13),fill='#906b4d')
 a.add('table',3,2,table)
 def rack(d,w,h):
  d.line((3,0,3,h-1),fill='#765940',width=3);d.line((w-4,0,w-4,h-1),fill='#765940',width=3);d.line((3,6,w-4,6),fill='#b89a6a',width=2)
  for x in range(10,w-5,10): d.line((x,6,x,12),fill='#705a46');d.ellipse((x-2,11,x+2,25),fill='#b5b0a0');d.polygon([(x-2,25),(x+2,25),(x,29)],fill='#a49b86')
 a.add('rack',3,2,rack)
 from arctic_art import enrich_atlas
 enrich_atlas(a)
 a.add('collision',1,1,lambda d,w,h:None)
 a.save();return a
ATLASES={s:make_atlas(s) for s in ['spring','summer','fall','winter']}
# Independent 16x16 fish silhouettes, kept deliberately readable in the inventory.
fishdefs=[('PolarCod','Polar cod','北极鳕',25,85,'smooth',6,15,'winter spring','Boreogadus saida. A small fish associated with cold Arctic waters.','Boreogadus saida。与北极寒冷海水及海冰环境关联的小型鱼类。'),('AtlanticCod','Atlantic cod','大西洋鳕鱼',40,120,'mixed',15,50,'summer fall','Gadus morhua. A demersal fish of North Atlantic and adjacent waters.','Gadus morhua。生活于北大西洋及邻近海域的底栖鱼类。'),('Capelin','Capelin','毛鳞鱼',20,65,'smooth',4,9,'spring summer','Mallotus villosus. A small schooling fish in northern seas.','Mallotus villosus。北方海洋中成群生活的小型鱼类。'),('ArcticChar','Arctic char','北极红点鲑',55,185,'dart',12,30,'summer fall','Salvelinus alpinus. Lives in fresh water; some populations migrate to the sea.','Salvelinus alpinus。生活于淡水，部分种群在海洋和淡水间洄游。'),('Halibut','Greenland halibut','格陵兰大比目鱼',80,340,'sinker',25,60,'spring summer fall winter','Reinhardtius hippoglossoides. A deep-water flatfish; available only on the offshore route.','Reinhardtius hippoglossoides。深水比目鱼，仅在已解锁的外海航线上出现。'),('Wolffish','Atlantic wolffish','大西洋狼鱼',65,215,'mixed',18,45,'spring summer fall','Anarhichas lupus. A bottom-dwelling fish associated with rocky habitats.','Anarhichas lupus。与岩礁底栖环境关联的鱼类。')]
icons=Image.new('RGBA',(128,16));di=ImageDraw.Draw(icons)
colors=['#92b7b2','#a5aa87','#b6cbd0','#b97e70','#8f8f87','#73878c']
for i,f in enumerate(fishdefs):
 x=i*16;c=colors[i];di.polygon([(x+2,8),(x+1,4),(x+5,6),(x+10,4),(x+14,7),(x+14,9),(x+9,12),(x+5,10),(x+1,12)],fill=c,outline='#384f60');di.line((x+6,9,x+12,9),fill='#d3d4b4');di.point((x+12,7),fill='#202e40');di.polygon([(x+7,5),(x+9,2),(x+11,5)],fill=c)
 if i==4:di.ellipse((x+4,3,x+14,13),fill=c,outline='#3b5261');di.point((x+12,6),fill='#202e40');di.point((x+12,8),fill='#202e40')
di.rectangle((98,3,109,14),fill='#d9c392',outline='#6d685d');di.line((101,6,107,6),fill='#8e7e64');di.line((101,9,107,9),fill='#8e7e64');icons.save(PACK/'assets/items/fish.png')
# Original and newly authored residents: four directions × four native walk frames.
# New residents use deliberately different cold-weather silhouettes and work gear.
people=[('Ada','艾达','#a2504a','#4c3531','#c99875'),('Mira','米拉','#4b8392','#3f3532','#bd8d6c'),('Roan','罗安','#be9955','#b98853','#deb18a'),
        ('Nora','诺拉','#456b82','#3a3030','#dfb18e'),('Levin','莱文','#657961','#58483c','#d4a47d'),('Amma','阿玛','#a45d46','#392e2c','#d6a17e')]

def paint_new_sprite(name, coat, hair, skin):
 im=Image.new('RGBA',(64,128));d=ImageDraw.Draw(im)
 palettes={
  'Nora':dict(shade='#304e63',light='#7896a6',trim='#dbe5df',accent='#d18453',pants='#354b5d',boot='#273c4b'),
  'Levin':dict(shade='#435948',light='#89967a',trim='#c7b58c',accent='#d4bb82',pants='#4d5348',boot='#303c3c'),
  'Amma':dict(shade='#793f39',light='#ce8060',trim='#e6ddc7',accent='#c4a76e',pants='#44464a',boot='#303b43')}
 p=palettes[name]
 for direction in range(4):
  for frame in range(4):
   x,y=frame*16,direction*32;step=[0,1,0,-1][frame]
   d.ellipse((x+2,y+28,x+13,y+31),fill='#22344260')
   # Short, insulated trousers and broad weather boots establish a sturdy winter stance.
   for lx,dy in [(5,step),(9,-step)]:
    d.rectangle((x+lx,y+22,x+lx+2,y+28+dy),fill=p['pants'])
    d.rectangle((x+lx-1,y+28+dy,x+lx+3,y+30+dy),fill=p['boot'])
    d.line((x+lx,y+28+dy,x+lx+2,y+28+dy),fill=p['light'])
   # Parka body with a shaded side seam, raised collar, cuffs and identifiable field equipment.
   d.polygon([(x+4,y+12),(x+11,y+12),(x+13,y+15),(x+12,y+24),(x+3,y+24),(x+2,y+16)],fill=coat,outline=p['shade'])
   d.line((x+4,y+14,x+4,y+22),fill=p['light']);d.line((x+11,y+15,x+11,y+22),fill=p['shade'])
   d.line((x+4,y+13,x+11,y+13),fill=p['trim']);d.line((x+4,y+24,x+11,y+24),fill=p['accent'])
   d.rectangle((x+2,y+16,x+3,y+21+step),fill=coat);d.rectangle((x+12,y+16,x+13,y+21-step),fill=coat)
   # Character-specific headwear and face shapes remain legible at 16×32 pixels.
   if name=='Nora':
    d.rectangle((x+2,y+3,x+13,y+13),fill=p['shade']);d.rectangle((x+4,y+3,x+11,y+12),fill=p['trim'])
    d.rectangle((x+5,y+5,x+10,y+12),fill=skin);d.rectangle((x+4,y+2,x+11,y+5),fill=coat)
    d.line((x+3,y+7,x+3,y+12),fill=p['light']);d.line((x+12,y+7,x+12,y+12),fill=p['light'])
    d.rectangle((x+5,y+13,x+10,y+15),fill=p['accent']);d.rectangle((x+6,y+16,x+9,y+20),fill=p['shade'])
    d.rectangle((x+9,y+17,x+12,y+20),fill='#344b5b');d.point((x+11,y+18),fill=p['accent'])
    # Small flight-service wing tab and radio on the parka.
    d.line((x+5,y+17,x+7,y+16,x+8,y+17),fill=p['trim']);d.point((x+7,y+17),fill=p['accent'])
    if direction==0:
     d.line((x+5,y+5,x+7,y+4,x+9,y+5),fill='#b8c8c7')
     d.point((x+6,y+9),fill='#293b48');d.point((x+9,y+9),fill='#293b48')
    elif direction in (1,3):d.point((x+(9 if direction==1 else 6),y+9),fill='#293b48')
    else:d.rectangle((x+5,y+6,x+10,y+11),fill=hair)
   elif name=='Levin':
    d.rectangle((x+4,y+3,x+11,y+12),fill=skin);d.rectangle((x+3,y+2,x+12,y+5),fill=hair)
    d.rectangle((x+5,y+1,x+10,y+3),fill=p['shade']);d.line((x+5,y+4,x+10,y+4),fill=p['accent'])
    d.rectangle((x+4,y+11,x+11,y+13),fill=hair);d.rectangle((x+5,y+13,x+10,y+15),fill=p['trim'])
    d.line((x+4,y+14,x+11,y+14),fill=p['accent']);d.rectangle((x+6,y+16,x+9,y+19),fill=p['light'])
    d.line((x+4,y+15,x+10,y+22),fill=p['accent']);d.rectangle((x+10,y+18,x+13,y+22),fill='#c8ae7c',outline=p['shade'])
    d.point((x+11,y+20),fill=p['trim']);d.point((x+12,y+20),fill=p['shade'])
    if direction==0:
     d.rectangle((x+4,y+7,x+7,y+9),outline=p['trim']);d.rectangle((x+9,y+7,x+12,y+9),outline=p['trim']);d.line((x+7,y+8,x+9,y+8),fill=p['trim'])
     d.point((x+6,y+8),fill='#293b48');d.point((x+10,y+8),fill='#293b48')
    elif direction in (1,3):d.point((x+(9 if direction==1 else 6),y+8),fill='#293b48')
    else:d.rectangle((x+4,y+5,x+11,y+11),fill=hair)
   else:
    # Amma's pale kerchief, silver side braid and warm harness-worker's coat.
    d.rectangle((x+4,y+3,x+11,y+12),fill=skin);d.rectangle((x+3,y+2,x+12,y+5),fill=p['trim'])
    d.rectangle((x+4,y+4,x+5,y+8),fill=hair);d.rectangle((x+10,y+4,x+11,y+8),fill=hair)
    d.line((x+5,y+12,x+10,y+12),fill=hair);d.line((x+4,y+6,x+11,y+6),fill='#f1ead9')
    d.rectangle((x+11,y+8,x+13,y+15),fill=hair);d.point((x+12,y+10),fill=p['trim']);d.point((x+12,y+13),fill=p['trim'])
    d.rectangle((x+5,y+14,x+10,y+16),fill=p['trim']);d.rectangle((x+6,y+16,x+9,y+19),fill=p['accent'])
    d.rectangle((x+4,y+18,x+7,y+21),fill=p['shade']);d.point((x+6,y+19),fill=p['trim'])
    d.line((x+4,y+17,x+6,y+16,x+8,y+17),fill=p['trim'])
    if direction==0:
     d.point((x+6,y+9),fill='#293b48');d.point((x+9,y+9),fill='#293b48')
     d.point((x+5,y+10),fill='#cf8271');d.point((x+10,y+10),fill='#cf8271')
    elif direction in (1,3):d.point((x+(9 if direction==1 else 6),y+9),fill='#293b48')
    else:d.rectangle((x+4,y+5,x+11,y+11),fill=hair)
 im.save(PACK/f'assets/characters/{name}.png')

def paint_new_portraits(name, coat, hair, skin):
 # The code-authored expression masters are shared with the website portraits.
 # Resize each frame independently: filtering across sheet borders can mix faces.
 source=ROOT/f'art/source/portrait-{name}-master.png'
 master=Image.open(source).convert('RGB')
 assert master.size==(1024,1536),f'Invalid expression master: {source}'
 sheet=Image.new('RGB',(128,192))
 for emotion in range(6):
  x=(emotion%2)*512;y=(emotion//2)*512
  frame=master.crop((x,y,x+512,y+512)).resize((64,64),Image.Resampling.LANCZOS)
  sheet.paste(frame,((emotion%2)*64,(emotion//2)*64))
 sheet.quantize(colors=96,dither=Image.Dither.NONE).convert('RGBA').save(PACK/f'assets/portraits/{name}.png')

for name,cn,coat,hair,skin in people:
 if name in ['Nora','Levin','Amma']:
  paint_new_sprite(name,coat,hair,skin);paint_new_portraits(name,coat,hair,skin)
 else:
  # Authored source sheets for the original residents remain authoritative.
  for kind,size,folder in [('portrait',(128,192),'portraits'),('sprite',(64,128),'characters')]:
   source=ROOT/f'art/source/{kind}-{name}-master.png'
   if source.exists():Image.open(source).convert('RGBA').resize(size,Image.Resampling.NEAREST).save(PACK/f'assets/{folder}/{name}.png')
 # Normalize authored source sheets to the engine grid; keep masters unchanged.
 for kind,size in [('portrait',(128,192)),('sprite',(64,128))]:
  source=ROOT/f'art/source/{kind}-{name}-master.png'
  if source.exists():
   if kind=='portrait' and name in ['Nora','Levin','Amma']:paint_new_portraits(name,coat,hair,skin)
   else:Image.open(source).convert('RGBA').resize(size,Image.Resampling.NEAREST).save(PACK/f'assets/{"portraits" if kind=="portrait" else "characters"}/{name}.png')
class Map:
 def __init__(self,name,w,h,season):
  self.name=name;self.w=w;self.h=h;self.season=season;self.a=ATLASES[season];self.layers={n:[[0]*w for _ in range(h)] for n in ['Back','Buildings','Front','AlwaysFront']};self.over={};self.warps=[];self.points={};self.properties={'Outdoors':'T','PassOutSafe':'T'}
 def tile(self,name,x,y,layer='Back'):
  ids=self.a.tiles[name]
  for j,row in enumerate(ids):
   for i,t in enumerate(row):
    if 0<=x+i<self.w and 0<=y+j<self.h:self.layers[layer][y+j][x+i]=t
 def rect(self,name,x,y,w,h,layer='Back'):
  for yy in range(y,y+h):
   for xx in range(x,x+w):self.tile(name,xx,yy,layer)
 def prop(self,x,y,k,v,layer='Buildings'):
  self.over.setdefault((layer,x,y),{})[k]=v
 def action(self,name,x,y,act):self.tile(name,x,y,'Buildings');self.prop(x,y,'Action',act)
 def composite(self,name,x,y,solid=True):
  ids=self.a.tiles[name];h=len(ids)
  for j,row in enumerate(ids):
   for i,t in enumerate(row):
    if 0<=x+i<self.w and 0<=y+j<self.h:self.layers['Buildings' if solid and j>=h-2 else 'Front'][y+j][x+i]=t
 def house(self,x,y,color,target=None):
  self.composite('house'+str(color),x,y)
  if target:self.prop(x+3,y+5,'Action',f'Warp 12 14 {loc(target)}')
  self.rect('path',x+2,y+6,3,3)
 def warp(self,x,y,target,tx,ty):self.warps.extend([str(x),str(y),loc(target),str(tx),str(ty)])
 def export(self):
  self.properties['Warp']=' '.join(self.warps)
  self.properties['LocationContext']='ArcticPassage_TundraClimate' if self.name in ['Tundra','WinterCamp','ResearchStation'] else 'ArcticPassage_CoastClimate'
  r=ET.Element('map',version='1.10',tiledversion='1.10.2',orientation='orthogonal',renderorder='right-down',width=str(self.w),height=str(self.h),tilewidth='16',tileheight='16',infinite='0')
  ps=ET.SubElement(r,'properties')
  for k,v in self.properties.items():ET.SubElement(ps,'property',name=k,value=v)
  ts=ET.SubElement(r,'tileset',firstgid='1',name='z_ArcticPassage',tilewidth='16',tileheight='16',tilecount=str(self.a.used*32),columns='32')
  ET.SubElement(ts,'image',source=f'ArcticPassage_{self.season}.png',width='512',height=str(self.a.used*16))
  for n,p in self.a.props.items():
   t=ET.SubElement(ts,'tile',id=str(n)); pp=ET.SubElement(t,'properties')
   for k,v in p.items():ET.SubElement(pp,'property',name=k,value=v)
  for i,(name,grid) in enumerate(self.layers.items()):
   ly=ET.SubElement(r,'layer',id=str(i+1),name=name,width=str(self.w),height=str(self.h));ET.SubElement(ly,'data',encoding='csv').text='\n'+',\n'.join(','.join(map(str,row)) for row in grid)+'\n'
  # Per-instance properties use Tiled tile clones, since standard TMX layers cannot hold TileData.
  nextid=self.a.used*32
  for (layer,x,y),p in self.over.items():
   gid=self.layers[layer][y][x]
   # SMAPI's TMX loader supports per-tile properties through a dedicated tileset tile definition.
   # Use a one-tile inline tileset referencing a cropped, original tile PNG.
   old=gid-1; src=PACK/f'assets/tilesheets/ArcticPassage_{self.season}.png'; tile=Image.open(src).crop(((old%32)*16,(old//32)*16,(old%32+1)*16,(old//32+1)*16))
   key=f'{self.name}_{self.season}_{layer}_{x}_{y}';out=PACK/f'assets/tilesheets/{key}.png';tile.save(out)
   newgid=nextid+1;nextid+=1
   extra=ET.Element('tileset',firstgid=str(newgid),name='z_'+key,tilewidth='16',tileheight='16',tilecount='1',columns='1');ET.SubElement(extra,'image',source=key+'.png',width='16',height='16');t=ET.SubElement(extra,'tile',id='0');pp=ET.SubElement(t,'properties')
   # Preserve inherited terrain properties when decorating a Back tile.
   for k,v in {**self.a.props.get(old,{}),**p}.items():ET.SubElement(pp,'property',name=k,value=v)
   r.insert(2,extra) # sorted below
   self.layers[layer][y][x]=newgid
  from scene_maps import append_scene
  append_scene(r,self,nextid)
  # xTile expects tilesets sorted by firstgid, then layers.
  children=list(r);r[:]=[c for c in children if c.tag=='properties']+sorted([c for c in children if c.tag=='tileset'],key=lambda c:int(c.get('firstgid')))+[c for c in children if c.tag=='layer']
  for ly in r.findall('layer'):
   ly.find('data').text='\n'+',\n'.join(','.join(map(str,row)) for row in self.layers[ly.get('name')])+'\n'
  # TMXTile stores instance properties in hidden, same-name TileData object layers.
  # NPC updateDoors reads instance Action, so index properties alone are insufficient.
  for layer in self.layers:
   records=[(x,y,p) for (name,x,y),p in self.over.items() if name==layer]
   if not records:continue
   group=ET.SubElement(r,'objectgroup',name=layer,visible='0')
   for x,y,p in records:
    tiledata=ET.SubElement(group,'object',name='TileData',x=str(x*16),y=str(y*16),width='16',height='16')
    pp=ET.SubElement(tiledata,'properties')
    for k,v in p.items():ET.SubElement(pp,'property',name=k,type='string',value=v)
  ET.indent(r);ET.ElementTree(r).write(PACK/f'assets/maps/{self.name}_{self.season}.tmx',encoding='utf-8',xml_declaration=True)
  return r
 def preview(self):
  im=Image.new('RGBA',(self.w*16,self.h*16));sheet=self.a.im
  for layer,grid in self.layers.items():
   for y,row in enumerate(grid):
    for x,g in enumerate(row):
     if not g:continue
     if g in getattr(self,'scene_detail_tiles',{}):t=self.scene_detail_tiles[g]
     elif hasattr(self,'scene_first') and g>=self.scene_first:
      index=g-self.scene_first;t=self.scene_image.crop(((index%self.w)*16,(index//self.w)*16,(index%self.w+1)*16,(index//self.w+1)*16))
     elif g<=self.a.used*32:t=sheet.crop((((g-1)%32)*16,((g-1)//32)*16,((g-1)%32+1)*16,((g-1)//32+1)*16))
     else:t=Image.open(PACK/f'assets/tilesheets/{self.name}_{self.season}_{layer}_{x}_{y}.png')
     im.alpha_composite(t,(x*16,y*16))
  im.convert('RGB').resize((self.w*24,self.h*24),Image.Resampling.NEAREST).save(ROOT/f'previews/{self.name}_{self.season}.png')
MAPS={}
for season in ATLASES:
 for name,w,h in [('Town',64,48),('Harbor',64,48),('Icefjord',72,56),('Tundra',64,48),('Guesthouse',24,18),('Fishery',24,18),('WinterCamp',64,48),('ResearchStation',24,18)]:
  m=Map(name,w,h,season);rr=random.Random(75+len(name));m.rect('ground',0,0,w,h)
  if name in ['Town','Harbor','Icefjord','Tundra']:
   m.rect('rock',0,0,w,2,'Buildings');m.rect('rock',0,h-2,w,2,'Buildings');m.rect('rock',0,0,2,h,'Buildings');m.rect('rock',w-2,0,2,h,'Buildings')
  if name=='Town':
   for y in range(2,h-2):
    edge=40+int(2*math.sin(y/5));m.rect('water',edge,y,w-edge,1)
   m.rect('path',17,25,25,3);m.rect('path',27,5,4,39);m.rect('path',17,14,22,2);m.rect('pier',38,24,11,4)
   m.house(17,19,0,'Guesthouse');m.house(32,19,1,'Fishery');m.house(16,7,2);m.house(32,6,3);m.house(18,33,1);m.house(33,34,0)
   m.action('sign',36,27,'Warp 28 33 Beach');m.action('sign',26,24,'Message ArcticPassage_TownGuide');m.action('sign',22,26,'Message ArcticPassage_InnGuide');m.warp(42,25,'Harbor',24,25);m.warp(42,26,'Harbor',24,26)
   m.rect('path',29,2,2,4);m.layers['Buildings'][1][29]=0;m.layers['Buildings'][1][30]=0;m.warp(29,1,'Tundra',29,43);m.warp(30,1,'Tundra',30,43)
   for x,y in [(16,25),(24,24),(32,25),(39,24),(28,12),(28,35)]:m.composite('lamp',x,y,False)
   m.composite('berg2',48,8,False)
   for xx,yy in [(5,6),(6,7),(23,9),(38,11),(7,30),(13,31),(14,35),(7,40),(26,41),(36,43),(14,18),(7,17)]:
    m.tile('boulder' if (xx+yy)%3==0 else 'shrub',xx,yy,'Buildings')
   for xx,yy in [(24,22),(39,22),(24,11),(39,11)]:m.tile('crate',xx,yy,'Buildings')
   m.points={'spawn':[29,26]}
  elif name=='Harbor':
   for y in range(2,h-2):
    edge=25+int(3*math.sin(y/6));m.rect('water',edge,y,w-edge,1)
   m.rect('path',2,24,25,4);m.rect('pier',24,24,24,4);m.rect('pier',35,14,4,25);m.rect('pier',23,13,16,3);m.rect('pier',23,36,16,3)
   m.house(8,9,0);m.house(9,32,2);m.action('sign',21,23,'OpenShop ArcticPassage_Orders');m.action('crate',15,22,'OpenShop ArcticPassage_Supplies');m.action('sign',43,23,'Message ArcticPassage_BoatLocked')
   m.action('sign',32,14,'Message ArcticPassage_Fishing');m.action('sign',23,35,'Message ArcticPassage_Workshop');m.composite('boat',40,27,False)
   m.composite('rack',11,29);m.composite('crate',19,18);m.composite('crate',20,19);m.composite('berg0',52,6,False);m.composite('berg1',54,36,False)
   m.warp(2,25,'Town',54,23);m.warp(2,26,'Town',54,23);m.points={'spawn':[24,25],'fishing':[38,20],'boat':[43,24]}
  elif name=='Icefjord':
   m.rect('water',2,2,w-4,h-4);m.rect('rock',2,32,23,20);m.rect('snow',3,33,20,18);m.rect('pier',9,31,4,16);m.rect('pier',9,40,26,4);m.rect('pier',31,35,4,9)
   for n,x,y in [('berg0',35,8),('berg1',53,22),('berg2',25,25),('berg1',15,8),('berg0',49,42)]:m.composite(n,x,y,False)
   m.composite('boat',13,44,False);m.action('sign',9,37,f'Warp 42 24 {loc("Harbor")}');m.action('sign',32,34,'Message ArcticPassage_DeepWater');m.action('sign',5,34,'Message ArcticPassage_WhaleNote');m.points={'spawn':[32,40],'fishing':[34,39]}
  elif name=='Tundra':
   # A bare coastal tundra, with a sinuous meltwater stream and a connected footbridge.
   for y in range(2,h-2):
    x=40+int(4*math.sin(y/6));m.rect('water',x,y,4,1)
   m.rect('path',28,2,4,44);m.rect('path',28,24,21,3);m.rect('pier',35,24,18,3);m.rect('path',48,15,4,12)
   for i in range(65):
    x,y=rr.randrange(4,59),rr.randrange(4,42)
    if m.layers['Back'][y][x]==m.a.tiles['ground'][0][0]:m.tile('shrub' if i%3 else 'boulder',x,y,'Buildings')
   m.action('sign',27,39,'Message ArcticPassage_TundraGuide');m.action('sign',48,23,'Message ArcticPassage_Char');m.action('sign',29,5,'Message ArcticPassage_Safety')
   m.layers['Buildings'][46][29]=0;m.layers['Buildings'][46][30]=0;m.warp(29,46,'Town',27,2);m.warp(30,46,'Town',27,2);m.points={'spawn':[29,43],'fishing':[39,25]}
  elif name in ['WinterCamp','ResearchStation']:pass
  else:
   m.properties={'PassOutSafe':'T'};m.rect('floor',0,0,w,h);m.rect('rock',0,0,w,4,'Buildings');m.rect('rock',0,h-1,w,1,'Buildings');m.rect('rock',0,0,1,h,'Buildings');m.rect('rock',w-1,0,1,h,'Buildings');m.layers['Buildings'][h-1][12]=0
   m.composite('table',7,8);m.composite('table',16,8)
   if name=='Guesthouse':
    m.composite('bed',3,5,False)
    for yy in [6,7]:
     for xx in [3,4]:m.prop(xx,yy,'Bed','T','Back');m.prop(xx,yy,'TouchAction','Sleep','Back')
    m.action('sign',12,4,'Message ArcticPassage_Lodging');m.warp(12,17,'Town',18,23)
   else:m.action('crate',10,5,'OpenShop ArcticPassage_Market');m.action('sign',13,5,'OpenShop ArcticPassage_Orders');m.warp(12,17,'Town',33,23)
   m.points={'spawn':[12,14]}
  from arctic_art import decorate_map
  decorate_map(m)
  from scene_maps import configure_scene
  configure_scene(m)
  MAPS[name,season]=m;m.export()
  if season in ['spring','summer','winter']:m.preview()
# SMAPI resolves custom map tilesheets reliably when stored beside the TMX.
import shutil
for image_path in (PACK/'assets/tilesheets').glob('*.png'):
 shutil.copy2(image_path,PACK/'assets/maps'/image_path.name)
# Patcher assembly
changes=[]
def patch(action,target,**kw):changes.append({'LogName':kw.pop('LogName',target),'Action':action,'Target':target,**kw})
audio={}
for cue in ['CoastalWind','TundraWind','IndoorWind']:
 audio[loc(cue)]={'Id':loc(cue),'FilePaths':['{{AbsoluteFilePath: assets/audio/'+cue+'.wav}}'],'Category':'Ambient','Looped':True,'UseReverb':False,'StreamedVorbis':False}
for cue in ['LumenhavenTheme','IcefjordTheme','PolarNightTheme']:
 audio[loc(cue)]={'Id':loc(cue),'FilePaths':['{{AbsoluteFilePath: assets/audio/'+cue+'.ogg}}'],'Category':'Music','Looped':True,'UseReverb':False,'StreamedVorbis':True}
patch('EditData','Data/AudioChanges',Entries=audio)
contexts={}
for name,cue in [('CoastClimate','CoastalWind'),('TundraClimate','TundraWind')]:
 contexts[loc(name)]={
  'PlayRandomAmbientSounds':False,'DayAmbience':loc(cue),'NightAmbience':loc(cue),'Music':[],
  'AllowRainTotem':False,
  # Native Wind includes valley petals/leaves; it is not an Arctic wind effect.
  # These are authored game probabilities, not measured Greenland climatology.
  'WeatherConditions':[
   {'Id':'WinterSnow','Condition':'SEASON winter, RANDOM 0.45','Weather':'Snow'},
   {'Id':'SpringSnow','Condition':'SEASON spring, RANDOM 0.30','Weather':'Snow'},
   {'Id':'AutumnSnow','Condition':'SEASON fall, RANDOM 0.20','Weather':'Snow'},
   {'Id':'SummerRain','Condition':'SEASON summer, RANDOM 0.25','Weather':'Rain'},
   {'Id':'AutumnRain','Condition':'SEASON fall, RANDOM 0.15','Weather':'Rain'},
   {'Id':'Clear','Condition':None,'Weather':'Sun'}
  ]}
 if name=='TundraClimate':contexts[loc(name)]['CopyWeatherFromLocation']=loc('CoastClimate')
patch('EditData','Data/LocationContexts',Entries=contexts)
write(Path('manifest.json'),{'Name':'霜灯港 / Frosthavn','Author':'WhiteBay Project','Version':'0.7.10','Description':'Frosthavn: an Arctic fishing port, seasonal field camp, research shelter and personal nature notes.','UniqueID':MOD,'Dependencies':[{'UniqueID':'WhiteBay.ArcticPassage.Runtime','MinimumVersion':'0.7.10','IsRequired':True}],'MinimumApiVersion':'4.5.2','ContentPackFor':{'UniqueID':'Pathoschild.ContentPatcher','MinimumVersion':'2.4.0'}})
locations={}
for name,zh in [('Town','栖光湾小镇'),('Harbor','栖光湾渔港'),('Icefjord','冰山峡湾'),('Tundra','极地苔原'),('Guesthouse','栖光湾旅舍'),('Fishery','渔业收购站'),('WinterCamp','苔原营地'),('ResearchStation','营地研究站')]:
 patch('Load','Maps/'+loc(name),FromFile='assets/maps/'+name+'_{{MapSeason}}.tmx')
 locations[loc(name)]={'DisplayName':tr('location.'+name,{'Town':'Lumenhaven','Harbor':'Lumenhaven Harbor','Guesthouse':'Lumenhaven Guesthouse','Fishery':'Fish Market','Icefjord':'Icefjord','Tundra':'Arctic Tundra','WinterCamp':'Tundra Field Camp','ResearchStation':'Field Research Shelter'}[name],zh),'DefaultArrivalTile':{'X':MAPS[name,'summer'].points['spawn'][0],'Y':MAPS[name,'summer'].points['spawn'][1]},'CreateOnLoad':{'MapPath':'Maps/'+loc(name)},'CanPlantHere':False,'CanHaveGreenRainSpawns':False,'MinDailyWeeds':0,'MaxDailyWeeds':0,'MinDailyForageSpawn':0,'MaxDailyForageSpawn':0,'Fish':[]}
 locations[loc(name)].update(MusicDefault=loc('IcefjordTheme' if name in ['Icefjord','Tundra','WinterCamp','ResearchStation'] else 'LumenhavenTheme'),Music=[{'Id':loc('Night'),'Track':loc('PolarNightTheme'),'Condition':'TIME 1800 2600'}],MusicIgnoredInRain=False,MusicIgnoredInSpring=False,MusicIgnoredInSummer=False,MusicIgnoredInFall=False,MusicIgnoredInFallDebris=False,MusicIgnoredInWinter=False)
 if name in ['Harbor','Icefjord']:locations[loc(name)]['FishAreas']={'Default':{'CrabPotFishTypes':['ocean']}}
fishdefs.append(('GoldenRedfish','Golden redfish','金红鱼',60,170,'mixed',12,32,'summer fall','Sebastes norvegicus. An orange-red deep-water North Atlantic fish; found on the offshore route.','Sebastes norvegicus。橙红色的北大西洋深水鱼，仅在外海航线出现。'))
objects={};fish={}
for i,(key,en,zh,difficulty,price,behavior,mi,ma,seasons,desc,desczh) in enumerate(fishdefs):
 id=obj(key);objects[id]={'Name':en,'DisplayName':tr('fish.'+key+'.name',en,zh),'Description':tr('fish.'+key+'.description',desc,desczh),'Type':'Fish','Category':-4,'Price':price,'Texture':'Mods/'+MOD+'/Fish','SpriteIndex':i,'Edibility':12,'ExcludeFromRandomSale':True,'ContextTags':['fish_arcticpassage','fish_ocean' if key!='ArcticChar' else 'fish_river']}
 fish[id]=f'{en}/{difficulty}/{behavior}/{mi}/{ma}/600 2600/{seasons}/both/0/1/0.65/0.05/0/true'
 areas=['Tundra'] if key=='ArcticChar' else ['Icefjord'] if key in ['Halibut','GoldenRedfish'] else ['Harbor','Icefjord']
 for area in areas:
  for season in seasons.split():
   entry={'Id':id+'_'+season,'ItemId':'(O)'+id,'Season':season,'Chance':0.75,'Precedence':-20,'MinFishingLevel':4 if key=='Halibut' else 2 if key=='GoldenRedfish' else 0}
   if key=='Wolffish' and area=='Harbor':entry['BobberPosition']={'X':23,'Y':4,'Width':18,'Height':18}
   locations[loc(area)]['Fish'].append(entry)
objects[obj('Receipt')]={'Name':'Lumenhaven receipt','DisplayName':tr('receipt.name','Harbor order receipt','港口交货收据'),'Description':tr('receipt.desc','Payment was added to your wallet. Keep as a souvenir or discard.','货款已直接入账。收据可留作纪念或丢弃。'),'Type':'Basic','Category':0,'Price':0,'Texture':'Mods/'+MOD+'/Fish','SpriteIndex':6,'Edibility':-300,'ExcludeFromShippingCollection':True,'ExcludeFromRandomSale':True,'CanBeGivenAsGift':False}
patch('Load','Mods/'+MOD+'/Fish',FromFile='assets/items/fish.png');patch('EditData','Data/Objects',Entries=objects);patch('EditData','Data/Fish',Entries=fish);patch('EditData','Data/Locations',Entries=locations)
# Minimal, additive departure sign on the vanilla beach pier (no replacement of Beach).
patch('EditMap','Maps/Beach',AddWarps=['29 34 '+loc('Town')+' 36 23'])
# Three social NPCs, with all-season default, winter and rainy schedules.
characters={};gifts={}
line_sets={
'Ada':[
('The tide board is the first thing I check each morning.','我每天早晨先看潮汐记录。'),('A small catch handled well is worth more than a crate left warm.','少量渔获保存得当，比一箱放坏的鱼更有价值。'),('The order board pays directly. Read which species is needed.','订单板会直接结清货款，先看清所需鱼种。'),('Willy says you know how to be patient with a fishing rod.','威利说，你拿起钓竿的时候很有耐心。'),('Our harbor is small. Everyone knows when a boat is late.','港口很小，有船晚归，大家都会留意。'),('Capelin arrive in schools. The gulls often notice first.','毛鳞鱼结群而来，海鸟常常先发现。'),('Coffee can wait. Fish cannot.','咖啡可以晚点喝，鱼货可等不得。'),('The blue building is our fishery. Come in out of the wind.','蓝房子是收购站，进来避避风吧。'),('A good crate needs drainage and a clear label.','好鱼箱得排水通畅，标签也要清楚。'),('Roan repairs what the salt wears down. It is endless work.','盐雾磨损的东西，都归罗安修。这活儿没个完。'),('There is no prize for landing more than you can handle.','捕得太多却照看不过来，不是什么值得夸耀的事。'),('We keep the deep-water route separate from the harbor.','深水航线和港内作业是分开的。'),('Your first order does not expire. Take your time.','第一批货没有交货期限，慢慢来。'),('A clean worktable is a useful kind of luxury.','干净的操作台，是很实用的享受。'),('I keep the old shipping ledgers. They tell quite a story.','我留着旧货运账本，里面故事可不少。'),('Not every northern town catches the same species.','北方不同小镇，捕到的鱼也不尽相同。'),('I like an orderly morning and an unhurried supper.','我喜欢井然有序的早晨，也喜欢慢慢吃晚饭。'),('The first crate of the season always feels special.','每个季节的第一箱鱼，总让人有些期待。'),('Thanks for bringing your catch in carefully.','谢谢你细心照看这些渔获。'),('You have made yourself part of this harbor.','这座港口已经有了你的一份日常。')],
'Mira':[
('Check the route before you check the clock.','先确认路线，再看时间。'),('Sea ice can look solid from a distance. We stay on shore.','海冰从远处看常常很坚实。我们留在岸上。'),('My dogs each have their own pace. A team learns to listen.','每只犬的步调不同，队伍要慢慢学着配合。'),('Summer tundra is not a forest hiding under snow.','夏天的苔原，并不是雪下面藏着一片森林。'),('Those low plants grow slowly. Stay on the marked path.','低矮植物长得很慢，尽量走标好的路。'),('For a winter journey, check the equipment notes at our tundra stop.','冬季出行前，请先查看苔原停靠处的装备说明。'),('Wild bears need distance, never food from our hands.','观察野生熊要保持距离，绝不能喂食。'),('I like the sound of boots on packed snow.','我喜欢靴子踩在压实雪上的声音。'),('A good guide knows when to turn back.','好向导知道什么时候该返程。'),('A sheltered place to rest is part of a good route.','好的路线，总得有能避风歇脚的地方。'),('The river belongs to the char before it belongs to our maps.','在我们画出地图以前，红点鲑就生活在这条河里了。'),('You can watch a fox without following it.','可以安静看狐狸，不必追着它走。'),('The hills are quiet today. That does not mean empty.','今天山坡很安静，但不代表那里没有生命。'),('I mend a strap before it breaks.','我习惯在皮带断裂前把它修好。'),('Snow houses are seasonal shelters, not every northern home.','雪屋是季节性庇护所，并不是北方所有人的日常住宅。'),('A bright summer night can make bedtime easy to forget.','夏夜太明亮，常让人忘记该睡了。'),('The path north takes you onto the tundra.','朝北走，就是苔原小路。'),('We return with the same team we set out with.','我们带着完整的队伍出发，也要一起回来。'),('A warm drink is even better after a careful journey.','稳稳当当走完一程，再喝热饮格外舒服。'),('You have learned to look before you hurry.','你已经学会在赶路之前，先仔细看看。')],
'Roan':[
('Salt finds every screw I forget to grease.','忘了上油的螺钉，总会被盐雾找到。'),('I am fixing the processing shed, one board at a time.','我正在修加工棚，一块木板一块木板地修。'),('Bring the materials to me, not to the order board.','修理材料直接交给我，不用交到订单板。'),('A boat is a collection of small jobs done properly.','把每件小事做好，才有一艘可靠的船。'),('That old hull still has good years in it.','那条老船的船体，还能再用好多年。'),('We only open the fjord route after the repairs.','修理完成后，才会开放峡湾航线。'),('Willy once sent me a box of spare fittings. Useful fellow.','威利给我寄过一箱备用配件，他真是个热心人。'),('The smoker needs coal. Good fish deserves careful processing.','熏鱼机要用煤。好鱼也值得认真加工。'),('I wrote the measurement down. Somewhere very sensible.','尺寸我记下来了。放在一个很合理的地方……'),('A dry pair of gloves saves a surprising amount of trouble.','一副干手套，能省去不少麻烦。'),('Icebergs are scenery, not stepping stones.','冰山是值得看的风景，可不能当垫脚石。'),('The pier rail is there for a reason.','码头护栏可不是摆设。'),('I prefer repairing things to throwing them away.','比起扔掉，我更愿意修一修。'),('The yellow house catches the afternoon light nicely.','下午的光照在黄房子上，特别好看。'),('When the wind rises, the workbench can wait.','风起得太大，工作台上的活儿就先放一放。'),('A small leak gets a large note in my book.','再小的渗漏，我也会在本子上郑重记下来。'),('I am proud of this little harbor.','我挺为这座小港口骄傲的。'),('Thank you for lending a hand with the first shipment.','谢谢你来帮忙准备第一批货。'),('The fjord is deeper than it looks from the landing.','从登岸处看不出来，峡湾其实很深。'),('There is always another hinge to oil tomorrow.','明天，总还有一副铰链等着上油。')]}
from resident_dialogue import NEW_DIALOGUE
line_sets.update(NEW_DIALOGUE)
resident_profiles={
 'Ada':('Fishery',5,'fall',9,'Female','Neutral'),
 'Mira':('Guesthouse',10,'winter',15,'Female','Neutral'),
 'Roan':('Guesthouse',15,'summer',21,'Male','Outgoing'),
 'Nora':('Guesthouse',8,'spring',8,'Female','Outgoing'),
 'Levin':('ResearchStation',12,'summer',4,'Male','Neutral'),
 'Amma':('Guesthouse',15,'fall',18,'Female','Outgoing')}
for index,(name,cn,coat,hair,skin) in enumerate(people):
 id=loc(name);home,hx,birth_season,birth_day,gender,social=resident_profiles[name]
 characters[id]={'DisplayName':tr('npc.'+name,name,cn),'Gender':gender,'Age':'Adult','Manner':'Polite','SocialAnxiety':social,'BirthSeason':birth_season,'BirthDay':birth_day,'HomeRegion':'Other','CanBeRomanced':False,'CanVisitIsland':'FALSE','IntroductionsQuest':False,'PerfectionScore':False,'Home':[{'Id':'Home','Location':loc(home),'Tile':{'X':hx,'Y':12 if home!='ResearchStation' else 14},'Direction':'down'}]}
 for target,source in [('Characters','characters'),('Portraits','portraits')]:patch('Load',target+'/'+id,FromFile=f'assets/{source}/{name}.png')
 lines={}
 keys=['Mon','Tue','Wed','Thu','Fri','Sat','Sun','Mon2','Tue2','Wed2','Thu2','Fri2','Sat2','Sun2','Mon4','Tue4','Wed4','Thu4','Fri4','Sat4']
 for key,(en,zh) in zip(keys,line_sets[name]):lines[key]=tr('dialogue.'+name+'.'+key,en,zh)
 lines['Introduction']=tr('dialogue.'+name+'.intro',f'I am {name}. Welcome to Lumenhaven.','我是'+cn+'。欢迎来到栖光湾。')
 lines['Rainy_Day_0']=tr('dialogue.'+name+'.rain','Come inside. Work can wait until the weather settles.','进来吧，等天气平稳了再忙。')
 lines['winter_Mon']=tr('dialogue.'+name+'.winter','The snow makes the harbor quiet. The sea is still working.','雪让港口安静下来，海面却一直在动。')
 # Load reads raw JSON; only patch Entries resolve Content Patcher i18n tokens.
 patch('Load','Characters/Dialogue/'+id,FromFile='assets/data/'+name+'_dialogue.json');write(Path('assets/data/'+name+'_dialogue.json'),{})
 patch('EditData','Characters/Dialogue/'+id,Entries=lines)
 if name=='Ada': schedule=f'600 {loc(home)} {hx} 12 2/800 {loc("Harbor")} 20 25 2/1200 {loc("Fishery")} 9 10 2/1600 {loc("Town")} 35 24 2/1900 {loc(home)} {hx} 12 2'
 elif name=='Mira':schedule=f'600 {loc(home)} {hx} 12 2/800 {loc("Town")} 27 10 2/1100 {loc("Tundra")} 29 34 2/1500 {loc("Town")} 24 26 2/1900 {loc(home)} {hx} 12 2'
 elif name=='Roan':schedule=f'600 {loc(home)} {hx} 12 2/800 {loc("Harbor")} 21 32 2/1300 {loc("Harbor")} 22 25 2/1700 {loc("Town")} 30 24 2/2000 {loc(home)} {hx} 12 2'
 elif name=='Nora':schedule=f'600 {loc(home)} {hx} 12 2/800 {loc("Harbor")} 24 23 2/1000 {loc("Airstrip")} 34 27 2/1500 {loc("Harbor")} 24 23 2/1900 {loc(home)} {hx} 12 2'
 elif name=='Levin':schedule=f'600 {loc(home)} {hx} 14 2/800 {loc("Tundra")} 29 43 2/1200 {loc("WinterCamp")} 19 37 2/1700 {loc(home)} {hx} 12 2/2100 {loc(home)} {hx} 14 2'
 else:schedule=f'600 {loc(home)} {hx} 12 2/900 {loc("WinterCamp")} 49 23 2/1200 {loc("SledTrail")} 25 24 2/1600 {loc("Town")} 36 23 2/1900 {loc(home)} {hx} 12 2'
 if name in ['Nora','Levin','Amma']:
  winter_camp={'Nora':(31,25),'Levin':(19,37),'Amma':(49,23)}[name]
  winter=f'600 {loc(home)} {hx} {14 if home=="ResearchStation" else 12} 2/900 {loc("WinterCamp")} {winter_camp[0]} {winter_camp[1]} 2/1300 {loc("Harbor")} 24 23 2/1700 {loc(home)} {hx} {14 if home=="ResearchStation" else 12} 2'
  rain=f'600 {loc(home)} {hx} {14 if home=="ResearchStation" else 12} 2/1000 {loc(home)} {hx} 10 2/1700 {loc(home)} {hx} 12 2'
 else:
  winter=f'600 {loc(home)} {hx} 12 2/900 {loc("Town")} {24+index*3} 24 2/1300 {loc("Harbor")} {20+index*2} 23 2/1700 {loc(home)} {hx} 12 2'
  rain=f'600 {loc(home)} {hx} 12 2/1000 {loc(home)} {hx} 10 2/1700 {loc(home)} {hx} 12 2'
 write(Path('assets/data/'+name+'_schedule.json'),{'spring':schedule,'summer':schedule,'fall':schedule,'winter':winter,'rain':rain,'rain2':rain});patch('Load','Characters/schedules/'+id,FromFile='assets/data/'+name+'_schedule.json')
 gift_items={
  'Ada':(obj('PanCod'),'ArcticPassage_Capelin ArcticPassage_NorthernShrimp 334','92','168 169 170 171 172'),
  'Mira':(obj('FishPotatoStew'),'ArcticPassage_ArcticChar ArcticPassage_SnowCrab 395','92','168 169 170 171 172'),
  'Roan':(obj('ShrimpChowder'),'ArcticPassage_AtlanticCod ArcticPassage_PolarCod 388','92','168 169 170 171 172'),
  'Nora':(obj('FishPotatoStew'),'ArcticPassage_PolarCod ArcticPassage_Capelin 395','92','168 169 170 171 172'),
  'Levin':(obj('CharSoup'),'ArcticPassage_ArcticChar 422 74','92','168 169 170 171 172'),
  'Amma':(obj('ShrimpChowder'),'ArcticPassage_SnowCrab ArcticPassage_Capelin 216','92','168 169 170 171 172')}
 loved,liked,disliked,hated=gift_items[name]
 gifts[id]=tr('gift.'+name+'.love','That is very thoughtful. Thank you!','真用心，谢谢你！')+'/'+loved+'/'+tr('gift.'+name+'.like','I can make good use of this.','这个用得上。')+'/'+liked+'/'+tr('gift.'+name+'.dislike','I do not have much use for this.','我不太用得上这个。')+'/'+disliked+'/'+tr('gift.'+name+'.hate','Please keep that away from the workbench.','别把这个放在工作台边。')+'/'+hated+'/'+tr('gift.'+name+'.neutral','Thank you for thinking of me.','谢谢你惦记着我。')+'//'
patch('EditData','Data/Characters',Entries=characters);patch('EditData','Data/NPCGiftTastes',Entries=gifts)
from build_processing import build_processing
build_processing(ROOT,PACK,patch,tr,loc,obj,objects)
# Native journal chain: no cancellable main quests, rewards paid by the game's journal.
quests={}
def quest(id,kind,en,zh,desen,deszh,hinten,hintzh,requirements,nextid,reward,reaction=None):
 parts=[kind,tr('quest.'+id+'.title',en,zh),tr('quest.'+id+'.desc',desen,deszh),tr('quest.'+id+'.hint',hinten,hintzh),requirements,nextid,str(reward),'-1','false']
 if reaction:parts.append(reaction)
 quests[loc(id)]='/'.join(parts)
quest('Arrival','Location','A northern welcome','来自北方的邀请','Willy has arranged a place at the Lumenhaven guesthouse.','威利已替你联系好栖光湾旅舍。','Enter the red guesthouse west of the square.','进入广场西侧的红色旅舍。',loc('Guesthouse'),loc('FirstCatch_{{MapSeason}}'),150)
for season,key in [('spring','Capelin'),('summer','Capelin'),('fall','AtlanticCod'),('winter','PolarCod')]:
 en=next(f[1] for f in fishdefs if f[0]==key);zh=next(f[2] for f in fishdefs if f[0]==key)
 quest('FirstCatch_'+season,'ItemDelivery','The first shipment','今天的第一网',f'Ada needs three {en}. This order has no deadline.','艾达需要三条'+zh+'。订单没有期限。',f'Give Ada 3 {en} in a single stack.','手持同一堆叠的三条'+zh+'交给艾达。',loc('Ada')+' (O)'+obj(key)+' 3',loc('Shed'),400,tr('quest.catch.reply','Fresh and carefully packed. Let us fix the shed next.','新鲜，装箱也细致。接下来一起修好加工棚吧。'))
quest('Shed','ItemDelivery','The old processing shed','老旧的加工棚','Roan needs wood for the shed. He will finish the work overnight.','罗安需要木材维修加工棚，收齐后隔夜完工。','Give Roan 40 wood in one stack.','手持同一堆叠的40份木材交给罗安。',loc('Roan')+' (O)388 40',loc('BoatRepair'),250,tr('quest.shed.reply','Good boards. The shed will be ready in the morning.','好木料。明早加工棚就能用了。')+'#$action AddMail Current ArcticPassage_WoodDelivered received')
quest('BoatRepair','ItemDelivery','A route beyond the harbor','峡湾外的收获','Two iron bars will secure the old boat. The route opens the next morning.','用两块铁锭加固旧船，航线将在交货次日开放。','Give Roan 2 iron bars in one stack.','手持同一堆叠的两块铁锭交给罗安。',loc('Roan')+' (O)335 2',loc('FjordVisit'),300,tr('quest.boat.reply','I will finish the fittings tonight. Check the pier sign tomorrow.','今晚我来装好配件。明天看看码头上的航线牌。')+'#$action AddMail Current ArcticPassage_IronDelivered received')
quest('FjordVisit','Location','Among the icebergs','冰山之间','The repaired boat runs a fixed route to the observation landing.','修好的船只按固定航线往返观测码头。','Use the route sign at the east end of the harbor pier.','与渔港码头东端的航线牌互动。',loc('Icefjord'),loc('DeepCatch'),200)
quest('DeepCatch','ItemDelivery','The deep-water catch','深水的第一批货','Ada would like one Greenland halibut from the fjord. Fishing level 4 is required.','艾达想收一条峡湾深水区的格陵兰大比目鱼，需钓鱼等级4。','Give Ada one Greenland halibut.','将一条格陵兰大比目鱼交给艾达。',loc('Ada')+' (O)'+obj('Halibut')+' 1','-1',700,tr('quest.deep.reply','Our first shipment is complete. There will be more orders tomorrow.','第一批货齐了。明天，港口还会有新订单。'))
patch('EditData','Data/Quests',Entries=quests)
trigger_entries=[{'Id':loc('Invitation'),'Trigger':'DayStarted','Actions':['AddMail Current ArcticPassage_Invitation now']},{'Id':loc('Start'),'Trigger':'LocationChanged','Condition':'PLAYER_LOCATION_NAME Current '+loc('Town'),'Actions':['AddQuest '+loc('Arrival')]},{'Id':loc('RepairComplete'),'Trigger':'DayStarted','Condition':'PLAYER_HAS_MAIL Current ArcticPassage_WoodDelivered','Actions':['AddMail Current ArcticPassage_Shed received','AddMail Current ArcticPassage_Processing now']},{'Id':loc('BoatComplete'),'Trigger':'DayStarted','Condition':'PLAYER_HAS_MAIL Current ArcticPassage_IronDelivered','Actions':['AddMail Current ArcticPassage_Boat received','AddMail Current ArcticPassage_Route now']}]
# Data/TriggerActions is a LIST (not a dictionary). Fields merge through Entries keyed by Id.
patch('EditData','Data/TriggerActions',Entries={t['Id']:t for t in trigger_entries})
mail={'ArcticPassage_Invitation':tr('mail.invitation','Farmer,^A boat at the beach can take you north. Walk to the end of my long pier (29, 34). Bring your rod. Lumenhaven is a working harbor, and Ada could use a hand.^-Willy[#]A northern invitation','农夫：^栖光湾的朋友邀请你去北方看看。走到我店外长码头尽头（29,34），即可乘船。带上钓竿，艾达正好需要人帮忙。^-威利[#]来自北方的邀请'),'ArcticPassage_Processing':tr('mail.processing','The shed is ready.^Here is a Fish Smoker to get started. Ten coal will be delivered when you next arrive in the bay. It uses the normal recipe and professions.^-Roan %item bigobject FishSmoker %%[#]Processing shed ready','加工棚修好了。^先送你一台熏鱼机。使用原版熏制机制，别忘了带煤。^-罗安 %item bigobject FishSmoker %%[#]加工棚竣工'),'ArcticPassage_Route':tr('mail.route','The boat is ready.^Use the route post at the east end of the harbor pier. The return post is always available on the landing.^-Roan[#]Fjord route open','渔船已完成检查。^去渔港长码头东端查看航线牌。峡湾登岸处始终有返程牌。^-罗安[#]峡湾航线开放')}
patch('EditData','Data/mail',Entries=mail)
# Coal reward is a separate one-time trigger to avoid multiple mail attachments.
patch('EditData','Data/TriggerActions',Entries={loc('Coal'):{'Id':loc('Coal'),'Trigger':'LocationChanged','Condition':'PLAYER_HAS_MAIL Current ArcticPassage_Shed','Actions':['AddItem (O)382 10']}})
patch('EditMap','Maps/'+loc('Harbor'),MapTiles=[{'Position':{'X':43,'Y':24},'Layer':'Buildings','SetProperties':{'Action':'ArcticPassageFjordOutbound'}}],When={'HasFlag |contains=ArcticPassage_Boat':True})
patch('EditMap','Maps/'+loc('Icefjord'),MapTiles=[{'Position':{'X':8,'Y':28},'Layer':'Buildings','SetProperties':{'Action':'ArcticPassageFjordReturn'}}])
# The repaired workshop updates its existing inspection board.
patch('EditMap','Maps/'+loc('Harbor'),MapTiles=[{'Position':{'X':23,'Y':36},'Layer':'Buildings','SetProperties':{'Action':'Message ArcticPassage_WorkshopReady'}}],When={'HasFlag |contains=ArcticPassage_Shed':True})
# Native shop barter: submit fish by buying an order receipt, receive gold immediately.
# Stock limits reset by the game each day and survive reopening the same shop.
shops={};orders=[]
for season,base in [('spring','Capelin'),('summer','AtlanticCod'),('fall','AtlanticCod'),('winter','PolarCod')]:
 for typ,count,mult in [('Regular',3,1.4),('Restaurant',2,1.55),('Research',1,1.3)]:
  price=next(f[4] for f in fishdefs if f[0]==base);pay=round(price*count*mult);oid=obj(typ+'Receipt')
  objects[oid]={**objects[obj('Receipt')],'Name':typ+' receipt','DisplayName':tr('order.'+typ+'.name',typ+' order receipt',{'Regular':'普通订单收据','Restaurant':'餐馆订单收据','Research':'样本订单收据'}[typ]),'Description':tr('order.'+typ+'.desc','Trade the requested fish. Gold payment is added immediately; one delivery per day.','提交所需鱼类后，货款立即入账；每种订单每天限交一次。')}
  # Native per-player shop stock survives reopening but is lost across a process
  # reload in 1.6.15. A dated native mail flag is serialized with the farmer and
  # independently enforces the same limit after reload, without resetting on load.
  paid_flag=loc('Order_'+typ+'_{{Year}}_{{Season}}_{{Day}}')
  orders.append({'Id':season+'_'+typ,'ItemId':'(O)'+oid,'Condition':'SEASON '+season+', !PLAYER_HAS_MAIL Current '+paid_flag,'TradeItemId':'(O)'+obj(base),'TradeItemAmount':count,'Price':0,'AvailableStock':1,'AvailableStockLimit':'Player','ActionsOnPurchase':['AddMoney '+str(pay),'AddMail Current '+paid_flag+' received']})
shops[loc('Orders')]={'Owners':[{'Name':'AnyOrNone','Portrait':loc('Ada'),'Dialogues':[{'Id':'Instructions','Dialogue':tr('shop.orders','Trade fish for a receipt. Payment goes directly into your wallet. Three offers refresh each morning.','用鱼换取收据，货款直接入账。三种订单每天早晨更新。')}]}],'Items':orders}
shops[loc('Supplies')]={'Items':[{'Id':'Bait','ItemId':'(O)685','Price':5},{'Id':'TrainingRod','ItemId':'(T)TrainingRod','Price':25},{'Id':'Coal','ItemId':'(O)382','Price':150,'AvailableStock':10}]}
shops[loc('Market')]={'Owners':[{'Name':'AnyOrNone','Portrait':loc('Ada')}],'SalableItemTags':['category_fish','arcticpassage_fish_product'],'Items':[{'Id':'Bait','ItemId':'(O)685','Price':5}]}
from build_seafood import build_seafood
build_seafood(ROOT,PACK,patch,tr,loc,obj,objects,fish,locations,shops)
patch('EditData','Data/Shops',Entries=shops)
# Objects dictionary is serialized after order receipt entries have been added.
strings={
'TownGuide':tr('sign.town','LUMENHAVEN — Red house: guesthouse. Blue house: fishery. North: tundra. East: harbor. The return post is beside the east pier. The harbor supply counter sells four cooking recipes and imported staples; the guesthouse kitchen counter is shared.','栖光湾——红房子是旅舍，蓝房子是收购站。向北去苔原，向东去渔港。东侧栈桥旁有返程牌。港口补给柜台出售四份食谱及外运食材，旅舍料理台可共用。'),
'InnGuide':tr('sign.inn','Guesthouse entrance: the red front door. Beds are inside.','旅舍入口是红房子的正门，床铺在室内。'),
'BoatLocked':tr('sign.boat','Fjord route closed for repairs. Finish Roan\'s wood and iron-bar requests; the boat reopens the next morning.','峡湾航线正在检修。完成罗安的木材、铁锭委托后，交货次日开放。'),
'Fishing':tr('sign.fishing','Safe fishing from the piers. Spring: capelin and polar cod. Summer and fall: Atlantic cod. Winter: polar cod; cast west from the upper pier into dark open water. Wolffish prefer the northern rocky inlet outside winter. Harbor pots: northern shrimp in spring, summer and fall. Fjord pots: snow crab in fall. In winter use harbor pots for snow crab; the fjord landing is icebound. Bait, leave overnight, and collect from shore.','安全钓点在木栈桥。春季有毛鳞鱼、北极鳕；夏秋有大西洋鳕鱼；冬季有北极鳕，请从上段栈桥朝西侧深色开水面投竿，避开岸冰。非冬季的北侧岩岸水湾可遇到狼鱼。港口蟹笼春夏秋捕虾；秋季到峡湾捕雪蟹，冬季改在港口下笼，峡湾岸冰边不宜操作。装饵过夜，从岸上收取。'),
'Workshop':tr('sign.workshop','Processing shed: ask Roan about repairing it. Wood first, then two iron bars for the boat.','加工棚：找罗安商量维修。先交木材，再用两块铁锭修船。'),
'WorkshopReady':tr('sign.ready','The shed is ready. Roan sent a Fish Smoker and a drying-rack plan. Smoking is quick and needs coal; drying takes two nights without fuel.','加工棚已完工，罗安寄来了熏鱼机和晾鱼架图纸。熏制快、要用煤；风干慢，要等两个夜晚，不耗燃料。'),
'DeepWater':tr('sign.deep','Deep-water observation pier. Greenland halibut: all seasons, fishing level 4+. Golden redfish: summer and fall, fishing level 2+. In winter cast south from the viewing platform into dark open water. Icebergs and shore ice cannot be walked on.','深水观测栈桥。格陵兰大比目鱼全年出现，需要钓鱼等级4。金红鱼在夏秋出现，需要钓鱼等级2。冬季请从观测台朝南侧深色开水面投竿。冰山与岸冰均不可步行接近。'),
'WhaleNote':tr('sign.whale','The lookout faces the open fjord. Dark water and the blue edges of distant ice fill the view.','从这里可以静静眺望峡湾。墨色的海水延伸到远处，浮冰的边缘透着清蓝。'),
'TundraGuide':tr('sign.tundra','Low shrubs, stones and meltwater. The stream supports Arctic char in summer and fall. South: town. Cross the eastern wooden bridge to reach the field camp and research shelter.','低矮灌丛、碎石与融水溪流。夏秋可在溪中钓北极红点鲑。南侧回小镇；向东走过木桥，通往营地和研究站。'),
'CampRoute':tr('sign.camp.route','Field camp. West: tundra bridge, then south to Frosthavn. The red research hut has a bed on the left. The marked route stays open throughout the year.','苔原营地。向西回木桥，再向南回霜灯港。红色研究站左侧有床，全年沿标记路线往返。'),
'SnowShelter':tr('sign.camp.snow','These are seasonal demonstration shelters: snow houses in winter, canvas tents during the other seasons. The red hut is the overnight shelter; the domes are for viewing from the marked path.','这里是季节性庇护所展示区：冬季为雪屋，其余季节搭设帆布帐篷。请沿小路观察；实际住宿在红色研究站，雪屋暂不开放进入。'),
'CampDesk':tr('sign.camp.desk','Field research shelter. The bed to the left uses normal overnight saving. Return through the south door, walk west to the bridge, then south to town. K opens your route book and field notes.','营地研究站。左侧床铺可正常过夜并保存。南门离开后向西回木桥，再向南回镇区。按 K 查看路线和自然笔记。'),
'Char':tr('sign.char','Fresh-water channel. Cast from the bridge for Arctic char in summer and fall.','淡水溪流，夏秋可从桥边垂钓北极红点鲑。'),
'Safety':tr('sign.safety','North winds can erase old tracks. Follow the shore markers home, and keep clear of newly formed sea ice.','北风会掩盖旧脚印。请沿岸边标记返回，不要独自走上新结的海冰。'),
'Lodging':tr('sign.lodging','The guesthouse is warm. Your room is on the left. If you plan to sail home, the return post by the town pier is always there.','炉火还温着，房间在左侧。如果打算返航，镇东侧码头的返程牌一直为你留着。')}
patch('EditData','Strings/StringsFromMaps',Entries={'ArcticPassage_'+k:v for k,v in strings.items()})
# Brief native arrival scene. Its start/skip does not carry any progression or item rewards.
intro1=tr('event.arrival1','Welcome to Lumenhaven. We have a room for you in the red house.','欢迎来到栖光湾。红房子里替你留了房间。')
intro2=tr('event.arrival2','Bring your rod to the harbor. A few well-kept fish will get our first shipment started.','带上钓竿来港口吧。几条保存得当的鱼，就能开始我们的第一批货。')
write(Path('assets/data/Town_events.json'),{})
patch('Load','Data/Events/'+loc('Town'),FromFile='assets/data/Town_events.json')
patch('EditData','Data/Events/'+loc('Town'),Entries={loc('Welcome'):'continue/24 24/farmer 24 24 2 '+loc('Ada')+' 25 24 3/pause 400/speak '+loc('Ada')+' "'+intro1+'"/speak '+loc('Ada')+' "'+intro2+'"/end'})
# Each added resident has a native, friendship-gated personal scene at a place
# tied to their work. The game's event ledger persists completion in the save.
personal_events={
 'Fishery':('Ada','ArcticPassage_AdaColdChain','900 1500',
   'The ledger says the first crate stayed cold from pier to counter. That small detail is how a harbor earns trust.',
   '账本记着，第一箱鱼从栈桥到柜台都保持了低温。港口能不能让人放心，就看这些小事。',
   'You kept the label facing out and the drain clear. I will put your name beside this morning’s careful work.',
   '你把标签朝外贴好，也留出了排水口。我会在今天的记录旁写下你的名字。',
   '12 14/farmer 12 14 2 '+loc('Ada')+' 14 14 3'),
 'Tundra':('Mira','ArcticPassage_MiraTrailSigns','900 1600',
   'The tracks cross the marked path and disappear among the stones. We can learn from them without following or feeding the animal.',
   '足迹横过标好的小路，消失在石缝之间。不追赶、不投喂，我们也能从中学到很多。',
   'You left the stones where they were. That is good field practice; the next thaw may tell us more.',
   '你没有挪动那些石头。这才是合适的野外观察；等下次融雪，也许还会有新发现。',
   '28 34/farmer 28 34 2 '+loc('Mira')+' 29 34 3'),
 'Harbor':('Roan','ArcticPassage_RoanSignalLamp','900 1700',
   'The harbor lamp was loose in its bracket. I tightened it before dusk; a small light matters when the landing is hard to see.',
   '港口的灯在支架里松了。我赶在天黑前把它拧紧；岸线看不清时，这一点灯光很重要。',
   'You held the ladder steady and kept the pier clear. That is good repair work, even without a wrench in your hand.',
   '你扶稳了梯子，也把栈桥通道留了出来。即使手里没有扳手，这也是在帮忙修理。',
   '22 24/farmer 22 25 2 '+loc('Roan')+' 20 25 3'),
 'Airstrip':('Nora','ArcticPassage_NoraWindCheck','900 1700',
   'The wind sock has gone still, but I still check the ice haze before clearing a flight. A safe return is part of every departure.',
   '风向袋停下来了，我还是要再看一遍海冰上方的雾霭，才能放行。每次出发，都得先想好怎么安全回来。',
   'You noticed the thin line of open water on my chart. Good eyes. I will mark it before the evening report.',
   '你注意到了图上那条细细的开水带。眼力不错，我会在晚间报告前把它标清楚。',
   '32 27/farmer 32 28 2 '+loc('Nora')+' 34 27 3'),
 'ResearchStation':('Levin','ArcticPassage_LevinFieldNotes','1000 1800',
   'I drew the ice edge from solid ground and marked where the view was uncertain. A careful record should leave room for what we do not know.',
   '我站在稳固的岸上描下冰缘，也标出了看不准的地方。严谨的记录，要给未知留出位置。',
   'You spotted the same ridge in the meltwater sketch. I will add your observation to the field notes, with your name beside it.',
   '你在融水草图里也认出了同一道脊线。我会把你的观察添进野外记录，并写上你的名字。',
   '14 8/farmer 15 8 2 '+loc('Levin')+' 17 8 3'),
 'WinterCamp':('Amma','ArcticPassage_AmmaTeamCheck','900 1700',
   'Before a run, I check each paw, buckle and line. The team sets the pace; if one dog is tired, we all turn back.',
   '出发前，我会逐只检查爪子、扣环和牵引绳。队伍决定步速；只要有一只累了，我们就一起返程。',
   'You held the loose line clear of the path. Thank you. Everyone gets water and a quiet rest before we go out again.',
   '你把松开的牵引绳收到了路边。谢谢。再出发以前，大家都要先喝水、安静休息。',
   '18 36/farmer 18 37 2 '+loc('Amma')+' 20 37 3')}
for area,(name,event_id,time_range,line1_en,line1_zh,line2_en,line2_zh,actors) in personal_events.items():
 event_file='assets/data/'+area+'_events.json'
 write(Path(event_file),{})
 patch('Load','Data/Events/'+loc(area),FromFile=event_file)
 first=tr('event.'+name+'.personal.1',line1_en,line1_zh)
 second=tr('event.'+name+'.personal.2',line2_en,line2_zh)
 key=f'{event_id}/f {loc(name)} 500/t {time_range}'
 if name=='Nora':key+='/w sunny'
 script='continue/'+actors+'/pause 350/speak '+loc(name)+' "'+first+'"/pause 250/speak '+loc(name)+' "'+second+'"/end'
 if area=='Harbor':harbor_personal_event=(key,script)
 else:
  patch('Load','Data/Events/'+loc(area),FromFile=event_file)
  patch('EditData','Data/Events/'+loc(area),Entries={key:script})
write(Path('content.json'),{'Format':'2.4.0','DynamicTokens':[{'Name':'MapSeason','Value':'spring'}]+[{'Name':'MapSeason','Value':season,'When':{'Season':season}} for season in ['spring','summer','fall','winter']]+[{'Name':'HarborTrapType','Value':'shrimp'},{'Name':'HarborTrapType','Value':'crab','When':{'Season':'winter'}}],'Changes':changes})
write(Path('i18n/default.json'),EN);write(Path('i18n/zh.json'),ZH)
# Compact machine-readable design data and navigation anchors for independent validation.
(ROOT/'docs/build-index.json').write_text(json.dumps({'maps':{n:{'size':[m.w,m.h],'points':m.points} for (n,s),m in MAPS.items() if s=='summer'},'fish':[{'id':obj(f[0]),'difficulty':f[3],'price':f[4],'seasons':f[8]} for f in fishdefs]},indent=2))
print(f'Built {len(MAPS)} TMX maps, {len(objects)} objects, {len(quests)} quests, {len(characters)} residents and {len(changes)} patches.')
from build_air_travel import main as build_air_travel
build_air_travel()
from build_harbor_facilities import main as build_harbor_facilities
build_harbor_facilities()
from build_frontier import main as build_frontier
build_frontier()
from build_weekly_orders import main as build_weekly_orders
build_weekly_orders()
from build_ice_fishing import main as build_ice_fishing
build_ice_fishing()
from build_sled_travel import main as build_sled_travel
build_sled_travel()
from build_snow_shelter import main as build_snow_shelter
build_snow_shelter()
from build_daily_orders import main as build_daily_orders
build_daily_orders()
# The harbor facility builder registers the custom event asset. Append Roan's
# personal scene only after that Load patch so the empty base cannot replace it.
content=json.loads((PACK/'content.json').read_text())
content['Changes'].append({'Action':'EditData','Target':'Data/Events/'+loc('Harbor'),
 'LogName':'Resident personal event: Roan signal lamp','Entries':{harbor_personal_event[0]:harbor_personal_event[1]}})
(PACK/'content.json').write_text(json.dumps(content,ensure_ascii=False,indent=2)+'\n')
from build_research import main as build_research
build_research()
from build_secrets import main as build_secrets
build_secrets()
from build_festivals import main as build_festivals
build_festivals()
from build_story_extension import main as build_story_extension
build_story_extension()
