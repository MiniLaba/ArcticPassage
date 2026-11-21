"""MG edition: authored 3D animation and continuous native game recordings."""
from pathlib import Path
import subprocess,json,concurrent.futures,hashlib,re,sys
R=Path(__file__).resolve().parents[1];O=R/'renders/mg-edition-parts';O.mkdir(exist_ok=True);raw=R/'raw/gameplay';D=78.3
# Duration budget 80s, with 1.7s of motivated overlapping transitions = 78.3s.
shots=[
 {'id':'ticket','file':R/'renders/Frosthavn-航空折纸动效-轻纸声版-6s.mp4','in':0,'d':4,'type':'original-cg'},
 {'id':'window','file':R/'renders/mg/window.mp4','in':0,'d':16,'type':'original-cg','overlap':.3},
 {'id':'landing','file':raw/'20261029-030129-flight-arrival-real.mov','in':18,'d':6,'type':'native-video','overlap':.3,'crop':'crop=2062:1160:230:140,'},
 {'id':'polar-year','file':R/'renders/mg/panorama.mp4','in':0,'d':18,'type':'original-cg'},
 {'id':'neighbours','file':raw/'20261029-030324-guesthouse-real.mov','in':6,'d':6,'type':'native-video','overlap':.5},
 {'id':'town','file':raw/'20261029-025523-town-real.mov','in':1,'d':6,'type':'native-video'},
 {'id':'fishing','file':raw/'20261029-030741-fishing-shore-real.mov','in':2,'d':7,'type':'native-video'},
 {'id':'harbour','file':raw/'20261029-025431-harbor-real.mov','in':2,'d':5,'type':'native-video'},
 {'id':'night','file':raw/'20261029-030007-town-night-real.mov','in':1,'d':6,'type':'native-video'},
 {'id':'outro','file':R/'renders/mg/outro.mp4','in':0,'d':6,'type':'original-cg','overlap':.6},
]
def run(a,capture=False):return subprocess.run(['ffmpeg','-y','-hide_banner','-loglevel','error']+list(map(str,a)),check=True,capture_output=capture,text=capture)
def part(pair):
 i,s=pair;p=O/f'{i:02}-{s["id"]}.mp4'
 if '--resume' in sys.argv and p.exists():return p
 vf=s.get('crop','')+'scale=1920:1080:force_original_aspect_ratio=increase:flags=lanczos,crop=1920:1080,setpts=PTS-STARTPTS,fps=30,setsar=1'
 if s['type']=='native-video':vf+=',eq=contrast=1.025:saturation=0.97:brightness=0.002'
 vf+=',setparams=range=tv:color_primaries=bt709:color_trc=bt709:colorspace=bt709,tpad=stop_mode=clone:stop_duration=0.067'
 run(['-ss',s['in'],'-i',s['file'],'-t',s['d'],'-an','-vf',vf,'-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-threads','2',p]);print('Picture segment:',s['id'],flush=True);return p
with concurrent.futures.ThreadPoolExecutor(max_workers=3)as pool:parts=list(pool.map(part,enumerate(shots)))
args=[];filters=[]
for i,p in enumerate(parts):args+=['-i',p];filters.append(f'[{i}:v]settb=AVTB,setpts=PTS-STARTPTS[v{i}]')
total=shots[0]['d'];prev='v0';shots[0]['start']=0;shots[0]['end']=total
for i,s in enumerate(shots[1:],1):
 ov=s.get('overlap',0);out=f'chain{i}';start=round(total-ov,4)
 if ov:filters.append(f'[{prev}][v{i}]xfade=transition=fade:duration={ov}:offset={start}[{out}]')
 else:filters.append(f'[{prev}][v{i}]concat=n=2:v=1:a=0[{out}]')
 total=round(total+s['d']-ov,4);prev=out;s['start']=start;s['end']=total
assert abs(total-D)<1e-6
picture=O/'picture.mp4'
if not ('--resume' in sys.argv and picture.exists()):
 run(args+['-filter_complex_threads','2','-filter_complex',';'.join(filters),'-map',f'[{prev}]','-an','-r','30','-t',D,'-c:v','libx264','-preset','fast','-crf','17','-pix_fmt','yuv420p','-threads','4',picture])
print('Picture complete',flush=True)
rawmix=R/'public/mg-mix-raw.wav';master=R/'public/mg-mix-master.wav'
run(['-ss','10','-i',R/'raw/music/LifeInSilico-ScottBuckley.mp3','-i',R/'public/paper-fold-sfx.wav','-i',R/'public/mg-atmosphere-sfx.wav','-filter_complex',f'[0:a]atrim=0:{D},asetpts=PTS-STARTPTS,volume=0.75,afade=t=in:d=0.4,afade=t=out:st={D-3.2}:d=3.2[m];[1:a]atrim=0:4,afade=t=out:st=3.5:d=0.5,volume=0.9[p];[2:a]volume=1.0[s];[m][p][s]amix=inputs=3:normalize=0[a]','-map','[a]','-t',D,'-c:a','pcm_s24le',rawmix])
measure=subprocess.run(['ffmpeg','-hide_banner','-i',str(rawmix),'-af','loudnorm=I=-16:TP=-1.5:LRA=9:print_format=json','-f','null','-'],capture_output=True,text=True,check=True)
measurement=json.JSONDecoder().raw_decode(measure.stderr[measure.stderr.rfind('{'):])[0];m=measurement
norm=f'loudnorm=I=-16:TP=-1.5:LRA=9:measured_I={m["input_i"]}:measured_TP={m["input_tp"]}:measured_LRA={m["input_lra"]}:measured_thresh={m["input_thresh"]}:offset={m["target_offset"]}:linear=true:print_format=json'
run(['-i',rawmix,'-af',norm,'-ar','48000','-c:a','pcm_s24le',master])
final=R/'renders/Frosthavn-穿过机窗抵达北极-MG提升版-78s.mp4'
run(['-i',picture,'-i',master,'-map','0:v','-map','1:a','-c:v','copy','-c:a','aac','-b:a','256k','-ar','48000','-t',D,'-movflags','+faststart','-metadata','title=霜灯港 / Frosthavn — 穿过机窗，抵达北极','-metadata','comment=Music: Life in Silico by Scott Buckley / CC BY 4.0 / www.scottbuckley.com.au. Edited excerpt. Original procedural 3D theme animation; gameplay segments use continuous native recordings.',final])
report={'file':str(final.relative_to(R)),'duration':D,'width':1920,'height':1080,'fps':30,'stillsUsedAsGameplay':False,'music':'Life in Silico — Scott Buckley, CC BY 4.0','musicSourceIn':10,'subjectiveListeningVerified':False,'loudnessFirstPass':measurement,'masterSha256':hashlib.sha256(master.read_bytes()).hexdigest(),'videoSha256':hashlib.sha256(final.read_bytes()).hexdigest(),'shots':[{**s,'file':str(s['file'].relative_to(R))}for s in shots]}
(R/'evidence/mg-edition-edit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(final,flush=True)
