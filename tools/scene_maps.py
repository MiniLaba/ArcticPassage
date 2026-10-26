"""Export composed environment art as real xTile tiles with authored walk/water masks.
The retained master is never changed. Cropping/scaling here only normalizes game texture format.
"""
from pathlib import Path
from PIL import Image, ImageDraw
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]

def clear_water_pixel_majority(image,x,y):
 # Only assign fishing water where most sample points visibly show open water.
 # Blue paint on buildings is excluded separately by the authored shore region.
 pixels=[image.getpixel((x*16+dx,y*16+dy))[:3] for dx in [3,7,11,14] for dy in [3,7,11,14]]
 return sum(r<85 and g>r*1.2 and b>r*1.4 and b>g*.95 for r,g,b in pixels)>=8

def configure_scene(m):
 if m.name in ['WinterCamp','ResearchStation']:
  from camp_maps import configure_camp
  configure_camp(m);return
 if m.name in ['Guesthouse','Fishery']:
  configure_interior(m);return
 if m.name in ['Icefjord','Tundra']:
  configure_wild(m);return
 if m.name=='Harbor':
  configure_harbor(m);return
 if m.name!='Town':return
 master=ROOT/f'art/source/town-{m.season}-master.png'
 if not master.exists():master=ROOT/'art/source/town-spring-master.png'
 if not master.exists():return
 m.scene_image=Image.open(master).convert('RGBA').resize((m.w*16,m.h*16),Image.Resampling.NEAREST)
 m.scene_file=f'Town_{m.season}_scene.png';m.scene_image.save(ROOT/'ContentPack/assets/maps'/m.scene_file)
 m.layers={n:[[0]*m.w for _ in range(m.h)] for n in m.layers};m.over={};m.warps=[]
 mask=Image.new('L',(m.w,m.h));d=ImageDraw.Draw(mask)
 d.polygon([(25,0),(28,0),(29,5),(28,10),(26,14),(26,20),(25,24),(25,29),(25,35),(25,39),(26,42),(31,47),(27,47),(23,43),(22,39),(22,34),(22,29),(22,25),(23,20),(24,14),(26,10),(27,5)],fill=255)
 # Doorstep aprons and the waterfront lane are deliberately broader than one tile.
 for box in [(17,22,26,24),(25,23,41,24),(40,22,57,24),(18,9,27,10),(27,10,34,11),(15,38,24,40),(24,39,33,41),(32,24,34,30)]:d.rectangle(box,fill=255)
 for x,y in [(18,22),(33,22),(20,9),(33,10),(16,38),(32,39)]:d.rectangle((x,y,x+1,y+1),fill=255)
 m.scene_walk={(x,y) for y in range(m.h) for x in range(m.w) if mask.getpixel((x,y))}
 # The shoreline is authored separately from collision, preserving native fishing water.
 edge=[45]*8+[47]*5+[45]*5+[43]*4+[41]*4+[45]*5+[46]*5+[43]*5+[50]*7
 m.scene_water={(x,y) for y in range(m.h) for x in range(m.w) if x>=edge[min(y,len(edge)-1)] and (x,y) not in m.scene_walk and clear_water_pixel_majority(m.scene_image,x,y)}
 for y in range(m.h):
  for x in range(m.w):
   m.tile('water' if (x,y) in m.scene_water else 'ground',x,y)
   if (x,y) not in m.scene_walk and (x,y) not in m.scene_water:m.tile('collision',x,y,'Buildings')
 m.action('collision',18,21,'Warp 12 14 ArcticPassage_Guesthouse')
 m.action('collision',33,21,'Warp 12 14 ArcticPassage_Fishery')
 m.action('sign',40,24,'Warp 28 33 Beach')
 # Keep both waterfront-lane rows clear; the guide stands beside the lane.
 m.action('sign',25,25,'Message ArcticPassage_TownGuide')
 m.action('collision',22,21,'Message ArcticPassage_InnGuide')
 for y in [22,23]:m.warp(57,y,'Harbor',24,23)
 for x in [26,27]:m.warp(x,0,'Tundra',29,43)
 attach_iceberg(m,(45,15))
 m.points={'spawn':[36,23],'inn_door_approach':[18,22],'fishery_door_approach':[33,22],'harbor_departure':[56,23]}
 # Keep an honest developer overlay to inspect art against traversability.
 debug=m.scene_image.copy();dd=ImageDraw.Draw(debug,'RGBA')
 for x,y in m.scene_walk:dd.rectangle((x*16,y*16,x*16+15,y*16+15),fill=(60,240,140,85))
 debug.save(ROOT/f'previews/Town_{m.season}_navigation.png')

