"""Arctic landscape art direction and native pixel assets for version 0.2."""
from PIL import Image,ImageDraw
from pathlib import Path
import random,math

def enrich_atlas(a):
 winter=a.season=='winter'; melt=a.season=='spring'; summer=a.season=='summer'
 snow=(224,237,235); soil=(132,150,127) if summer else (135,133,117) if a.season=='fall' else (187,208,211)
 # Replace flat, single-color surfaces with sparse clustered material variation.
 for n in range(5):
  base=snow if winter else soil
  def terrain(d,w,h,n=n,base=base):
   d.rectangle((0,0,15,15),fill=base);rr=random.Random(190+n)
   for k in range(6):
    x,y=rr.randrange(14),rr.randrange(14);delta=rr.choice([-9,-5,5,8]);c=tuple(max(0,min(255,v+delta)) for v in base);d.line((x,y,x+rr.randrange(1,4),y),fill=c)
   if winter:
    d.line((0,13,6,13,9,11,15,11),fill='#ccdde0');d.line((1,12,6,12),fill='#eff6ec')
   elif n in [1,3]:
    for x,y in [(2,3),(10,9),(5,12)]:d.line((x,y,x+2,y-1),fill='#6e806c' if summer else '#7c7b6c')
  a.add('terrain'+str(n),1,1,terrain,{'Type':'Stone','NoSpawn':'All'})
 for n,c in enumerate(['#194b66','#215c75','#2d6d80','#3c8290']):
  def sea(d,w,h,c=c,n=n):
   d.rectangle((0,0,15,15),fill=c)
   if n%2==0:d.line((2,5,5,5),fill='#437b90');d.point((6,4),fill='#437b90')
   d.line((10,12,14,12),fill='#41768c')
  a.add('sea'+str(n),1,1,sea,{'Water':'T','Passable':'T','NoSpawn':'All'})
 # Terrain edge masks: a dark rock lip under a pale snow/lichen cap.
 for mask in range(1,16):
  def coast(d,w,h,mask=mask):
   d.rectangle((0,0,15,15),fill=snow if winter else soil)
   for bit,points in [(1,(0,0,15,3)),(2,(12,0,15,15)),(4,(0,12,15,15)),(8,(0,0,3,15))]:
    if mask&bit:
     d.rectangle(points,fill='#526a75')
     if bit==4:d.line((0,11,15,11),fill='#dce8e1' if winter else '#acb8a5');d.line((0,15,15,15),fill='#a2c6cd')
     if bit==2:d.line((11,0,11,15),fill='#dce8e1' if winter else '#acb8a5');d.line((15,0,15,15),fill='#a2c6cd')
     if bit==8:d.line((4,0,4,15),fill='#dce8e1' if winter else '#acb8a5')
     if bit==1:d.line((0,4,15,4),fill='#dce8e1' if winter else '#acb8a5')
  a.add('coast'+str(mask),1,1,coast,{'Type':'Stone','NoSpawn':'All'})
 # Footpaths are compacted snow in winter, weathered gravel in summer.
 def path(d,w,h):
  base='#b5c8cb' if winter else '#abbcb8' if melt else '#afa58c'
  d.rectangle((0,0,15,15),fill=base)
  for x,y in [(2,4),(9,11),(12,2)]:
   d.line((x,y,x+2,y),fill='#93aeb8' if winter else '#968e7c');d.point((x,y-1),fill='#c8d8d7' if winter else '#c3b79a')
 a.add('path',1,1,path,{'Type':'Dirt','NoSpawn':'All'})
 # Larger cottages, with front gable, a visible side wall, slate foundations and snow eaves.
 for index,(wall,shade,light,roof) in enumerate([('#ad5149','#763b3b','#d47a64','#6a5958'),('#487e9b','#32566e','#7aa6b8','#4b606c'),('#c9a755','#8d7045','#e3c879','#5f645f'),('#5c8174','#405e5c','#90a88a','#59656b')]):
  def house(d,w,h,wall=wall,shade=shade,light=light,roof=roof):
   d.ellipse((5,h-10,w-2,h-1),fill='#29455145')
   d.polygon([(10,41),(88,41),(103,33),(103,83),(88,93),(10,93)],fill=wall,outline='#334752')
   d.polygon([(88,41),(103,33),(103,83),(88,93)],fill=shade)
   for y in range(46,91,5):
    d.line((11,y,87,y),fill=shade);d.line((12,y+1,86,y+1),fill=light)
    d.line((89,y,102,y-7),fill='#40515a')
   d.rectangle((10,88,88,95),fill='#59636a');d.line((13,90,86,90),fill='#899192')
   # steep offset roof and warm chimney
   d.polygon([(1,43),(43,7),(70,7),(111,39),(87,45),(44,16),(9,46)],fill='#354b5b',outline='#293b49')
   d.polygon([(5,39),(44,9),(84,39)],fill=roof)
   d.polygon([(45,9),(68,9),(107,37),(85,40)],fill='#4c5d67')
   for y in range(18,40,6):d.line((45+(y-10),y,67+(y-10),y),fill='#819298')
   if winter or melt:
    d.polygon([(4,37),(43,8),(69,8),(106,36),(87,39),(45,12),(12,41)],fill='#e3efed',outline='#b2ced5')
    d.line((13,38,43,15,79,38),fill='#f4f5e9',width=2)
    for x,y in [(12,42),(22,34),(82,41),(94,38)]:d.line((x,y,x,y+3),fill='#b1cfd8')
   d.rectangle((75,3,84,20),fill='#6c6061');d.rectangle((73,2,86,5),fill='#a09d99');d.line((77,7,82,7),fill='#4a5058')
   # Double windows, with thick cream casings, muntins and shadowed ledges.
   for x in [20,66]:
    d.rectangle((x-2,51,x+16,73),fill='#353f49');d.rectangle((x,52,x+14,70),fill='#e9dcc0');d.rectangle((x+2,54,x+12,68),fill='#dca760');d.rectangle((x+3,55,x+7,62),fill='#ffe0a0');d.line((x+7,54,x+7,68),fill='#765a4d');d.line((x+2,62,x+12,62),fill='#765a4d');d.rectangle((x-3,71,x+17,74),fill='#617480')
   d.rectangle((46,59,62,91),fill='#e3d2ae');d.rectangle((48,61,60,91),fill='#735446');d.rectangle((50,63,58,73),fill='#eac58b');d.point((58,80),fill='#e0c579');d.line((48,77,59,77),fill='#a78361')
   # raised entrance deck and two visible slate steps
   d.rectangle((41,91,68,94),fill='#b8a891');d.rectangle((39,94,70,95),fill='#687d88')
   for x in [12,86]:d.rectangle((x,43,x+2,86),fill='#dbcdb1')
  a.add('house'+str(index),7,6,house)
 def cliff(d,w,h):
  d.polygon([(2,8),(12,2),(32,3),(46,12),(45,28),(36,39),(8,38),(1,26)],fill='#425b6c',outline='#314a5d')
  d.polygon([(3,9),(13,3),(31,4),(43,12),(31,18),(10,19)],fill='#8ea5aa')
  d.polygon([(4,10),(13,4),(31,5),(40,11),(29,15),(11,17)],fill='#e2ede7' if winter or melt else '#aab5a6')
  for x in [11,22,34]:d.line((x,20,x-2,31),fill='#6e8995');d.line((x+1,22,x,33),fill='#263f54')
 a.add('cliff',3,3,cliff)
 def drift(d,w,h):
  d.ellipse((1,6,w-2,h-1),fill='#aac6ce');d.ellipse((0,2,w-3,h-4),fill='#e8f0e9');d.line((5,7,w-10,4),fill='#f9f6e8');d.line((w-14,h-7,w-5,h-7),fill='#c1d7db')
 a.add('drift',3,2,drift)
 def iceberg(d,w,h):
  d.ellipse((0,h-12,w-1,h-1),fill='#39798f80');p=[(2,h-22),(13,32),(30,38),(47,6),(68,17),(80,5),(101,31),(w-3,h-27),(w-20,h-10),(32,h-8)]
  d.polygon(p,fill='#8fc6d9',outline='#447e9d');d.polygon([(3,h-24),(15,33),(30,40),(47,7),(55,24),(42,h-20),(20,h-14)],fill='#eaf4ed');d.polygon([(49,8),(69,18),(79,7),(85,42),(75,h-20),(43,h-20)],fill='#c9e7e9');d.polygon([(81,8),(102,32),(w-4,h-28),(75,h-20),(85,42)],fill='#79b6d1')
  for x,y in [(44,36),(70,30),(93,40),(28,53)]:d.line((x,y,x-3,y+20),fill='#5b9fbe');d.line((x+2,y,x,y+14),fill='#b4dbe4')
  d.line((28,h-11,75,h-11,94,h-17),fill='#daf1e9',width=2)
 a.add('icebergLarge',8,6,iceberg)
 def net(d,w,h):
  d.rectangle((1,6,w-2,22),fill='#765941')
  for x in range(2,w-2,4):d.line((x,5,x+6,23),fill='#a5a58d');d.line((x,23,x+6,6),fill='#a5a58d')
  d.line((1,4,w-2,4),fill='#d9be8e');d.rectangle((1,1,3,29),fill='#6d5545');d.rectangle((w-4,1,w-2,29),fill='#6d5545')
 a.add('net',3,2,net)
 def buoy(d,w,h):
  for x in [5,20]:
   d.line((x+2,1,x+2,7),fill='#bda177');d.ellipse((x-1,6,x+5,17),fill='#c46d4f',outline='#714c40');d.line((x,10,x+4,10),fill='#e9d9ae');d.line((x+2,18,x+2,29),fill='#a48b69')
 a.add('buoys',2,2,buoy)
 def bollard(d,w,h):
  d.ellipse((2,10,14,15),fill='#5d5047');d.rectangle((5,4,11,12),fill='#4b616b');d.ellipse((3,2,13,7),fill='#91a5a5',outline='#344b5d');d.arc((0,7,15,15),0,320,fill='#d0b987',width=2)
 a.add('bollard',1,1,bollard)
 def sled(d,w,h):
  d.line((3,26,42,26,47,22),fill='#927253',width=2);d.line((6,31,45,31,50,27),fill='#d3b17c',width=2);d.polygon([(8,11),(33,11),(43,22),(16,22)],fill='#b78859',outline='#674f40')
  for x in range(13,34,5):d.line((x,13,x+7,20),fill='#e2ba7d')
  d.line((8,11,6,3,12,2,15,10),fill='#7c6046',width=2);d.line((13,23,13,29),fill='#73513e');d.line((37,23,37,29),fill='#73513e');d.rectangle((20,9,33,17),fill='#7b9091')
 a.add('sled',4,2,sled)
 def dog(d,w,h):
  # A static working-dog scene prop, distinct pointed muzzle and upright ears.
  d.ellipse((5,21,39,29),fill='#45596740');d.polygon([(7,15),(2,11),(0,6),(5,8),(11,10)],fill='#b3c4c8');d.ellipse((8,10,32,23),fill='#b6c6c9',outline='#667e8c');d.polygon([(27,10),(29,2),(33,7),(38,2),(39,12),(45,16),(38,19),(29,17)],fill='#d6e1df',outline='#667e8c');d.polygon([(30,5),(32,8),(30,9)],fill='#8e7b75');d.rectangle((40,14,45,16),fill='#394f5f');d.point((36,11),fill='#233747')
  for x in [13,27]:d.rectangle((x,19,x+3,27),fill='#dce5dd');d.line((x,27,x+5,27),fill='#637b88')
  d.line((27,18,33,20),fill='#ae6351',width=2)
 a.add('dog',3,2,dog)
 def fishrack(d,w,h):
  for x in [3,w-5]:d.line((x,1,x,h-1),fill='#785c46',width=3);d.line((x+1,1,x+1,h-2),fill='#c29c6b')
  for yy in [5,17]:
   d.line((2,yy,w-3,yy),fill='#d3bb89');
   for x in range(10,w-4,9):d.line((x,yy,x,yy+3),fill='#897b64');d.polygon([(x,yy+3),(x-2,yy+7),(x-1,yy+12),(x+2,yy+12),(x+3,yy+7)],fill='#d6c9aa',outline='#8c8879')
 a.add('rack',4,3,fishrack)
 def lamp(d,w,h):
  d.ellipse((1,25,15,31),fill='#49647645');d.rectangle((7,9,9,30),fill='#3a5365');d.rectangle((3,3,13,13),fill='#3b5263');d.rectangle((5,5,11,11),fill='#ffd28a');d.line((4,2,12,2),fill='#9bafae');d.line((7,0,9,0),fill='#3b5263')
 a.add('lamp',1,2,lamp)
 # Rejected glacier-wall prototype remains in art/source for provenance only.
 # The composed Icefjord scene supplies the actual environment artwork.
 return a

