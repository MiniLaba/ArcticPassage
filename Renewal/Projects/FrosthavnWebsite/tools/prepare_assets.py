"""Website assets from the user's code-drawn town plan and real game captures.
No model-generated imagery, external photos, or personal ticket information.
"""
from pathlib import Path
from PIL import Image
import json,shutil
R=Path(__file__).resolve().parents[1];MOD=R.parent/'ArcticPassage';A=R/'public/assets';A.mkdir(parents=True,exist_ok=True)
source=MOD/'art/ephemera/frosthavn-v3/frosthavn-v4/Frosthavn-winter-pixel-back.png'
im=Image.open(source).convert('RGB').resize((2030,826),Image.Resampling.NEAREST)
im.save(A/'frosthavn-day.webp',lossless=True)
# Discrete palette transforms preserve the existing pixel grid; warm lit windows stay lit.
night=im.copy();p=night.load();sp=im.load()
for y in range(im.height):
 for x in range(im.width):
  r,g,b=sp[x,y]
  if r>170 and r>g*.96 and g>115 and b<175 and r>b*1.2:p[x,y]=(min(255,int(r*1.13)),min(235,int(g*1.08)),int(b*.88))
  else:p[x,y]=(int(r*.39+5),int(g*.49+5),int(b*.64+7))
night.save(A/'frosthavn-dusk.webp',lossless=True)
shots={'ice-fishing':MOD/'previews/InGame_R03_ice_native_cast.jpg','dog-team':MOD/'previews/InGame_R03_sled_trip.jpg'}
for key,p in shots.items():
 im=Image.open(p).convert('RGB');w,h=im.size;im=im.crop((0,int(h*.03),w,h));im.thumbnail((1440,1000));im.save(A/(key+'.webp'),quality=84)
for key in ['Airstrip','Harbor','WinterCamp','Glacier']:
 p=MOD/f'Code/ArcticPassage/Runtime/assets/guide/{key}_winter.png'
 im=Image.open(p).convert('RGB');im.save(A/(key.lower()+'.webp'),lossless=True)
shutil.copy2(MOD/'Code/ArcticPassage/Runtime/assets/flight/plane.png',A/'plane.png')
# Original nine-species sprite sheet remains at its native grid.
sea=MOD/'ContentPack/assets/items/seafood.png'
if not sea.exists():
 for p in (MOD/'ContentPack/assets/items').glob('*'):
  if 'seafood' in p.name.lower():sea=p;break
if sea.exists():shutil.copy2(sea,A/'seafood.png')
(A/'moonbird.svg').write_text('''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><path d="M45 8A25 25 0 1 0 55 43 22 22 0 0 1 45 8Z" fill="currentColor"/><path d="m21 34 8-5 8 5 11-7" stroke="currentColor" stroke-width="3" fill="none" stroke-linecap="round"/></svg>''')
(A/'favicon.svg').write_text('''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="15" fill="#183c44"/><path d="M44 11A23 23 0 1 0 52 44 21 21 0 0 1 44 11Z" fill="#f0eadc"/><path d="m21 34 8-5 8 5 10-7" stroke="#d6a77a" stroke-width="3" fill="none" stroke-linecap="round"/></svg>''')
credits={'town':'Code-drawn Frosthavn winter overall plan from the user-approved boarding-pass reverse; adapted as an artistic website panorama, not an exact game map.','captures':'Actual local Stardew Valley 1.6.15 mod windows; isolated QA character, not a claim of ordinary unlock progression.','plane':'Project code-drawn aircraft sprite.','newAssets':'All website adaptation uses code; no new AI imagery.','modVersion':'0.7.9 development preview'}
credits.update(json.loads((R/'docs/ASSETS.json').read_text()) if (R/'docs/ASSETS.json').exists() else {})
(R/'docs/ASSETS.json').write_text(json.dumps(credits,ensure_ascii=False,indent=2)+'\n')
print('Prepared original code art, dusk palette and real QA screenshots:',sum(p.stat().st_size for p in A.iterdir()),'bytes')

# Keep the upgrade assets reproducible alongside the original panorama.
import runpy
runpy.run_path(str(R/'tools/prepare_upgrade_assets.py'))