def append_scene(root,m,nextid):
 if not hasattr(m,'scene_image'):return
 first=nextid+1;m.scene_first=first
 ts=ET.SubElement(root,'tileset',firstgid=str(first),name='z_'+m.name+'Scene',tilewidth='16',tileheight='16',tilecount=str(m.w*m.h),columns=str(m.w))
 ET.SubElement(ts,'image',source=m.scene_file,width=str(m.w*16),height=str(m.h*16))
 for y in range(m.h):
  for x in range(m.w):
   wood=(x,y) in getattr(m,'scene_wood',set()) or (m.name=='Town' and x>=40 and 22<=y<=24)
   # In the native 1.6 engine, Grass + winter selects snowyStep (there is no
   # Snow tile type). Only apply it to outdoor snow-covered walking ground.
   snow=m.season=='winter' and 'Outdoors' in m.properties and (x,y) in m.scene_walk
   index=y*m.w+x;p={'NoSpawn':'All','Type':'Wood' if wood else 'Grass' if snow else 'Stone'}
   p.update(m.over.get(('Back',x,y),{}))
   if (x,y) in m.scene_water:p.update(Water='I',Passable='T')
   t=ET.SubElement(ts,'tile',id=str(index));pp=ET.SubElement(t,'properties')
   for k,v in p.items():ET.SubElement(pp,'property',name=k,value=v)
   m.layers['Back'][y][x]=first+index
 # Roof and upper facade occlusion follows artwork; bases are separately blocked.
 for x1,y1,x2,y2 in getattr(m,'scene_roofs',[(12,12,23,19),(27,14,37,19),(15,1,24,7),(29,2,36,8),(11,30,21,35),(29,31,37,36)]):
  for y in range(y1,y2+1):
   for x in range(x1,x2+1):m.layers['Front'][y][x]=first+y*m.w+x
 if hasattr(m,'scene_berg'):
  im=m.scene_berg;ox,oy=m.scene_berg_origin;cols=im.width//16;rows=im.height//16;gid=first+m.w*m.h
  ts=ET.SubElement(root,'tileset',firstgid=str(gid),name='z_NearIceberg',tilewidth='16',tileheight='16',tilecount=str(cols*rows),columns=str(cols))
  ET.SubElement(ts,'image',source='NearIceberg.png',width=str(im.width),height=str(im.height))
  m.scene_detail_tiles={}
  for y in range(rows):
   for x in range(cols):
    tile=im.crop((x*16,y*16,(x+1)*16,(y+1)*16))
    if not tile.getbbox():continue
    index=gid+y*cols+x;m.scene_detail_tiles[index]=tile
    if 0<=ox+x<m.w and 0<=oy+y<m.h:m.layers['Front'][oy+y][ox+x]=index

