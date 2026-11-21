from pathlib import Path
from PIL import Image,ImageDraw
import subprocess,json
R=Path(__file__).resolve().parents[1];V=R/'renders/Frosthavn-再往北一点-1080p.mp4';O=R/'evidence/final-frames';O.mkdir(parents=True,exist_ok=True)
def ff(*args):subprocess.run(['ffmpeg','-v','error','-y',*map(str,args)],check=True)
ff('-i',V,'-vf','fps=2,scale=384:216','-q:v','2',O/'frame-%03d.jpg')
frames=sorted(O.glob('frame-*.jpg'))
for part in range(3):
 sheet=Image.new('RGB',(1536,2400),'#132c39');d=ImageDraw.Draw(sheet)
 for i,p in enumerate(frames[part*40:(part+1)*40]):
  x=i%4*384;y=i//4*240;sheet.paste(Image.open(p),(x,y));d.text((x+9,y+219),f'{part*20+i*.5:05.1f}s',fill='white')
 sheet.save(R/f'evidence/final-contact-{part+1:02d}.jpg',quality=92)
cuts=[6,12,19,22,24.2,27,30,33,35.667,38.333,41,44,47,48.25,49.5,50.75,52,56]
for i,t in enumerate(cuts):
 ff('-ss',max(0,t-.4),'-t',1,'-i',V,'-vf','fps=10,scale=320:180,tile=10x1','-frames:v',1,R/f'evidence/cut-{i+1:02d}-{t:.3f}.jpg')
for part in range(3):
 sheet=Image.new('RGB',(3200,1212),'#132c39');d=ImageDraw.Draw(sheet)
 for j,t in enumerate(cuts[part*6:(part+1)*6]):
  n=part*6+j;file=R/f'evidence/cut-{n+1:02d}-{t:.3f}.jpg';sheet.paste(Image.open(file),(0,j*202));d.text((8,j*202+182),f'cut {t:.3f}s / 10fps',fill='white')
 sheet.save(R/f'evidence/final-transitions-{part+1:02d}.jpg',quality=93)
for t in [0,9.5,15,24.7,31,34.2,37.2,39.4,42.5,45.7,49.8,54.5,58,59.9]:ff('-ss',t,'-i',V,'-frames:v',1,O/f'full-{t:04.1f}.png')
print(json.dumps(dict(contactFrames=len(frames),transitionStrips=len(cuts),fullSizeFrames=14)))
