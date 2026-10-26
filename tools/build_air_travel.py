"""Original code-drawn airline assets, playable snow airstrip and compatible CP update.
Run standalone or after build_content.py. No game binaries or saves are written.
"""
from pathlib import Path
from PIL import Image, ImageDraw
import json, math, random, struct, wave
import xml.etree.ElementTree as E
ROOT=Path(__file__).resolve().parents[1]
PACK=ROOT/'ContentPack'
RUNTIME=ROOT/'Code/ArcticPassage/Runtime'
ART=RUNTIME/'assets/flight'; ART.mkdir(parents=True,exist_ok=True)
SEASONS=['spring','summer','fall','winter']

def dump(path,value):
 path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')

def plane():
 im=Image.new('RGBA',(200,88));d=ImageDraw.Draw(im)
 # Far ski, undercarriage, high wing and engine pod; starboard profile.
 d.line((54,59,50,74,89,74),fill='#243e4f',width=3)
 d.line((134,60,140,75,176,75),fill='#243e4f',width=3)
 for x in [48,138]:
  d.polygon([(x-4,75),(x+31,75),(x+39,71),(x+34,79),(x-5,79)],fill='#a8b8b9',outline='#334f60')
  d.line((x,76,x+30,76),fill='#e3ebdf')
 d.polygon([(49,44),(76,17),(117,14),(135,19),(100,37),(154,39),(161,47),(116,49)],fill='#596d78',outline='#243e4f')
 d.line((78,19,116,16,132,20),fill='#b8c7c5',width=2)
 # Tail with moon/bird emblem and distinct high horizontal stabilizer.
 d.polygon([(18,49),(13,14),(26,11),(46,41)],fill='#b54f4a',outline='#263e50')
 d.line((17,17,26,15,39,39),fill='#e5ad7c',width=2)
 d.ellipse((20,21,30,31),fill='#e8d6a8');d.ellipse((24,20,31,28),fill='#b54f4a')
 d.line((20,27,24,25,27,27,31,25),fill='#fff3d3',width=1)
 d.polygon([(7,49),(19,42),(62,45),(67,50),(21,54)],fill='#d4d9c7',outline='#243e4f')
 # Fuselage, reinforced belly, cockpit, emergency door and cabin glazing.
 d.polygon([(19,43),(44,39),(148,38),(167,40),(184,48),(195,54),(194,59),(179,65),(58,65),(31,57)],fill='#ece4ca',outline='#243e4f')
 d.polygon([(29,53),(181,53),(194,56),(180,62),(58,62)],fill='#b54f4a')
 d.line((45,52,183,52),fill='#d0a35f');d.line((57,64,175,64),fill='#62808b')
 d.polygon([(152,40),(166,42),(180,49),(155,49)],fill='#33566b',outline='#253d50')
 d.line((162,42,168,48),fill='#9dc6ca');d.line((173,47,178,49),fill='#b9d8d4')
 for x in range(54,144,13):
  d.rounded_rectangle((x,43,x+8,49),radius=1,fill='#355c70')
  d.line((x+1,44,x+5,44),fill='#91b5be')
 d.rectangle((40,43,50,59),outline='#918b79');d.point((47,53),fill='#344e5b')
 for x in range(58,174,6):d.point((x,59),fill='#d98c68')
 # Near wing sits above cabin; strut, near engine and prop hub.
 d.line((93,57,119,31),fill='#536c78',width=2)
 d.polygon([(77,37),(113,28),(154,28),(162,32),(113,39)],fill='#e3dfc8',outline='#2b4556')
 d.line((87,36,146,30),fill='#fff3d5')
 d.polygon([(127,32),(147,33),(154,39),(151,44),(126,43)],fill='#b34e49',outline='#294351')
 d.line((130,34,148,35),fill='#edba80');d.ellipse((148,36,156,43),fill='#314d5f')
 for x,y in [(146,48),(28,16)]:d.point((x,y),fill='#ffe9a1')
 im.save(ART/'plane.png');return im