def attach_iceberg(m,origin):
 """A real foreground tile asset keeps ice visible from the playable camera."""
 source=ROOT/'art/source/near-iceberg-master.png'
 if not source.exists():return
 m.scene_berg=Image.open(source).convert('RGBA').resize((192,112),Image.Resampling.NEAREST)
 m.scene_berg.save(ROOT/'ContentPack/assets/maps/NearIceberg.png');m.scene_berg_origin=origin
 ox,oy=origin
 for y in range(7):
  for x in range(12):
   alpha=list(m.scene_berg.getchannel('A').crop((x*16,y*16,(x+1)*16,(y+1)*16)).getdata())
   if sum(a>160 for a in alpha)>=80:
    m.scene_water.discard((ox+x,oy+y));m.tile('collision',ox+x,oy+y,'Buildings')


def configure_harbor(m):
 master=ROOT/f'art/source/harbor-{m.season}-master.png'
 if not master.exists():master=ROOT/'art/source/harbor-spring-master.png'
 if not master.exists():return
 m.scene_image=Image.open(master).convert('RGBA').resize((m.w*16,m.h*16),Image.Resampling.NEAREST)
 m.scene_file=f'Harbor_{m.season}_scene.png';m.scene_image.save(ROOT/'ContentPack/assets/maps'/m.scene_file)
 m.layers={n:[[0]*m.w for _ in range(m.h)] for n in m.layers};m.over={};m.warps=[]
 mask=Image.new('L',(m.w,m.h));d=ImageDraw.Draw(mask)
 # Work lane, transverse quay, and connected upper/lower berths.
 d.polygon([(19,0),(21,0),(23,7),(23,14),(22,19),(22,26),(23,32),(22,37),(20,37),(20,31),(19,25),(20,18),(21,13),(21,7)],fill=255)
 for box in [(0,22,53,24),(24,11,44,12),(36,12,37,22),(34,24,36,36),(24,36,37,37),(11,15,22,16),(10,36,22,37)]:d.rectangle(box,fill=255)
 d.rectangle((51,21,52,22),fill=0)
 m.scene_walk={(x,y) for y in range(m.h) for x in range(m.w) if mask.getpixel((x,y))}
 edge=[39]*9+[25]*13+[24]*3+[28]*10+[25]*4+[34]*9
 m.scene_water={(x,y) for y in range(m.h) for x in range(m.w) if x>=edge[min(y,len(edge)-1)] and (x,y) not in m.scene_walk and clear_water_pixel_majority(m.scene_image,x,y)}
 m.scene_wood={(x,y) for x,y in m.scene_walk if (y in range(22,25) and not 19<=x<=22) or (x>=24 and y>=10)}
 for y in range(m.h):
  for x in range(m.w):
   m.tile('water' if (x,y) in m.scene_water else 'ground',x,y)
   if (x,y) not in m.scene_walk and (x,y) not in m.scene_water:m.tile('collision',x,y,'Buildings')
 m.action('collision',8,21,'OpenShop ArcticPassage_Orders')
 m.action('collision',16,21,'OpenShop ArcticPassage_Supplies')
 m.action('sign',43,24,'Message ArcticPassage_BoatLocked')
 m.action('sign',32,10,'Message ArcticPassage_Fishing')
 m.action('sign',23,36,'Message ArcticPassage_Workshop')
 for y in [22,23]:m.warp(0,y,'Town',54,23)
 m.points={'spawn':[24,23],'fishing':[37,20],'boat':[43,23]}
 m.scene_roofs=[(5,4,19,11),(6,24,19,33)]
 debug=m.scene_image.copy();dd=ImageDraw.Draw(debug,'RGBA')
 for x,y in m.scene_walk:dd.rectangle((x*16,y*16,x*16+15,y*16+15),fill=(60,240,140,85))
 debug.save(ROOT/f'previews/Harbor_{m.season}_navigation.png')

