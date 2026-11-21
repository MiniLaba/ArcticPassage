from pathlib import Path
import json
R=Path(__file__).resolve().parents[1]
rows=[
('invitation',0,6,'title','A little further north.','再往北，一点。','一张机票，走进北方的日常。',False,'src/product/WindowFlight.tsx'),
('landing',6,12,'workspace','Touch down in the north.','月月鸟航空，带你抵达。','从山谷出发，在雪跑道降落。',True,'evidence/product-source/AirTravel.cs'),
('town',12,19,'workspace','Make a home in the north.','把日常，过到北极去。','彩屋、岩岸，还有一处等你入住的暖房。',True,'evidence/product-source/DevelopmentStatus.md'),
('fishing',19,27,'detail','Between ice and water.','在冰与海之间，等一尾鱼。','在冰洞与港湾抛竿，带回寒水里的渔获。',True,'public/media/catch.webp'),
('harbour',27,33,'detail','A working harbour.','今天的渔获，明天的烟火。','加工渔获，让小小的港口忙碌起来。',True,'public/media/smoke.webp'),
('neighbours',33,41,'workspace','The people of the bay.','每一扇暖窗，都有一段故事。','六位邻居，六种认识北方的方式。',True,'evidence/product-source/DevelopmentStatus.md'),
('beyond',41,47,'workspace','Follow the snow.','沿着雪痕，去更远的地方。','解锁犬橇，沿山路抵达冬季营地。',True,'evidence/product-source/SledTravel.cs'),
('seasons',47,52,'workspace','One bay. Four seasons.','一整个海湾，一整年的日常。','冬、春、夏、秋，海湾有不同的颜色。',True,'public/media/winter.webp'),
('night',52,56,'title','A light left on for you.','长夜里，也有一盏灯。','',False,'public/media/night.webp'),
('home',56,60,'end','Frosthavn','霜灯港','开启你的北方旅程',False,None)]
shots=[]
for id,start,end,kind,en,zh,desc,claim,source in rows:
 shots.append(dict(id=id,start=start,end=end,type=kind,headlineEn=en,headline=zh,description=desc,plainExplanation=desc,descriptionAt=0,claim=claim,source=['file:'+source] if source else [],component='src/product/WindowFlight.tsx' if id=='invitation' else 'src/shots/frosthavn.jsx',actions=[]))
actions=[('landing','engine',0,'原生飞机开始下降','engine',0),('landing','touchdown',3,'飞机滑雪架接地','snow',0),('fishing','cast-water',.4,'实际抛竿画面进入','water',0),('fishing','catch-fish',5.2,'真实北极鳕钓获画面进入','chime',0),('harbour','wood-room',3,'进入实际加工收取画面','wood',0),('neighbours','meet-people',.2,'第一对居民肖像进入','paper',0),('beyond','sled-glide',.2,'原生犬橇开始行进','snow',0),('seasons','season-spring',1.25,'原生春季地图展开','softbell',0),('home','brand-resolve',.1,'霜灯港最终落版','resolve',0)]
cues=[]
for sid,id,at,action,sound,offset in actions:
 s=next(x for x in shots if x['id']==sid);s['actions'].append(dict(id=id,at=at,action=action,soundRequired=True))
 file='assets/sfx/'+sound+'.wav'
 lmfile=R/'evidence/sfx-landmarks.json'
 if lmfile.exists():
  landmarks=json.loads(lmfile.read_text());lm=next(x for x in landmarks if x['file']==file);offset=lm['peak'] if sound=='paper' else lm['onset']
 cues.append(dict(actionId=id,at=round(s['start']+at-offset,4),syncOffset=offset,file=file,gain=.65 if sound=='engine' else 1.3,role='sfx',kind='resolve' if sound in ['chime','resolve'] else 'whoosh' if sound=='paper' else sound))
plan=dict(demo=False,product='霜灯港 · 再往北，一点',style='repo',width=1920,height=1080,fps=30,duration=60,repo='.',scope=dict(versions='Published 0.7.10 overall introduction',platforms=['PC single-player mod'],excludes=['mobile','multiplayer','Windows in-game compatibility assurance'],userConfirmed='2026-10-28: 按推荐方案制作'),audioRequired=True,sfxRequired=True,typography=dict(mode='bilingual',zhFont='PingFang SC',enFont='Cormorant Garamond / DM Sans',zhStyle='sans-serif'),shots=shots,audio=dict(beatGrid=dict(bpm=72,offset=0),music=dict(file='assets/music.wav',gain=.75),ducking=dict(enabled=True),cues=cues))
(R/'plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n')
evidence=[]
for s in shots:
 evidence.append(dict(shotId=s['id'],featureEntry=s['source'],components=[s['component']],reuseMode='direct-product-component' if s['id']=='invitation' else 'native-animation-display-adapter' if s['id']=='landing' else 'authentic-native-capture-and-map-assets',styleEntries=['../FrosthavnWebsite/src/ScrollJourney.css'] if s['id']=='invitation' else ['src/film.css'],stateDriver='deterministic film seek',exceptions='C#/MonoGame cannot run inside browser. Original drawing equations and textures are retained; this is a faithful video adapter, not a running game.' if s['id']=='landing' else 'Promotional camera/layout over existing artwork and authentic captures; no new gameplay state is claimed.'))
(R/'evidence/component-usage.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+'\n')
(R/'evidence/feature-evidence.json').write_text(json.dumps([dict(feature=s['headline'],benefit=s['description'],release='0.7.10',status='published implementation; evidence limits in DevelopmentStatus.md',source=s['source'],limits='No claim of complete story playthrough, yearly festival playthrough, multiplayer or Windows game execution.') for s in shots if s['claim']],ensure_ascii=False,indent=2)+'\n')
