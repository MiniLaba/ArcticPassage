"""Recover retained artwork for the player website; does not rebuild game files."""
from pathlib import Path
from PIL import Image,ImageEnhance
import json,argparse
R=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--mod',type=Path,default=R.parent/'ArcticPassage')
M=parser.parse_args().mod.resolve();A=R/'public/assets/experience';A.mkdir(exist_ok=True)
pan=M/'art/ephemera/frosthavn-v3/frosthavn-v4/Frosthavn-winter-pixel-back.png'
Image.open(pan).convert('RGB').save(A/'original-bay.webp',quality=95,method=6)
for name in ['Ada','Mira','Roan']:
 im=Image.open(M/f'art/source/portrait-{name}-master.png').convert('RGB')
 im.crop((0,0,im.width//2,im.height//3)).save(A/f'portrait-{name.lower()}-original.webp',quality=96,method=6)
for s in ['winter','spring','summer','fall']:
 Image.open(M/f'art/source/town-{s}-master.png').convert('RGB').save(A/f'town-{s}.webp',quality=92,method=6)
for name,scene in [('harbour','Harbor'),('camp','WinterCamp'),('glacier','Glacier')]:
 Image.open(M/f'ContentPack/assets/maps/{scene}_winter_scene.png').convert('RGB').save(A/f'{name}.webp',quality=93,method=6)
(A/'sources.json').write_text(json.dumps({'panorama':str(pan.relative_to(M)),'portraits':'Retained 1024×1536 source; original first512×512 expression. No upscaling.','seasons':'Four retained town masters1448×1086, used by scene_maps.py for the actual game town.','buildings':'Same roof/facade/shore artwork as ContentPack, no substitute house models.','calls':'No new generated imagery'},indent=2)+'\n')
print('Restored original panorama, three512px portraits and four original town seasons.')
