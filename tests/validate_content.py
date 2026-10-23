"""Independent resource, graph and economy checks; does not simulate the game engine."""
from pathlib import Path
from collections import deque
import json,re,wave,struct,subprocess,xml.etree.ElementTree as E
from PIL import Image
R=Path(__file__).resolve().parents[1];P=R/'ContentPack';data=json.loads((P/'content.json').read_text());patches=data['Changes'];passed=[]
def require(ok,msg):
 if not ok:raise AssertionError(msg)
def record(s):passed.append(s);print('PASS',s)
def entries(target):
 out={}
 for p in patches:
  if p['Target']==target:out.update(p.get('Entries',{}))
 return out
maps={};warps=[];actions=[]
for path in sorted((P/'assets/maps').glob('*.tmx')):
 root=E.parse(path).getroot();w=int(root.get('width'));h=int(root.get('height'));props={};images={}
 for ts in root.findall('tileset'):
  gid=int(ts.get('firstgid'));image=ts.find('image');imagepath=(path.parent/image.get('source')).resolve();require(imagepath.exists(),str(imagepath));im=Image.open(imagepath);require(im.size==(int(image.get('width')),int(image.get('height'))),'Image geometry')
  count=int(ts.get('tilecount'))
  for i in range(count):props[gid+i]={}
  for t in ts.findall('tile'):props[gid+int(t.get('id'))]={p.get('name'):p.get('value') for p in t.findall('./properties/property')}
 layers={ly.get('name'):[int(v.strip()) for v in ly.find('data').text.strip().split(',')] for ly in root.findall('layer')}
 require(set(layers)=={'Back','Buildings','Front','AlwaysFront'},'Missing engine layer')
 for grid in layers.values():require(len(grid)==w*h,'Bad map dimensions');require(all(g==0 or g in props for g in grid),'Invalid GID')
 # GameLocation.isTileFishable rejects Back water covered by a Buildings tile
 # unless that Buildings tile explicitly also has Water. Walk blocking belongs
 # to the Back water property; transparent solids must not cover fishing water.
 for k,g in enumerate(layers['Back']):
  if g and 'Water' in props[g]:
   b=layers['Buildings'][k]
   require(not b or 'Water' in props[b],f'Fishing water blocked by Buildings: {path.name} {k%w},{k//w}')
 def walk(x,y):
  if not(0<=x<w and 0<=y<h):return False
  b=layers['Back'][y*w+x];solid=layers['Buildings'][y*w+x]
  return b>0 and 'Passable' not in props[b] and (not solid or 'Passable' in props[solid])
 mp={p.get('name'):p.get('value') for p in root.findall('./properties/property')};warp=mp.get('Warp','').split();require(len(warp)%5==0,'Malformed warp')
 name,season=path.stem.rsplit('_',1);index=json.loads((R/'docs/build-index.json').read_text())['maps'][name];start=tuple(index['points']['spawn']);require(walk(*start),f'Blocked arrival {path.name}')
 seen={start};queue=deque([start])
 while queue:
  x,y=queue.popleft()
  for nx,ny in [(x-1,y),(x+1,y),(x,y-1),(x,y+1)]:
   if (nx,ny) not in seen and walk(nx,ny):seen.add((nx,ny));queue.append((nx,ny))
 for i in range(0,len(warp),5):
  x,y,target,tx,ty=warp[i:i+5];require((int(x),int(y)) in seen,f'Unreachable exit {path.name}:{x},{y}');warps.append((path.stem,target,int(tx),int(ty),season))
 for lname,grid in layers.items():
  for k,g in enumerate(grid):
   if g and 'Action' in props[g]:
    x,y=k%w,k//w;act=props[g]['Action'];require(any(q in seen for q in [(x-1,y),(x+1,y),(x,y-1),(x,y+1)]),f'Cannot interact {path.name} {x},{y}: {act}')
    if act.startswith('Warp '):
     _,tx,ty,target=act.split();warps.append((path.stem,target,int(tx),int(ty),season))
 for label,point in index['points'].items():require(tuple(point) in seen,f'Unreachable {label} in {path.name}')
 fishable={(i%w,i//w) for i,g in enumerate(layers['Back']) if g and 'Water' in props[g] and not layers['Buildings'][i]}
 if 'fishing' in index['points']:
  fx,fy=index['points']['fishing']
  require(any((fx+dx*distance,fy+dy*distance) in fishable for dx,dy in [(0,-1),(0,1),(-1,0),(1,0)] for distance in range(2,6)),f'No fishing water within cast distance: {path.name}')
 maps[path.stem]={'walk':set(seen),'fishable':fishable,'w':w,'h':h,'occupied':{(i%w,i//w) for i,g in enumerate(layers['Buildings']) if g}}
for source,target,x,y,season in warps:
 if target=='Beach':continue
 dest=maps[target.removeprefix('ArcticPassage_')+'_'+season];require((x,y) in dest['walk'],f'Warp from {source} arrives blocked: {target} {x} {y}')
record(f'{len(maps)} TMX files: dimensions, tile GIDs, PNG resources and layers valid')
record(f'{len(warps)} exits/doors: reachable sources and walkable destinations in all four seasons')
record('Native fishing-water rule: no Buildings covers Back water; every marked fishing approach has water within casting distance in all seasons')
for name,ice,water in [('Harbor',(43,20),(33,20)),('Icefjord',(43,34),(39,37))]:
 require(ice not in maps[name+'_winter']['fishable'],'Painted winter shore ice remains fishable')
 require(all(water in maps[name+'_'+s]['fishable'] for s in ['spring','summer','fall','winter']),'Year-round open fishing lead lost')
for point in [(6,10),(7,17),(6,29)]:
 require(point in maps['Tundra_summer']['fishable'] and point not in maps['Tundra_winter']['fishable'],'Tundra pond ice does not match seasonal water data')
record('Winter shore ice and three frozen tundra ponds reject fishing; open harbor/fjord leads remain usable')

conditional=0
for p in patches:
 if p['Action']!='EditMap' or not p['Target'].startswith('Maps/ArcticPassage_'):continue
 name=p['Target'].removeprefix('Maps/ArcticPassage_')
 for tile in p.get('MapTiles',[]):
  x,y=tile['Position']['X'],tile['Position']['Y'];action=tile.get('SetProperties',{}).get('Action')
  if not action:continue
  for season in ['spring','summer','fall','winter']:
   mp=maps[name+'_'+season];require((x,y) in mp['occupied'],f'Conditional action lacks a real tile: {name} {x},{y}')
   require(any(q in mp['walk'] for q in [(x-1,y),(x+1,y),(x,y-1),(x,y+1)]),f'Conditional action inaccessible: {name} {x},{y}')
   if action.startswith('Warp '):
    _,tx,ty,target=action.split();dest=maps[target.removeprefix('ArcticPassage_')+'_'+season];require((int(tx),int(ty)) in dest['walk'],'Conditional warp destination blocked')
   conditional+=1
stops=0
for path in (P/'assets/data').glob('*_schedule.json'):
 for key,schedule in json.loads(path.read_text()).items():
  for segment in schedule.split('/'):
   parts=segment.split();name=parts[1].removeprefix('ArcticPassage_');point=(int(parts[2]),int(parts[3]))
   seasons=[key] if key in ['spring','summer','fall','winter'] else ['spring','summer','fall','winter']
   for season in seasons:require(point in maps[name+'_'+season]['walk'],f'NPC stop blocked: {path.stem} {key} {name} {point} ({season})');stops+=1
record(f'{conditional} seasonal unlock actions and {stops} NPC schedule destinations are reachable')

for p in patches:
 if p['Action']=='Load':
  for season in ['spring','summer','fall','winter']:require((P/p['FromFile'].replace('{{Season}}',season).replace('{{MapSeason}}',season)).exists(),'Missing content asset')
record('All Content Patcher Load sources exist')
for name in ['Ada','Mira','Roan']:
 target='Characters/Dialogue/ArcticPassage_'+name
 require(len(entries(target))==23,'Dialogue translations must resolve through EditData: '+name)
 require('{{' not in (P/f'assets/data/{name}_dialogue.json').read_text(),'Unresolved tokens in raw dialogue Load: '+name)
record('Three resident dialogue dictionaries resolve translations through EditData, not raw Load')
en=json.loads((P/'i18n/default.json').read_text());zh=json.loads((P/'i18n/zh.json').read_text());require(set(en)==set(zh),'Translation parity');text=(P/'content.json').read_text()+''.join(f.read_text() for f in (P/'assets/data').glob('*.json'))
for key in re.findall(r'\{\{i18n:([^}]+)\}\}',text):require(key in en,'Missing translation '+key)
record(f'{len(en)} translation keys complete in English and simplified Chinese')
fish=entries('Data/Fish');objects=entries('Data/Objects');locations=entries('Data/Locations');require(len(fish)==9,'Nine seafood species expected')
for id,desc in fish.items():
 require(id in objects and objects[id]['Category']==-4,'Fish metadata')
 require(len(desc.split('/'))==(7 if '/trap/' in desc else 14),'Fish field count')
for season in ['spring','summer','fall','winter']:
 pool=[f for f in locations['ArcticPassage_Harbor']['Fish'] if f['Season']==season];require(pool,'No harbor fish '+season)
require(not any(f['ItemId']=='(O)ArcticPassage_Halibut' for f in locations['ArcticPassage_Harbor']['Fish']),'Deepwater fish leaked into harbor')
require(all('ArcticChar' in f['ItemId'] for f in locations['ArcticPassage_Tundra']['Fish']),'Wrong freshwater fish')
require(not any(f['ItemId']=='(O)ArcticPassage_GoldenRedfish' for f in locations['ArcticPassage_Harbor']['Fish']),'Golden redfish leaked into harbor')
require({f['Season'] for f in locations['ArcticPassage_Icefjord']['Fish'] if f['ItemId']=='(O)ArcticPassage_GoldenRedfish'}=={'summer','fall'},'Redfish seasons')
for name,kind in [('Harbor','shrimp'),('Icefjord','crab')]:
 require(locations['ArcticPassage_'+name]['FishAreas']['Default']['CrabPotFishTypes']==[('ap_{{HarborTrapType}}_' if name=='Harbor' else 'ap_crab_')+'{{Season}}'],'Trap area must use isolated seasonal types')
require({'Name':'HarborTrapType','Value':'crab','When':{'Season':'winter'}} in data['DynamicTokens'],'Winter crab access must move to open harbor water')
record('Nine seafood species have rod/trap data, deepwater redfish and isolated seasonal shrimp/crab pools')
recipes=entries('Data/CookingRecipes')
require(len(recipes)==4,'Four meals expected')
for id,raw in recipes.items():
 fields=raw.split('/');require(len(fields)==5 and fields[2]==id,'Cooking recipe output')
 require(objects[id]['Name']==id,'Native recipe learning keys by the output BaseName')
 parts=fields[0].split();require(len(parts)%2==0,'Cooking ingredient pairs')
 for ingredient,count in zip(parts[::2],parts[1::2]):
  require(int(count)>0 and (ingredient.isdigit() or ingredient in objects),'Missing recipe ingredient')
 require(objects[id]['Category']==-7 and objects[id]['Edibility']>0,'Meal nutrition')
 for buff in objects[id]['Buffs']:require(0<buff['Duration']<=240,'Excessive food buff')
for filename,size in [('seafood.png',(144,16)),('cuisine.png',(64,16))]:
 im=Image.open(P/'assets/items'/filename);require(im.mode=='RGBA' and im.size==size,'New icon format')
 for x in range(0,size[0],16):
  alpha=im.crop((x,0,x+16,16)).getchannel('A')
  require(alpha.getbbox() and alpha.getextrema()==(0,255),'Sprite missing opaque silhouette/transparent padding')
record('Four cookable meals have ingredients, bounded buffs and distinct alpha-packed sprites')
quests=entries('Data/Quests')
for season in ['spring','summer','fall','winter']:
 q='ArcticPassage_Arrival';seen=set()
 while q!='-1':
  require(q not in seen,'Quest cycle');require(q in quests,'Missing follow-up '+q);seen.add(q);parts=quests[q].split('/');require(len(parts)>=9,'Quest format');q=parts[5].replace('{{Season}}',season).replace('{{MapSeason}}',season)
 require(len(seen)>=4,'Quest chain too short')
record('Four season-specific starts each lead through a complete six-quest chain without cycles')
shops=entries('Data/Shops');orders=shops['ArcticPassage_Orders']['Items'];require(len(orders)==12,'Four seasons x three orders')
for o in orders:
 require(o['AvailableStock']==1 and o['TradeItemAmount']>0,'Unlimited/negative order');raw=objects[o['TradeItemId'][3:]]['Price']*o['TradeItemAmount'];pay=int(o['ActionsOnPurchase'][0].split()[1]);require(raw<pay<raw*1.7,'Order balance')
for order in shops['ArcticPassage_Orders']['Items']:
 flags=[a.split()[2] for a in order['ActionsOnPurchase'] if a.startswith('AddMail Current ')]
 require(len(flags)==1 and all(t in flags[0] for t in ['{{Year}}','{{Season}}','{{Day}}']),'Order receipt must survive reload and be unique per calendar day')
 require('!PLAYER_HAS_MAIL Current '+flags[0] in order['Condition'],'Paid order remains eligible after reload')
record('Daily barter orders consume fish, pay a bounded premium and have a dated persistent stock limit')
processing=entries('Data/Machines')['(BC)ArcticPassage_DryingRack']
require(processing['AdditionalConsumedItems']==[] and processing['OnlyCompleteOvernight'],'Drying must be fuel free and complete overnight')
require(len(processing['OutputRules'])==3,'Drying fish whitelist')
for rule in processing['OutputRules']:
 require(rule['DaysUntilReady']==2 and rule['Triggers'][0]['RequiredCount']==1,'Drying duration/input count')
 product=rule['OutputItem'][0];require(product['CopyQuality'] and product['CopyPrice'],'Drying loses quality or fish value')
 require(product['ItemId'][3:] in objects and objects[product['ItemId'][3:]]['Category']==-26,'Dried product metadata')
 require(product['PriceModifiers'][0]['Amount']==1.4,'Drying value multiplier')
recipe=entries('Data/CraftingRecipes')['ArcticPassage_DryingRack'].split('/')
require(recipe[0]=='388 40 771 15 335 1' and recipe[2]=='ArcticPassage_DryingRack' and recipe[3]=='true','Drying rack recipe cost/output')
for source,size in [('assets/machines/DryingRack.png',(32,32)),('assets/items/processed-fish.png',(48,16))]:
 im=Image.open(P/source);require(im.size==size and im.mode=='RGBA','Processing sprite format')
 require(im.getextrema()[3][0]==0,'Processing sprite needs transparency')
record('Fuel-free two-night drying has a bounded fish whitelist, native recipe, preserved quality and 1.4x base value')
audio=entries('Data/AudioChanges');contexts=entries('Data/LocationContexts')
require(len(audio)==6 and len(contexts)==2,'Missing dedicated Arctic audio/context data')
for id,cue in audio.items():
 music=cue['Category']=='Music'
 require(id.startswith('ArcticPassage_') and cue['Looped'] and cue['Category'] in ['Ambient','Music'],'Audio cue scope/category')
 require(cue['StreamedVorbis']==music,'Long music must stream; WAV ambience must not')
 for source in cue['FilePaths']:
  match=re.fullmatch(r'\{\{AbsoluteFilePath: (assets/audio/[^}]+\.(?:wav|ogg))\}\}',source)
  require(match is not None,'Non-portable audio path')
  if music:
   probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(P/match[1])]))
   stream=probe['streams'][0]
   require(stream['codec_name']=='vorbis' and stream['channels']==2 and stream['sample_rate']=='44100','Music format')
   require(100<float(probe['format']['duration'])<130,'Music duration')
   subprocess.run(['ffmpeg','-v','error','-i',str(P/match[1]),'-f','null','-'],check=True)
  else:
   with wave.open(str(P/match[1]),'rb') as sound:
    require((sound.getnchannels(),sound.getsampwidth(),sound.getframerate())==(2,2,22050),'Audio format')
    require(sound.getnframes()==22050*36,'Audio loop duration')
for id,context in contexts.items():
 require(context['PlayRandomAmbientSounds'] is False and context['Music']==[],'Valley birds/music fallback enabled')
 require(context['DayAmbience'] in audio and context['NightAmbience'] in audio,'Missing polar day/night sound')
for path in (P/'assets/maps').glob('*.tmx'):
 props={p.get('name'):p.get('value') for p in E.parse(path).getroot().findall('./properties/property')}
 require(props.get('LocationContext') in contexts,'Map still inherits valley ambience: '+path.name)
for location in locations.values():
 require(audio[location['MusicDefault']]['Category']=='Music','Location has no dedicated score')
 require(location['Music'][0]['Track']=='ArcticPassage_PolarNightTheme' and location['Music'][0]['Condition']=='TIME 1800 2600','Missing night score')
record('Three ambient loops and three fully decoded streaming scores exist; all maps disable random birds and use dedicated day/night music')
coast=contexts['ArcticPassage_CoastClimate'];tundra=contexts['ArcticPassage_TundraClimate']
require(not coast.get('CopyWeatherFromLocation'),'Coast still inherits valley petals/leaves/green rain')
require(tundra.get('CopyWeatherFromLocation')=='ArcticPassage_CoastClimate','Adjacent Arctic regions must share weather')
for context in contexts.values():
 require(context['AllowRainTotem']==False,'Valley rain totem overrides authored Arctic precipitation')
 require({c['Weather'] for c in context['WeatherConditions']}=={'Sun','Rain','Snow'},'Non-Arctic weather effect leaked into forecast')
 require(context['WeatherConditions'][-1]['Condition'] is None,'Missing deterministic weather fallback')
record('Independent Arctic forecasts exclude valley petals, leaf debris and green rain; coast and tundra share weather')
(R/'docs/StaticTestResults.txt').write_text('\n'.join('PASS '+p for p in passed)+'\n')
