"""R03 fixed inland dog-team route, native quest items, and original pixel animation."""
from pathlib import Path
from PIL import Image,ImageDraw
import json,random
R=Path(__file__).resolve().parents[1];P=R/'ContentPack';A=R/'Code/ArcticPassage/Runtime/assets/sled'
def main():
 A.mkdir(parents=True,exist_ok=True)
 # Broad muzzle, erect ears, deep chest and curled tail: working spitz silhouettes.
 im=Image.new('RGBA',(160,28))
 for f in range(4):
  d=ImageDraw.Draw(im);x=f*40;step=[0,3,0,-3][f]
  d.ellipse((x+4,22,x+34,26),fill='#59798b66')
  d.polygon([(x+7,14),(x+4,8),(x+5,3),(x+10,2),(x+13,5),(x+10,8),(x+8,6),(x+8,10),(x+13,12)],fill='#d9d9cd',outline='#425563')
  d.polygon([(x+9,12),(x+17,9),(x+27,11),(x+30,17),(x+25,21),(x+13,20),(x+8,17)],fill='#c9cec9',outline='#3e5463')
  d.polygon([(x+10,12),(x+18,10),(x+24,12),(x+20,16),(x+13,16)],fill='#6a7e87')
  for bx,dy in [(12,step),(23,-step)]:
   d.line((x+bx,18,x+bx+dy,23,x+bx+dy+3,23),fill='#e5e4d6',width=2)
  d.polygon([(x+23,11),(x+25,5),(x+26,1),(x+29,5),(x+32,2),(x+33,8),(x+37,10),(x+37,13),(x+31,15),(x+27,18)],fill='#e2e1d2',outline='#425563')
  d.polygon([(x+26,4),(x+27,2),(x+28,5)],fill='#63727a');d.polygon([(x+31,5),(x+32,3),(x+32,7)],fill='#63727a')
  d.rectangle((x+29,8,x+32,10),fill='#617680');d.point((x+33,9),fill='#263f4e');d.rectangle((x+36,10,x+38,11),fill='#263e4b')
  d.line((x+24,14,x+27,17,x+20,19,x+16,12),fill='#b85749',width=2)
 im.save(A/'dogs.png')
 im=Image.new('RGBA',(80,40));d=ImageDraw.Draw(im)
 d.ellipse((5,29,76,38),fill='#516f8366')
 for y in (29,35):
  d.line((4,y,65,y,74,y-6,76,y-11),fill='#344c5c',width=3)
  d.line((5,y-1,65,y-1,72,y-6,74,y-11),fill='#c1a06d',width=2)
 for x in range(13,65,6):d.line((x,23,x,32),fill='#a98156',width=2)
 d.polygon([(9,18),(57,18),(68,25),(14,27)],fill='#927149',outline='#3d4c51')
 d.line((9,18,7,9,11,5,16,17),fill='#c3a477',width=2)
 d.rectangle((20,14,47,23),fill='#a94f49',outline='#374d59');d.line((23,16,44,16),fill='#cc8b68')
 for x in (17,57):d.line((x,20,x,30),fill='#dcc393',width=2)
 d.line((64,25,73,25),fill='#a98760');im.save(A/'sled.png')
 im=Image.new('RGB',(640,140),'#c9dce4');d=ImageDraw.Draw(im);rr=random.Random(7303)
 d.polygon([(0,40),(80,26),(180,42),(300,20),(430,37),(540,23),(640,40),(640,140),(0,140)],fill='#e1ebe8')
 d.polygon([(0,86),(160,78),(300,83),(450,74),(640,79),(640,105),(430,100),(230,108),(0,109)],fill='#b3cbda')
 for _ in range(450):
  x=rr.randrange(640);y=rr.randrange(140);d.line((x,y,x+rr.randrange(2,10),y),fill=rr.choice(['#e7eeeb','#abc3d2','#d4e3e7']))
 for x,y in [(45,31),(270,24),(490,33)]:
  d.polygon([(x,y),(x+12,y-8),(x+27,y-4),(x+39,y+7),(x+29,y+11),(x+5,y+9)],fill='#566f7f');d.line((x+12,y-8,x+26,y-4,x+36,y+4),fill='#dce8e6',width=2)
 im.save(A/'ground.png')
 item=Image.new('RGBA',(32,16));d=ImageDraw.Draw(item)
 d.line((2,12,11,3),fill='#ae8658',width=3);d.polygon([(8,2),(11,0),(15,4),(12,6)],fill='#99b7c1',outline='#304c60')
 d.rectangle((18,4,30,14),fill='#9b7550',outline='#3a5261');d.line((19,6,29,6),fill='#d2bc8d');d.line((24,4,24,14),fill='#647c83',width=2)
 item.save(P/'assets/items/sled-quest.png')
 p=P/'content.json';c=json.loads(p.read_text());c['Changes']=[x for x in c['Changes'] if not x.get('LogName','').startswith('R03 sled: ')]
 def patch(action,target,**kw):c['Changes'].append(dict(LogName='R03 sled: '+target,Action=action,Target=target,**kw))
 patch('Load','Mods/WhiteBay.ArcticPassage/SledQuest',FromFile='assets/items/sled-quest.png')
 objects={}
 for i,key in enumerate(['SledTool','SledSupply']):objects['ArcticPassage_'+key]={'Name':'ArcticPassage_'+key,'DisplayName':'{{i18n:sled.item.'+str(i)+'.name}}','Description':'{{i18n:sled.item.'+str(i)+'.desc}}','Type':'Basic','Category':-999,'Price':0,'Edibility':-300,'Texture':'Mods/WhiteBay.ArcticPassage/SledQuest','SpriteIndex':i,'CanBeGivenAsGift':False,'CanBeTrashed':False,'ExcludeFromFishingCollection':True,'ExcludeFromShippingCollection':True}
 patch('EditData','Data/Objects',Entries=objects)
 for name,x,y in [('Tundra',28,38),('WinterCamp',13,23),('Glacier',30,25),('SledTrail',29,27)]:
  patch('EditMap','Maps/ArcticPassage_'+name,MapTiles=[{'Position':{'X':x,'Y':y},'Layer':'Buildings','SetProperties':{'Action':'ArcticPassageSled'}}])
 texts={
 'season':('The dog-team route opens in winter. Marked walking trails remain open in other seasons.','犬队线路只在冬季开放。其他季节仍可沿标记步道往返。'),
 'single':('Dog-team travel is currently available in single-player. Please use the marked walking trail in multiplayer.','犬队交通当前仅开放单人体验。联机时请沿标记步道往返。'),
 'locked':('Mira: Help the harbor repair the processing shed first; then we can prepare the winter route together.','米拉：先帮助港口修好加工棚，再一起准备冬季路线吧。'),
 'tools':('Mira: My lashing tool was left beside the parked sled on the mountain trail. Check the station marker there, then bring it to the tundra stop.','米拉：我把绑扎工具落在山路的木雪橇旁了。请检查那里的站点标记，再带回苔原停靠处。'),
 'toolFound':('You found the lashing tool. Return it at the tundra stop.','你找到了绑扎工具。请带回苔原停靠处。'),
 'toolsDone':('The equipment yard is in order. Use the tundra, camp or glacier stop to arrange a journey.','装备场已整理妥当。请在苔原、营地或冰川站安排出行。'),
 'supplies':('Mira: Thank you. Collect the packed supplies at the field-camp sign and bring them back to the tundra stop.','米拉：谢谢。请到营地说明牌领取已装箱的补给，再带回苔原停靠处。'),
 'supplyFound':('The packed supplies are in your bag. Bring them to the tundra stop.','已装箱的补给放进了背包。请送到苔原停靠处。'),
 'repair':('Mira: The last job is the stop repair. Bring 20 wood and 5 fiber to the tundra stop for the rail and lashings.','米拉：最后要修好停靠处。请带20木材和5纤维到苔原站，用来修栏杆和绑扎。'),
 'repairConfirm':('Use 20 wood and 5 fiber to repair the tundra stop?','使用20木材和5纤维修好苔原停靠处？'),
 'trial':('Mira: Everything is checked. Take the first route from the tundra stop to the field camp; then all three winter stops will open.','米拉：装备都检查好了。从苔原站试乘到营地吧，抵达后开放三个冬季站点。'),
 'choose':('Mira: The team is ready. Where shall we go?','米拉：犬队准备好了。我们去哪里？'),
 'stop0':('Tundra edge','苔原边缘'),'stop1':('Winter field camp','冬季营地'),'stop2':('Glacier lookout','冰川观测站'),
 'cancel':('Stay here','暂不出发'),'full':('Please leave one empty bag slot for the equipment.','请先在背包中留出一格放装备。'),
 'unavailable':('The route is not ready. You can still return by the marked walking trail.','路线暂不可用，仍可沿标记步道返程。'),
 'unlocked':('First journey completed. All three winter dog-team stops are open.','首次试乘完成，三个冬季犬队站已开放。'),
 'skip':('Esc: continue to the destination','Esc：直接抵达目的地'),
 'item.0.name':('Lashing tool','雪橇绑扎工具'),'item.0.desc':('Mira left it beside the parked sled. Return it at the tundra stop.','米拉落在木雪橇旁的工具，请送回苔原停靠处。'),
 'item.1.name':('Packed trail supplies','山路补给箱'),'item.1.desc':('Packed at the field camp. Deliver it to the tundra stop.','营地装好的补给，请送往苔原停靠处。')}
 quests={}
 for q,key,title in [('Tools','tools',('The missing lashing tool','遗落的绑扎工具')),('Supplies','supplies',('Supplies for the trail','送往山路的补给')),('Repair','repair',('A sound winter stop','修好冬季停靠处')),('Trial','trial',('The first dog-team journey','第一次犬队出行'))]:
  texts['quest.'+q]=title
  quests['ArcticPassage_Sled'+q]='/'.join(['Basic','{{i18n:sled.quest.'+q+'}}','{{i18n:sled.'+key+'}}','{{i18n:sled.'+key+'}}','','-1','0','-1','false'])
 patch('EditData','Data/Quests',Entries=quests)
 for lang,n in [('default',0),('zh',1)]:
  for path in [P/f'i18n/{lang}.json',R/f'Code/ArcticPassage/Runtime/i18n/{lang}.json']:
   data=json.loads(path.read_text());data.update({'sled.'+k:v[n] for k,v in texts.items()});path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
 p.write_text(json.dumps(c,ensure_ascii=False,indent=2)+'\n')
 print('Built fixed winter dog-team candidate: three stops, four native quests, two quest items, original four-frame spitz animation; no additional map.')
if __name__=='__main__':main()
