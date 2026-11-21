"""Record the actual game via the user-requested macOS screencapture command."""
import argparse,datetime,json,subprocess
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('scene');p.add_argument('--seconds',type=int,default=30);args=p.parse_args()
if not 1<=args.seconds<=120:raise SystemExit('Use a duration from 1 to 120 seconds.')
windows=json.loads(subprocess.check_output(['/private/tmp/frosthavn-window-info']))
game=next((w for w in windows if 'Stardew Valley' in w['title'] and w['onScreen'] and w['bounds']['Width']>=800),None)
if game is None:raise SystemExit('No visible game window. No recording started.')
b=game['bounds'];rect=f"{round(b['X'])},{round(b['Y'])+28},{round(b['Width'])},{round(b['Height'])-28}"
stamp=datetime.datetime.now(ZoneInfo('Asia/Shanghai')).strftime('%Y%m%d-%H%M%S')
slug=''.join(c for c in args.scene if c.isalnum() or c in '-_')
out=ROOT/f'raw/gameplay/{stamp}-{slug}.mov'
command=['/usr/sbin/screencapture','-v','-V',str(args.seconds),'-A','-R',rect,str(out)]
print(f'Recording {args.scene} for {args.seconds}s: {out}',flush=True)
result=subprocess.run(command)
report={'scene':args.scene,'file':str(out.relative_to(ROOT)),'window':game,'rect':rect,'command':command,'exitCode':result.returncode,'systemAudioRequested':True,'visualVerified':False,'audioVerified':False,'staging':'Independent scene-start save; not ordinary progression validation.'}
if result.returncode==0 and out.exists():
 report['probe']=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','stream=codec_type,codec_name,width,height,avg_frame_rate,duration,nb_frames','-show_entries','format=duration,size','-of','json',str(out)]))
(ROOT/f'evidence/{stamp}-{slug}-recording.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
raise SystemExit(result.returncode)