def configure_wild(m):
 """The shore and paths are authored against retained original scene landmarks."""
 key=m.name.lower();master=ROOT/f'art/source/{key}-{m.season}-master.png'
 if not master.exists():master=ROOT/f'art/source/{key}-spring-master.png'
 if not master.exists():return
 m.scene_image=Image.open(master).convert('RGBA').resize((m.w*16,m.h*16),Image.Resampling.NEAREST)
 m.scene_file=f'{m.name}_{m.season}_scene.png';m.scene_image.save(ROOT/'ContentPack/assets/maps'/m.scene_file)
 m.layers={n:[[0]*m.w for _ in range(m.h)] for n in m.layers};m.over={};m.warps=[];m.scene_roofs=[]
 mask=Image.new('L',(m.w,m.h));d=ImageDraw.Draw(mask)
 if m.name=='Icefjord':
  # Broad landing and observation platform, with a worn loop on the headland.
  d.line([(23,55),(22,51),(21,48),(19,46),(15,45),(10,43),(7,42),(5,40),(4,38),(5,35),(6,33),(5,31),(3,29),(3,27),(5,25),(8,23),(11,23),(13,25),(12,27),(10,29)],fill=255,width=2)
  for box in [(9,25,10,28),(9,28,11,41),(8,29,11,30),(11,33,40,34),(33,31,39,34),(9,21,11,23)]:d.rectangle(box,fill=255)
  wood={(x,y) for y in range(m.h) for x in range(m.w) if (9<=x<=11 and 25<=y<=41) or (11<=x<=40 and 33<=y<=34) or (33<=x<=39 and 31<=y<=34)}
 else:
  # Trail follows the natural gravel line; the bridge is the only river crossing.
  d.line([(28,47),(29,45),(31,42),(31,40),(30,38),(29,36),(28,34),(27,32),(26,29),(26,27),(26,25),(27,23),(28,21),(29,18),(29,15),(28,12),(27,10),(26,8),(25,5)],fill=255,width=3)
  d.rectangle((24,3,28,5),fill=255)
  d.rectangle((29,42,30,46),fill=255)
  d.rectangle((29,23,53,24),fill=255)
  d.rectangle((50,22,54,24),fill=255)
  # A small open gravel apron beside Mira's research kit.
  d.rectangle((25,30,29,34),fill=255)
  wood={(x,y) for x in range(30,49) for y in range(23,25)}|{(x,y) for x in range(25,29) for y in range(3,6)}
 m.scene_walk={(x,y) for y in range(m.h) for x in range(m.w) if mask.getpixel((x,y))}
 m.scene_wood=wood
 ice=Image.new('L',(m.w,m.h));ice_draw=ImageDraw.Draw(ice)
 if m.name=='Icefjord':
  # Cyan ice faces can resemble water to a color sampler. Exclude the authored
  # berg silhouettes so native bobbers never land inside a painted ice wall.
  for outline in [
   [(0,0),(15,0),(30,10),(30,12),(20,12),(2,6)],
   [(38,3),(50,2),(71,8),(71,20),(66,21),(60,19),(54,16),(48,15),(39,10)],
   [(57,35),(69,38),(71,43),(71,47),(64,48),(59,43)]
  ]:ice_draw.polygon(outline,fill=255)
 # Color sampling is conservative: ice/rocks/wood never become fishing water.
 m.scene_water={(x,y) for y in range(m.h) for x in range(m.w) if (x,y) not in m.scene_walk and not ice.getpixel((x,y)) and clear_water_pixel_majority(m.scene_image,x,y)}
 for y in range(m.h):
  for x in range(m.w):
   m.tile('water' if (x,y) in m.scene_water else 'ground',x,y)
   if (x,y) not in m.scene_walk and (x,y) not in m.scene_water:m.tile('collision',x,y,'Buildings')
 if m.name=='Icefjord':
  attach_iceberg(m,(42,27))
  # Use the notice already painted in the original, without overlaying a second sign.
  m.action('collision',8,28,'ArcticPassageFjordReturn')
  m.action('collision',35,30,'Message ArcticPassage_DeepWater')
  m.action('collision',9,21,'Message ArcticPassage_WhaleNote')
  m.points={'spawn':[35,34],'fishing':[39,34],'return_approach':[9,29]}
 else:
  m.action('collision',28,38,'Message ArcticPassage_TundraGuide')
  m.action('collision',52,21,'Message ArcticPassage_Char')
  m.action('collision',24,2,'Message ArcticPassage_Safety')
  for x in [29,30]:m.warp(x,46,'Town',27,2)
  for y in [23,24]:m.warp(54,y,'WinterCamp',2,24)
  m.points={'spawn':[29,43],'fishing':[41,23],'lookout':[25,4]}
 debug=m.scene_image.convert('RGB');dd=ImageDraw.Draw(debug,'RGBA')
 for x,y in m.scene_water:dd.rectangle((x*16,y*16,x*16+15,y*16+15),fill=(40,120,255,65))
 for x,y in m.scene_walk:dd.rectangle((x*16,y*16,x*16+15,y*16+15),fill=(60,240,140,95))
 debug.save(ROOT/f'previews/{m.name}_{m.season}_navigation.png')

