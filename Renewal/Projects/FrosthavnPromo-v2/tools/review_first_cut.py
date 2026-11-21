import subprocess,json
from pathlib import Path
r=Path(__file__).resolve().parents[1];v=r/'renders/Frosthavn-B+C-实录首剪-60s.mp4'
for start in (0,20,40):
 subprocess.run(['ffmpeg','-y','-v','error','-ss',str(start),'-i',str(v),'-t','20','-vf','fps=2,scale=320:180,tile=8x5','-frames:v','1',str(r/f'evidence/first-cut-review-{start:02d}-{start+20:02d}.jpg')],check=True)
for cut in (6,10,15,22,30,36,42,48,55):
 subprocess.run(['ffmpeg','-y','-v','error','-ss',str(cut-.5),'-i',str(v),'-t','1','-vf','fps=10,scale=320:180,tile=5x2','-frames:v','1',str(r/f'evidence/transition-{cut:02d}.jpg')],check=True)
report=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(v)]))
a=subprocess.run(['ffmpeg','-hide_banner','-i',str(v),'-vn','-af','volumedetect','-f','null','-'],capture_output=True,text=True)
report['audioLevels']=[x.strip() for x in a.stderr.splitlines() if 'mean_volume' in x or 'max_volume' in x]
report['validationLimits']='Automated duration/codec/audio-level checks; visual review uses contact sheets and full-size frames. No subjective listening claim. First cut, not final approval.'
(r/'evidence/first-cut-probe.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(report['format']['duration'],report['audioLevels'])
