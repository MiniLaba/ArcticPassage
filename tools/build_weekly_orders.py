"""R01 native weekly contracts; separate board type, no save edits."""
from pathlib import Path
import json
R=Path(__file__).resolve().parents[1];P=R/'ContentPack';TAG='R01 weekly: '
def dump(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def main():
 c=json.loads((P/'content.json').read_text());c['Changes']=[x for x in c['Changes'] if not x.get('LogName','').startswith(TAG)]
 texts={l:json.loads((P/f'i18n/{l}.json').read_text()) for l in ('default','zh')}
 def tr(k,en,zh):
  for l,v in [('default',en),('zh',zh)]:texts[l][k]=v
  return '{{i18n:'+k+'}}'
 def patch(action,target,**kw):c['Changes'].append(dict(Action=action,Target=target,LogName=TAG+target,**kw))
 # Fish objective receives native rod catches, not inventory grants or resales.
 rods={'PolarCod','Capelin','AtlanticCod','ArcticChar','Wolffish','Halibut','GoldenRedfish'}
 for p in c['Changes']:
  if p.get('Target')!='Data/Objects':continue
  for n,v in p.get('Entries',{}).items():
   if n.removeprefix('ArcticPassage_') in rods:
    tags=v.setdefault('ContextTags',[])
    if 'arcticpassage_rod_fish' not in tags:tags.append('arcticpassage_rod_fish')
 orders={}
 for name,kind,count,reward,en,zh,descen,desczh,objen,objzh in [
  ('CoastalLog','Fish',6,600,'A week along the coast','近岸鱼情记录','Catch six northern rod fish before Sunday ends. Only catches made after accepting count. Keep the fish for sale or processing. —Ada','在本周日结束前，钓获6条北方钓竿鱼。只统计接单后的实际钓获；鱼可自行出售或加工。——艾达','Catch 6 northern rod fish after accepting.','接单后实际钓获6条北方钓竿鱼。'),
  ('FreshCrates','Donate',6,650,'The guesthouse fish crate','旅舍一周鲜鱼','Put six northern rod fish in the crate below the community noticeboard before Sunday ends. Any species, quality or mixture is accepted; partial deliveries are kept. Confirm by closing the crate. —Ada','在本周日结束前，向社区屋公告栏左下的鲜鱼箱投入6条北方钓竿鱼。不限鱼种和品质，可以分批混交；关闭箱子确认交付。——艾达','Put 6 northern rod fish in the community fish crate.','向社区屋鲜鱼箱投入6条北方钓竿鱼。')]:
  dat={'AcceptedContextTags':'arcticpassage_rod_fish'}
  if kind=='Donate':dat.update(DropBox='ArcticPassage_FishCrate',DropBoxGameLocation='ArcticPassage_CommunityHouse',DropBoxIndicatorLocation='3 5',MinimumCapacity='9')
  orders['ArcticPassage_'+name]={'Name':tr('weekly.'+name+'.name',en,zh),'Requester':'ArcticPassage_Ada','Duration':'Week','Repeatable':True,'Condition':'PLAYER_HAS_MAIL Host ArcticPassage_Shed','OrderType':'ArcticPassage_Weekly','Text':tr('weekly.'+name+'.desc',descen,desczh),'Objectives':[{'Type':kind,'Text':tr('weekly.'+name+'.objective',objen,objzh),'RequiredCount':str(count),'Data':dat}],'Rewards':[{'Type':'Money','Data':{'Amount':str(reward)}}]}
 # Story orders use the same native board, but unlock only at their chapter step.
 orders['ArcticPassage_StormSupplies']={
  'Name':tr('story.order.supplies.name','Gale-ready community stores','风雪前的社区补给'),
  'Requester':'ArcticPassage_Ada','Duration':'Week','Repeatable':True,
  'Condition':'PLAYER_HAS_MAIL Current ArcticPassage_StormSuppliesUnlocked, !PLAYER_HAS_MAIL Current ArcticPassage_StormSuppliesComplete',
  'OrderType':'ArcticPassage_Story',
  'Text':tr('story.order.supplies.desc','The community team needs 20 fiber for spare lashings before the next gale. Donate it to the shared box below the noticeboard.','下一场风雪前，社区团队需要20份纤维制作备用绑带。请交到公告板下方的共享补给箱。'),
  'Objectives':[{'Type':'Donate','Text':tr('story.order.supplies.objective','Donate 20 fiber to the community supply box.','向社区补给箱交付20份纤维。'),'RequiredCount':'20','Data':{'AcceptedContextTags':'id_o_771','DropBox':'ArcticPassage_StormSupplies','DropBoxGameLocation':'ArcticPassage_CommunityHouse','DropBoxIndicatorLocation':'3 5','MinimumCapacity':'24'}}],
  'Rewards':[{'Type':'Money','Data':{'Amount':'100'}}]
 }
 orders['ArcticPassage_StormFish']={
  'Name':tr('story.order.fish.name','Fresh catch before the gale','风雪前的鲜鱼'),
  'Requester':'ArcticPassage_Ada','Duration':'Week','Repeatable':True,
  'Condition':'PLAYER_HAS_MAIL Current ArcticPassage_StormFishUnlocked, !PLAYER_HAS_MAIL Current ArcticPassage_StormFishComplete',
  'OrderType':'ArcticPassage_Story',
  'Text':tr('story.order.fish.desc','Ada needs one fresh northern rod fish for the community kitchen. Only a catch made after accepting this order counts.','艾达需要一条新鲜北方钓竿鱼送到社区厨房；只统计接单后实际钓获的鱼。'),
  'Objectives':[{'Type':'Fish','Text':tr('story.order.fish.objective','Catch one northern rod fish after accepting.','接单后用钓竿实际钓获一条北方鱼。'),'RequiredCount':'1','Data':{'AcceptedContextTags':'arcticpassage_rod_fish'}}],
  'Rewards':[{'Type':'Money','Data':{'Amount':'120'}}]
 }
 patch('EditData','Data/SpecialOrders',Entries=orders)
 # Reuse the community noticeboard, preserving all four main interiors.
 patch('EditMap','Maps/ArcticPassage_CommunityHouse',MapTiles=[{'Position':{'X':5,'Y':5},'Layer':'Buildings','SetProperties':{'Action':'ArcticPassageWeekly'}},{'Position':{'X':3,'Y':5},'Layer':'Buildings','SetProperties':{'Action':'ArcticPassageFishCrate'}}])
 for l,v in texts.items():dump(P/f'i18n/{l}.json',v)
 dump(P/'content.json',c)
 print('Built two native weekly contracts on the existing community board; 7 rod fish tagged; no seasonal item lock.')
if __name__=='__main__':main()