def configure_interior(m):
 master=ROOT/f'art/source/{m.name.lower()}-interior-master.png'
 if not master.exists():return
 # Native custom interiors otherwise receive a purple default light mask.
 # Keep the authored amber lighting; a small night mask preserves the lamps.
 m.properties.update(AmbientLight='0 0 0',AmbientNightLight='24 18 10')
 m.scene_image=Image.open(master).convert('RGBA').resize((m.w*16,m.h*16),Image.Resampling.NEAREST)
 m.scene_file=f'{m.name}_{m.season}_scene.png';m.scene_image.save(ROOT/'ContentPack/assets/maps'/m.scene_file)
 m.layers={n:[[0]*m.w for _ in range(m.h)] for n in m.layers};m.over={};m.warps=[];m.scene_roofs=[]
 mask=Image.new('L',(m.w,m.h));d=ImageDraw.Draw(mask)
 d.rectangle((2,4,21,15),fill=255);d.rectangle((10,15,13,17),fill=255)
 if m.name=='Guesthouse':
  for box in [(2,3,6,8),(8,5,11,8),(12,3,15,5),(17,4,21,7),(18,8,19,8),(1,10,5,13)]:d.rectangle(box,fill=0)
  d.rectangle((3,6,5,8),fill=255)
 else:
  for box in [(2,4,4,8),(7,4,16,6),(9,7,13,9),(17,5,21,9),(1,10,4,14),(18,12,21,15)]:d.rectangle(box,fill=0)
 m.scene_walk={(x,y) for y in range(m.h) for x in range(m.w) if mask.getpixel((x,y))};m.scene_water=set()
 m.scene_wood=set(m.scene_walk) if m.name=='Guesthouse' else set()
 for y in range(m.h):
  for x in range(m.w):
   m.tile('floor',x,y)
   if (x,y) not in m.scene_walk:m.tile('collision',x,y,'Buildings')
 if m.name=='Guesthouse':
  for x in [3,4,5]:
   m.prop(x,7,'Bed','T','Back');m.prop(x,7,'TouchAction','Sleep','Back')
  m.action('collision',17,7,'Message ArcticPassage_Lodging');m.warp(12,17,'Town',18,23)
  m.action('collision',20,7,'Kitchen')
  m.points={'spawn':[12,14],'bed_approach':[4,9]}
 else:
  m.action('collision',8,6,'OpenShop ArcticPassage_Market')
  m.action('collision',15,6,'OpenShop ArcticPassage_Orders');m.warp(12,17,'Town',33,23)
  m.points={'spawn':[12,14],'counter_approach':[8,7]}
 debug=m.scene_image.convert('RGB');dd=ImageDraw.Draw(debug,'RGBA')
 for x,y in m.scene_walk:dd.rectangle((x*16,y*16,x*16+15,y*16+15),fill=(60,240,140,85))
 debug.save(ROOT/f'previews/{m.name}_{m.season}_navigation.png')
