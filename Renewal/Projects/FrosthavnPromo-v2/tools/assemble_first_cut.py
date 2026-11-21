"""Reproducible 60s first cut: original CG + actual native game video, no gameplay stills."""
import subprocess,json,concurrent.futures,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1]; C=R/'renders/film-cards'; O=R/'renders/first-cut-parts';O.mkdir(exist_ok=True)
raw=R/'raw/gameplay'
shots=[
 ('paper',R/'renders/Frosthavn-航空折纸动效-轻纸声版-6s.mp4',0,6,None),
 ('flight',raw/'20261029-030129-flight-arrival-real.mov',5,4,None),
 ('landing',raw/'20261029-030129-flight-arrival-real.mov',14,5,None),
 ('arrival',raw/'20261029-025523-town-real.mov',1,7,'arrival'),
 ('fishing',raw/'20261029-030741-fishing-shore-real.mov',2,8,'fishing'),
 ('harbour',raw/'20261029-025431-harbor-real.mov',2,6,None),
 ('neighbours',raw/'20261029-030324-guesthouse-real.mov',6,6,None),
 ('fjord',raw/'20261029-025649-icefjord-real.mov',2,6,'fjord'),
 ('night',raw/'20261029-030007-town-night-real.mov',1,7,None),
]
def run(a):subprocess.run(['ffmpeg','-y','-hide_banner','-loglevel','error']+list(map(str,a)),check=True)
def make(item):
 i,(name,src,ss,d,card)=item;out=O/f'{i:02}-{name}.mp4'
 if '--reuse-shots' in sys.argv and out.exists():return out
 args=['-ss',ss,'-i',src]
 vf='scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,setpts=PTS-STARTPTS,fps=30,setsar=1,setparams=range=tv:color_primaries=bt709:color_trc=bt709:colorspace=bt709,tpad=stop_mode=clone:stop_duration=0.067'
 if card:
  args+=['-loop','1','-i',C/(card+'.png')]
  args+=['-filter_complex',f'[0:v]{vf}[bg];[1:v]format=rgba,fade=t=in:st=0.5:d=0.6:alpha=1,fade=t=out:st={d-1.2}:d=0.6:alpha=1[title];[bg][title]overlay=0:0:shortest=1[v]','-map','[v]']
 else:args+=['-vf',vf]
 args+=['-t',d,'-an','-c:v','libx264','-preset','veryfast','-crf','19','-pix_fmt','yuv420p','-threads','2',out]
 run(args);print('Encoded '+name,flush=True);return out
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:parts=list(ex.map(make,enumerate(shots)))
end=O/'09-end.mp4';run(['-framerate','30','-i',C/'end-%04d.png','-t','5','-vf','setparams=range=tv:color_primaries=bt709:color_trc=bt709:colorspace=bt709','-an','-c:v','libx264','-preset','veryfast','-crf','19','-pix_fmt','yuv420p',end]);parts.append(end)
lst=O/'concat.txt';lst.write_text(''.join("file '"+str(p)+"'\n" for p in parts))
video=O/'picture.mp4';run(['-f','concat','-safe','0','-i',lst,'-c','copy',video])
# One continuous music excerpt. Paper stem stays restrained. Real game propeller remains audible under the score.
mix=R/'public/first-cut-mix.wav'
run(['-ss','10','-i',R/'raw/music/LifeInSilico-ScottBuckley.mp3','-i',R/'public/paper-fold-sfx.wav','-ss','5','-i',raw/'20261029-030129-flight-arrival-real.mov','-filter_complex','[0:a]atrim=0:60,asetpts=PTS-STARTPTS,volume=0.75,afade=t=in:d=0.4,afade=t=out:st=57:d=3[m];[1:a]volume=0.9[p];[2:a]atrim=0:4,asetpts=PTS-STARTPTS,volume=0.16,afade=t=in:d=0.3,afade=t=out:st=3.5:d=0.5,adelay=6000|6000[e];[m][p][e]amix=inputs=3:normalize=0,alimiter=limit=0.88[a]','-map','[a]','-t','60','-c:a','pcm_s24le',mix])
out=R/'renders/Frosthavn-B+C-实录首剪-60s.mp4';run(['-i',video,'-i',mix,'-map','0:v','-map','1:a','-c:v','copy','-c:a','aac','-b:a','256k','-ar','48000','-t','60','-movflags','+faststart','-metadata','title=Frosthavn / 霜灯港 — B+C first cut','-metadata','comment=Life in Silico by Scott Buckley / CC BY 4.0 / www.scottbuckley.com.au. Edited excerpt. Original paper CG; all gameplay segments are continuous native recordings.',out])
report={'output':str(out.relative_to(R)),'status':'first cut, not final quality approval','duration':60,'gameplayStillImages':False,'shots':[],'audioSubjectivelyReviewed':False}
t=0
for name,src,ss,d,card in shots:report['shots'].append({'id':name,'timeline':[t,t+d],'source':str(src.relative_to(R)),'sourceIn':ss,'type':'original-cg' if name=='paper' else 'native-video'});t+=d
report['shots'].append({'id':'end','timeline':[55,60],'type':'original-code-animation'})
(R/'evidence/first-cut-edit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(out,flush=True)