def decorate_map(m):
 if m.name in ['Guesthouse','Fishery']:return
 a=m.a;sea=a.tiles['water'][0][0];ground=a.tiles['ground'][0][0];winter=m.season=='winter';rr=random.Random(517+len(m.name))
 original=[row[:] for row in m.layers['Back']]
 def water(x,y):return 0<=x<m.w and 0<=y<m.h and original[y][x]==sea
 for y in range(m.h):
  for x in range(m.w):
   if original[y][x]==sea:
    near=min((abs(dx)+abs(dy) for dy in range(-3,4) for dx in range(-3,4) if 0<=x+dx<m.w and 0<=y+dy<m.h and original[y+dy][x+dx] not in [sea,0]),default=4)
    m.tile('sea'+str(max(0,3-near)),x,y)
   elif original[y][x]==ground:
    mask=sum(bit for bit,dx,dy in [(1,0,-1),(2,1,0),(4,0,1),(8,-1,0)] if water(x+dx,y+dy))
    m.tile('coast'+str(mask) if mask else 'terrain'+str((x*7+y*11)%5),x,y)
 # Props have deliberate clusters and large empty walking corridors.
 if m.name=='Town':
  for x,y in [(3,3),(4,11),(2,21),(3,35),(20,3),(35,2),(23,43),(38,40)]:m.composite('cliff',x,y)
  if winter or m.season=='spring':
   for x,y in [(12,13),(12,23),(35,13),(39,30),(14,39),(39,36)]:m.composite('drift',x,y,False)
  for x,y in [(13,20),(38,17),(14,34),(24,8)]:m.composite('net',x,y)
  m.composite('sled',22,30);m.composite('dog',22,28);m.composite('dog',25,30)
  m.composite('icebergLarge',48,31,False);m.composite('buoys',37,29);m.composite('rack',33,29)
 elif m.name=='Harbor':
  for x,y in [(4,3),(16,5),(3,17),(3,38),(18,42)]:m.composite('cliff',x,y)
  for x,y in [(16,16),(17,30),(6,30)]:m.composite('net',x,y)
  for x,y in [(28,14),(35,26),(25,37),(36,37)]:m.tile('bollard',x,y,'Front')
  m.composite('buoys',21,18);m.composite('buoys',28,21);m.composite('rack',8,27)
  m.composite('icebergLarge',47,33,False)
  if 'glacier' in a.tiles:m.composite('glacier',35,2,False)
  for x,y in [(17,8),(17,39),(5,16)]:
   if winter or m.season=='spring':m.composite('drift',x,y,False)
 elif m.name=='Icefjord':
  if 'glacier' in a.tiles:
   # Three connected glacier fronts occupy only remote, impassable water.
   for x,y in [(2,2),(34,3),(38,25)]:m.composite('glacier',x,y,False)
  m.composite('icebergLarge',41,20,False);m.composite('icebergLarge',57,34,False)
  for x,y in [(3,45),(18,33),(18,46)]:m.composite('cliff',x,y)
  m.composite('bollard',10,42,False);m.composite('lamp',13,38,False)
 elif m.name=='Tundra':
  for x,y in [(4,4),(9,8),(17,3),(48,3),(54,12),(6,28),(12,37),(50,35),(55,41)]:m.composite('cliff',x,y)
  for x,y in [(18,17),(32,9),(46,30),(20,38)]:
   if winter or m.season=='spring':m.composite('drift',x,y,False)
