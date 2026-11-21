# coding: utf-8
"""Two restrained outer-graphic transitions; native pictures are never recreated."""
from pathlib import Path
import io,json,math,subprocess
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[1];O=R/'renders/mg-v5';O.mkdir(exist_ok=True)
events=[
 {'id':'water-line','start':50.15,'duration':.8,'points':[[300,650],[430,365],[710,335],[815,605]],'meaning':'The printed flight arc returns as a brief line over empty water, away from the player and fishing UI.'},
 {'id':'inland-trail','start':97.7,'duration':.9,'points':[[112,272],[288,284],[430,165],[695,211]],'meaning':'A short trail leads out of the winter panorama into the inland chapter, above native dialogue and left of narration.'}
]
def cubic(p,t):return tuple((1-t)**3*p[0][i]+3*(1-t)**2*t*p[1][i]+3*(1-t)*t*t*p[2][i]+t**3*p[3][i]for i in [0,1])
for e in events:
 path=O/(e['id']+'.mov');p=subprocess.Popen(['ffmpeg','-y','-v','error','-f','image2pipe','-vcodec','png','-r','30','-i','-','-an','-c:v','qtrle','-pix_fmt','argb',str(path)],stdin=subprocess.PIPE)
 for n in range(round(e['duration']*30)):
  t=n/(e['duration']*30-1);q=t*t*(3-2*t);alpha=min(1,t/.15,(1-t)/.22)*.78;im=Image.new('RGBA',(3840,2160));a=ImageDraw.Draw(im)
  pts=[tuple(v*2 for v in cubic(e['points'],j/120))for j in range(max(2,round(q*120)))]
  a.line(pts,fill=(235,204,153,round(alpha*255)),width=3)
  x,y=cubic(e['points'],q);a.ellipse(((x-2.2)*2,(y-2.2)*2,(x+2.2)*2,(y+2.2)*2),fill=(245,223,183,round(alpha*255)))
  im=im.resize((1920,1080),Image.Resampling.LANCZOS);b=io.BytesIO();im.save(b,format='PNG');p.stdin.write(b.getvalue())
 p.stdin.close()
 if p.wait():raise RuntimeError('Transition encoding failed')
 e['file']=str(path.relative_to(R));e['fps']=30;e['nativePixelsRecreated']=False
(R/'evidence/v5-line-transitions.json').write_text(json.dumps(events,ensure_ascii=False,indent=2));print('Two line transitions rendered')