def scenery():
 # A low, pale sun and restrained sky; no forest, southern farm or fantasy aurora.
 im=Image.new('RGB',(640,360));d=ImageDraw.Draw(im)
 top=(58,91,116);bottom=(218,225,217)
 for y in range(360):
  f=y/359;d.line((0,y,639,y),fill=tuple(round(a+(b-a)*f) for a,b in zip(top,bottom)))
 for rad,c in [(39,'#afbec0'),(25,'#c8cfc4'),(15,'#e9dec0')]:d.ellipse((495-rad,119-rad,495+rad,119+rad),fill=c)
 im.save(ART/'sky.png')
 im=Image.new('RGBA',(1280,250));d=ImageDraw.Draw(im);rr=random.Random(772)
 for layer in range(3):
  base=140+layer*35; outline=[(-30,250)]
  for x in range(-30,1340,35):outline.append((x,base-rr.randrange(10,78)))
  outline.extend([(1340,250)])
  d.polygon(outline,fill=['#8fa9b5','#617e94','#405c73'][layer])
  for i in range(1,len(outline)-2):
   x,y=outline[i];nx,ny=outline[i+1]
   d.polygon([(x,y),(nx,ny),(nx+12,ny+27),(x+11,y+18)],fill=['#d9e4e2','#a9c2cf','#8faabd'][layer])
   for j in range(3):d.line((x+10+j*5,y+20+j*8,x+17+j*5,y+39+j*8),fill=['#b7cad0','#7799b0','#607f99'][layer])
 # Distant ice tongue descending between dark rock faces.
 d.polygon([(815,91),(851,125),(905,165),(980,205),(1045,239),(873,250),(846,196),(802,156),(784,124)],fill='#c2dce1')
 for k in range(12):
  x=813+k*7; y=125+k*8;d.line((x,y,x+55,y+19),fill='#83b0c6',width=2)
 im.save(ART/'mountains.png')
 im=Image.new('RGBA',(1280,170));d=ImageDraw.Draw(im);rr=random.Random(773)
 d.rectangle((0,0,1279,169),fill='#244b65')
 for _ in range(1700):
  x,y=rr.randrange(1280),rr.randrange(170);d.line((x,y,x+rr.randrange(2,15),y),fill=rr.choice(['#355e77','#496f82','#244b65']))
 for x,y,w in [(110,43,70),(380,87,46),(710,25,98),(1070,99,82)]:
  d.polygon([(x,y+14),(x+12,y-9),(x+24,y-5),(x+33,y-25),(x+w-8,y+2),(x+w,y+17),(x+45,y+25)],fill='#9bc9d7',outline='#598da8')
  d.polygon([(x+12,y-8),(x+24,y-4),(x+33,y-24),(x+46,y+13),(x+7,y+16)],fill='#e2efeb')
  d.line((x+7,y+20,x+w-7,y+19),fill='#6da8bd')
 im.save(ART/'sea.png')
 im=Image.new('RGBA',(1280,170));d=ImageDraw.Draw(im);rr=random.Random(774)
 d.polygon([(0,44),(80,34),(210,48),(375,30),(520,42),(660,20),(820,38),(1010,25),(1279,43),(1279,169),(0,169)],fill='#cedee5')
 d.rectangle((0,84,1279,122),fill='#a4bdce');d.line((0,83,1279,83),fill='#edf3ed',width=2)
 for y in [92,115]:d.line((0,y,1279,y),fill='#859fb5')
 for x in range(0,1280,68):
  d.line((x,102,x+27,102),fill='#e5eeeb',width=2)
  for yy in [75,132]:
   d.rectangle((x,yy,x+2,yy+6),fill='#4c6378');d.rectangle((x,yy,x+2,yy+1),fill='#edc67d')
 for _ in range(850):
  x,y=rr.randrange(1280),rr.randrange(136,170);d.line((x,y,x+rr.randrange(3,15),y-1),fill=rr.choice(['#e9f0ed','#bdcfdf','#9bb6cb']))
 # Red terminal/green equipment shed, windsock and amber windows.
 for x,y,w,h,c in [(850,54,73,29,'#a34f48'),(947,62,42,22,'#456f70')]:
  d.rectangle((x,y,x+w,y+h),fill=c,outline='#354e61')
  d.polygon([(x-5,y),(x+w//2,y-19),(x+w+5,y),(x+w+2,y+3),(x-3,y+3)],fill='#ecf1e9',outline='#57788f')
  for wx in range(x+7,x+w-10,16):d.rectangle((wx,y+8,wx+9,y+17),fill='#edc78b');d.line((wx+4,y+8,wx+4,y+17),fill='#6b6354')
  for wy in range(y+21,y+h,4):d.line((x+1,wy,x+w-1,wy),fill='#794c45')
 d.line((1030,81,1030,15),fill='#354d5b',width=2)
 d.polygon([(1030,15),(1061,24),(1059,29),(1030,22)],fill='#d4895d')
 for xx in [1037,1048]:d.line((xx,18+(xx-1030)//4,xx,24+(xx-1030)//4),fill='#f5e3bb',width=3)
 im.save(ART/'runway.png')


def airstrip(aircraft):
 w,h=64,40;im=Image.new('RGBA',(w*16,h*16),'#c7d8e4');d=ImageDraw.Draw(im);rr=random.Random(775)
 for _ in range(15000):
  x,y=rr.randrange(w*16),rr.randrange(h*16);d.line((x,y,x+rr.randrange(1,8),y-1),fill=rr.choice(['#dfe9ef','#b0c8dc','#d0deea','#c1d3e2']))
 # Bedrock encloses a plateau. Snow strips are authored above the settlement.
 for x,y,ww,hh in [(10,30,140,60),(210,0,180,60),(520,10,180,65),(830,30,190,80),(20,355,155,155),(800,380,200,145)]:
  pts=[(x,y+hh),(x+12,y+20),(x+ww//3,y),(x+ww-10,y+15),(x+ww,y+hh),(x+ww-20,y+hh+30),(x+10,y+hh+20)]
  d.polygon(pts,fill='#4c637b',outline='#304d64');d.polygon(pts[:5],fill='#e1eaf2')
  for xx in range(x+15,x+ww-15,8):d.line((xx,y+hh-7,xx-4,y+hh+15),fill='#849eb9')
 # Runway, grooved packed snow, threshold, edge posts, fuel-safe apron.
 d.rounded_rectangle((26,123,994,277),radius=32,fill='#abc2d7')
 d.rectangle((40,145,980,248),fill='#bfcede')
 for yy in range(151,246,5):d.line((42,yy,978,yy),fill='#adc1d3')
 for xx in range(88,954,80):d.rectangle((xx,193,xx+36,198),fill='#edf1e9')
 for xx in [58,928]:
  for yy in range(157,239,16):d.rectangle((xx,yy,xx+24,yy+5),fill='#f4efe0')
 for xx in range(44,984,64):
  for yy in [132,259]:d.rectangle((xx,yy,xx+3,yy+8),fill='#40586f');d.rectangle((xx,yy,xx+3,yy+2),fill='#eac380')
 d.rectangle((180,275,630,448),fill='#b8cddd')
 for yy in [303,386]:d.line((194,yy,590,yy),fill='#8cabc1',width=2)
 for xx in range(200,600,10):d.line((xx,391,xx+4,391),fill='#ecdcad',width=2)
 parked=aircraft.copy();im.alpha_composite(parked,(180,296))
 d=ImageDraw.Draw(im)
 # Small working terminal: 7x5 tiles, broad staircase and fenced circulation.
 x,y=490,330
 d.rectangle((x+4,y+30,x+119,y+101),fill='#3c5265');d.rectangle((x+4,y+25,x+115,y+88),fill='#ac574c',outline='#3a4e60')
 for yy in range(y+33,y+86,5):d.line((x+6,yy,x+113,yy),fill='#86493f')
 d.polygon([(x-3,y+31),(x+52,y-4),(x+123,y+29),(x+118,y+35),(x+2,y+35)],fill='#526b81',outline='#334e65')
 d.polygon([(x+2,y+27),(x+52,y-6),(x+118,y+26),(x+104,y+28),(x+52,y+5),(x+16,y+29)],fill='#eaf0ef')
 for wx in [x+14,x+81]:
  d.rectangle((wx,y+46,wx+20,y+65),fill='#314d61');d.rectangle((wx+2,y+48,wx+18,y+62),fill='#efce97');d.line((wx+10,y+48,wx+10,y+62),fill='#8c8170')
 d.rectangle((x+48,y+49,x+68,y+87),fill='#344d5c');d.rectangle((x+51,y+51,x+65,y+83),fill='#d0b085');d.point((x+62,y+69),fill='#efe2b8')
 for yy in [y+88,y+94,y+100]:d.rectangle((x+43,yy,x+74,yy+4),fill='#879fb3');d.line((x+44,yy,x+73,yy),fill='#e4eae8')
 # Passenger path and painted no-walk runway boundary.
 d.line((410,432,410,480,430,520,430,639),fill='#98b6cf',width=47)
 d.line((410,432,410,480,430,520,430,639),fill='#dce7ef',width=37)
 d.line((410,449,548,449,548,432),fill='#dce7ef',width=32)
 for xx,yy in [(391,451),(451,535),(399,586)]:
  d.line((xx,yy-21,xx,yy+5),fill='#4c6173',width=2);d.rectangle((xx-3,yy-26,xx+3,yy-20),fill='#f0c982')
 d.line((712,361,712,275),fill='#3e586b',width=2);d.polygon([(712,275),(758,288),(756,295),(712,284)],fill='#c37a54')
 for xx in [724,742]:d.line((xx,278+(xx-712)//4,xx,286+(xx-712)//4),fill='#f1e0bd',width=4)
 # Boarding sign beside the safe passenger path.
 d.rectangle((442,462,445,484),fill='#46576a');d.rectangle((433,452,456,469),fill='#274b61',outline='#d3c39b');d.line((437,457,451,457),fill='#eddbaf')
 im.save(PACK/'assets/maps/Airstrip_snow_scene.png')
 walk={(x,y) for y in range(h) for x in range(w) if (24<=x<=28 and 25<=y<=32) or (25<=x<=28 and 31<=y<=39) or (25<=x<=35 and 27<=y<=28) or (33<=x<=35 and 26<=y<=28)}
 # Departure from actual parked plane; runway itself is not pedestrian space.
 points={'spawn':[25,26],'boarding_approach':[27,30],'terminal_approach':[34,27],'town_exit':[26,38]}
 for season in SEASONS:
  root=E.Element('map',version='1.10',orientation='orthogonal',renderorder='right-down',width=str(w),height=str(h),tilewidth='16',tileheight='16',infinite='0')
  pp=E.SubElement(root,'properties')
  # Every walkable bottom-edge tile is an exit; no unwarped lane can leak off-map.
  for k,v in {'Outdoors':'T','PassOutSafe':'T','LocationContext':'ArcticPassage_TundraClimate','Warp':' '.join(f'{x} 39 ArcticPassage_Town 27 2' for x in range(25,29))}.items():E.SubElement(pp,'property',name=k,value=v)
  ts=E.SubElement(root,'tileset',firstgid='1',name='z_AirstripScene',tilewidth='16',tileheight='16',tilecount=str(w*h),columns=str(w));E.SubElement(ts,'image',source='Airstrip_snow_scene.png',width=str(w*16),height=str(h*16))
  for y in range(h):
   for x in range(w):
    tile=E.SubElement(ts,'tile',id=str(y*w+x));pr=E.SubElement(tile,'properties');E.SubElement(pr,'property',name='Type',value='Stone');E.SubElement(pr,'property',name='NoSpawn',value='All')
  solid=w*h+1
  ts=E.SubElement(root,'tileset',firstgid=str(solid),name='z_AirstripCollision',tilewidth='16',tileheight='16',tilecount='1',columns='1');E.SubElement(ts,'image',source='Airstrip_collision.png',width='16',height='16')
  action={(27,29):'ArcticPassageFlight',(34,26):'Message ArcticPassage_Airport'}
  gids={pos:solid+1+i for i,pos in enumerate(action)}
  for pos,gid in gids.items():
   ts=E.SubElement(root,'tileset',firstgid=str(gid),name=f'z_AirstripAction{gid}',tilewidth='16',tileheight='16',tilecount='1',columns='1');E.SubElement(ts,'image',source='Airstrip_collision.png',width='16',height='16');tile=E.SubElement(ts,'tile',id='0');pr=E.SubElement(tile,'properties');E.SubElement(pr,'property',name='Action',value=action[pos])
  for i,name in enumerate(['Back','Buildings','Front','AlwaysFront']):
   ly=E.SubElement(root,'layer',id=str(i+1),name=name,width=str(w),height=str(h));grid=[]
   for y in range(h):
    row=[]
    for x in range(w):
     gid=y*w+x+1 if name=='Back' else (gids.get((x,y),solid if (x,y) not in walk else 0) if name=='Buildings' else 0)
     if name=='Front' and 30<=x<=38 and 20<=y<=24:gid=y*w+x+1
     row.append(gid)
    grid.append(','.join(map(str,row)))
   E.SubElement(ly,'data',encoding='csv').text='\n'+',\n'.join(grid)+'\n'
  group=E.SubElement(root,'objectgroup',name='Buildings',visible='0')
  for (x,y),act in action.items():
   ob=E.SubElement(group,'object',name='TileData',x=str(x*16),y=str(y*16),width='16',height='16');pr=E.SubElement(ob,'properties');E.SubElement(pr,'property',name='Action',type='string',value=act)
  E.indent(root);E.ElementTree(root).write(PACK/f'assets/maps/Airstrip_{season}.tmx',encoding='utf-8',xml_declaration=True)
 Image.new('RGBA',(16,16)).save(PACK/'assets/maps/Airstrip_collision.png')
 debug=im.copy();d=ImageDraw.Draw(debug,'RGBA')
 for x,y in walk:d.rectangle((x*16,y*16,x*16+15,y*16+15),fill=(60,240,140,70))
 debug.save(ROOT/'previews/Airstrip_navigation.png');im.convert('RGB').save(ROOT/'previews/Airstrip_snow.png')
 return {'size':[w,h],'points':points}


def engine_audio():
 # Phase-continuous 2-second propeller loop; gain and ramp are handled in game.
 path=ART/'propeller.wav';sr=22050
 with wave.open(str(path),'wb') as out:
  out.setparams((1,2,sr,0,'NONE','not compressed'));samples=[]
  for i in range(sr*2):
   t=i/sr;v=.42*math.sin(2*math.pi*78*t)+.16*math.sin(2*math.pi*156*t)+.06*math.sin(2*math.pi*311*t)
   v*=.8+.2*math.cos(2*math.pi*8*t);samples.append(struct.pack('<h',round(v*12000)))
  out.writeframes(b''.join(samples))


def content(index):
 p=PACK/'content.json';data=json.loads(p.read_text());changes=data['Changes']
 # Replace the old beach teleport; keep the two letters' internal IDs for saves.
 changes[:]=[c for c in changes if c['Target']!='Maps/Beach' and not c.get('LogName','').startswith('Air travel:')]
 def patch(target,**kw):changes.append({'LogName':'Air travel: '+target,'Target':target,**kw})
 for change in changes:
  if change['Target']=='Data/TriggerActions':change.get('Entries',{}).pop('ArcticPassage_Invitation',None)
  if change['Target']=='Data/mail' and 'ArcticPassage_Invitation' in change.get('Entries',{}):
   change['Entries']['ArcticPassage_Invitation']='{{i18n:mail.invitation.legacy}}'
 patch('Data/TriggerActions',Action='EditData',Entries={'ArcticPassage_AirlineInvitation':{'Id':'ArcticPassage_AirlineInvitation','Trigger':'DayStarted','Condition':'!PLAYER_HAS_MAIL Current ArcticPassage_AirlineInvitation','Actions':['AddMail Current ArcticPassage_AirlineInvitation now']}})
 patch('Data/mail',Action='EditData',Entries={'ArcticPassage_AirlineInvitation':'{{i18n:mail.invitation}}'})
 patch('Maps/ArcticPassage_Airstrip',Action='Load',FromFile='assets/maps/Airstrip_{{MapSeason}}.tmx')
 patch('Mods/WhiteBay.ArcticPassage/FlightTicket',Action='Load',FromFile='assets/items/flight-ticket.png')
 patch('Data/Objects',Action='EditData',Entries={'ArcticPassage_FlightTicket':{'Name':'ArcticPassage_FlightTicket','DisplayName':'{{i18n:flight.ticket.name}}','Description':'{{i18n:flight.ticket.desc}}','Type':'Basic','Category':-999,'Price':0,'Edibility':-300,'Texture':'Mods/WhiteBay.ArcticPassage/FlightTicket','SpriteIndex':0,'CanBeGivenAsGift':False,'CanBeTrashed':False,'ExcludeFromFishingCollection':True,'ExcludeFromShippingCollection':True}})
 base=next(c['Entries']['ArcticPassage_Town'] for c in changes if c['Target']=='Data/Locations' and 'ArcticPassage_Town' in c.get('Entries',{}))
 loc={**base,'DisplayName':'{{i18n:location.Airstrip}}','DefaultArrivalTile':{'X':25,'Y':26},'CreateOnLoad':{'MapPath':'Maps/ArcticPassage_Airstrip'},'MusicDefault':'ArcticPassage_PolarNightTheme'}
 patch('Data/Locations',Action='EditData',Entries={'ArcticPassage_Airstrip':loc})
 # Existing return post becomes the free airport shuttle, retaining its position.
 patch('Maps/ArcticPassage_Town',Action='EditMap',MapTiles=[{'Position':{'X':40,'Y':24},'Layer':'Buildings','SetProperties':{'Action':'Warp 26 32 ArcticPassage_Airstrip'}}])
 patch('Strings/StringsFromMaps',Action='EditData',Entries={'ArcticPassage_Airport':'{{i18n:flight.airport}}'})
 for lang in ['default','zh']:
  q=PACK/f'i18n/{lang}.json';texts=json.loads(q.read_text());zh=lang=='zh'
  texts.update({
   'mail.invitation':('亲爱的农夫：^我是月月鸟。想邀请你离开熟悉的田野，去北方走一走。那里有被冰川雕刻的峡湾、风吹过的苔原，还有一座灯火温暖的小镇——霜灯港。^随信附上月月鸟航空的往返机票。请到山谷巴士站的航空接驳点办理登机；在那里按 B 查看机票。带上好奇心，也可以带一根钓竿。^不必急着完成什么。先听听风，看看北极的光。期待你把沿途的故事带回来。^-月月鸟 %item object ArcticPassage_FlightTicket 1 %%[#]给你一张飞往北方的机票' if zh else 'Dear farmer,^I am Yueyueniao. Come north with me, beyond the familiar fields, to glacier-carved fjords, wind-swept tundra, and a little town with warm windows: Frosthavn.^Enclosed is a return ticket with Moonbird Air. Check in at our Valley bus-stop transfer point; press B there to view your ticket. Bring your curiosity, and perhaps a fishing rod.^There is no need to rush. Listen to the wind. Watch the Arctic light. I look forward to the stories you bring home.^-Yueyueniao %item object ArcticPassage_FlightTicket 1 %%[#]A ticket to the northern light'),
   'quest.Arrival.desc':'月月鸟邀请你探索北极。降落后沿标记步道下山，去霜灯港的红色旅舍安顿下来。' if zh else 'Yueyueniao has invited you to explore the Arctic. After landing, follow the marked path down to the red guesthouse in Frosthavn.',
   'flight.ticket.name':'月月鸟航空往返机票' if zh else 'Moonbird Air return ticket',
   'flight.ticket.desc':'目的地：霜灯港。月月鸟邀请你探索北极。巴士站按 B 办理登机；返程已包含。航程登记在邀请信中，不消耗机票。' if zh else 'Destination: Frosthavn. An invitation to explore the Arctic. Press B at the bus stop to check in. Return included; the ticket is not consumed.',
   'location.Airstrip':'霜灯港雪原机场' if zh else 'Frosthavn snowfield airstrip',
   'flight.airport':'月月鸟航空 · 霜灯港雪原机场。沿标记步道向南进入镇区，红色旅舍可以过夜；按 B 办理免费返程。这里位于镇外较高的雪原，跑道不是步行道。' if zh else 'Moonbird Air / Frosthavn snowfield airstrip. Follow the marked path south into town; the red guesthouse has a bed. B checks in for your included return. This snowfield sits above the town. Stay off the runway.',
   'sign.lodging':'炉火还温着，房间在左侧。返程时，镇东侧码头旁的接驳牌可送你回雪原机场，再按 B 办理返航。' if zh else 'The fire is warm; your room is on the left. The shuttle post by the eastern town pier takes you back to the snowfield airstrip. Press B there for your return flight.'})
  texts['mail.invitation.legacy']=texts['mail.invitation'].replace(' %item object ArcticPassage_FlightTicket 1 %%','')
  texts['event.arrival1']='欢迎来到霜灯港！月月鸟说你会搭航班来。红房子里替你留了房间，先暖暖身子吧。' if zh else 'Welcome to Frosthavn! Yueyueniao told us you were flying in. There is a room waiting in the red house; come warm up.'
  dump(q,texts)
 idx=ROOT/'docs/build-index.json';obj=json.loads(idx.read_text());obj['maps']['Airstrip']=index;dump(idx,obj);dump(p,data)
 # Visible 16px ticket with perforation and moon-bird mark, not a fake QR code.
 icon=Image.new('RGBA',(16,16));d=ImageDraw.Draw(icon);d.rectangle((1,3,14,12),fill='#efe5c6',outline='#36566b');d.rectangle((2,4,4,11),fill='#a64f49');d.line((10,4,10,11),fill='#a99a7f');d.line((5,7,8,7),fill='#36566b');d.line((6,6,7,8),fill='#36566b');d.point((12,6),fill='#a64f49');d.point((12,9),fill='#a64f49');icon.save(PACK/'assets/items/flight-ticket.png')


def main():
 scenery();aircraft=plane();idx=airstrip(aircraft);engine_audio();content(idx)
 print('Built original flight layers, plane, propeller loop, four snowfield maps and airline invitation/ticket.')
if __name__=='__main__':main()
