from pathlib import Path
from PIL import Image
import shutil,json

R=Path(__file__).resolve().parents[1]; B=R.parent
out=R/'public/media';out.mkdir(parents=True,exist_ok=True)
sources=[]
def pic(name,source,kind):
 p=B/source
 if not p.exists() and source.endswith('Town_fall.png'):p=B/'.development/RuntimeMod/assets/guide/Town_fall.png';source=str(p.relative_to(B))
 im=Image.open(p).convert('RGB');im.thumbnail((2560,1800),Image.Resampling.LANCZOS)
 target=out/(name+'.webp');im.save(target,quality=94,method=6)
 sources.append(dict(file=str(target.relative_to(R)),source=source,kind=kind,width=im.width,height=im.height))
for name,file in [('town','Town_winter.png'),('winter','Town_winter.png'),('spring','Town_spring.png'),('summer','Town_summer.png'),('fall','Town_fall.png'),('harbour','Harbor_winter.png'),('night','InGame_Harbor_night_072.jpg'),('cast','InGame_R03_ice_native_cast.jpg'),('tutorial','InGame_Starter_fishing_tutorial_078.jpg'),('smoke','InGame_R01_smoked_cod_collected.jpg'),('camp','InGame_R03_sled_final_arrival.jpg')]:
 pic(name,'ArcticPassage/previews/'+file,'native-screenshot' if file.startswith('InGame') else 'game-map-render')
pic('catch','ArcticPassage/docs/InGame_R01_visual_native_catch.png','native-screenshot')
for name in ['ada','mira','roan']:
 pic(name,'FrosthavnWebsite/public/assets/experience/portrait-'+name+'-original.webp','retained-portrait-source')
for name in ['nora','levin','amma']:
 pic(name,'ArcticPassage/art/source/code-portraits/portrait-'+name+'.png','code-drawn-portrait-source')
for folder in ['flight','sled']:
 for p in (B/'.development/RuntimeMod/assets'/folder).glob('*.png'):
  dest=out/folder/p.name;dest.parent.mkdir(exist_ok=True);shutil.copy2(p,dest)
  sources.append(dict(file=str(dest.relative_to(R)),source=str(p.relative_to(B)),kind='native-runtime-texture'))
# Unchanged product component uses this root path.
dest=R/'public/assets/experience';dest.mkdir(parents=True,exist_ok=True)
shutil.copy2(B/'FrosthavnWebsite/public/assets/experience/original-bay.webp',dest/'original-bay.webp')
for file in ['moonbird.svg','fonts/dm-sans-latin-400-normal.woff2','fonts/dm-sans-latin-600-normal.woff2','fonts/cormorant-garamond-latin-400-normal.woff2','fonts/cormorant-garamond-latin-500-italic.woff2']:
 p=R/'public/assets'/file;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(B/'FrosthavnWebsite/public/assets'/file,p)
for p in (B/'FrosthavnWebsite/public/assets').glob('*OFL*'):shutil.copy2(p,R/'public/assets'/p.name)
sources.append(dict(file='public/assets/experience/original-bay.webp',source='FrosthavnWebsite/public/assets/experience/original-bay.webp',kind='website-panorama-illustration-not-exact-game-map'))
(R/'evidence/asset-sources.json').write_text(json.dumps(sources,ensure_ascii=False,indent=2)+'\n')
print('Prepared',len(sources),'tracked visual sources')
