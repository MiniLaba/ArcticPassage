"""Assemble the actual rendered CG frames, with selected licensed music and paper SFX."""
import json,subprocess,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
plan=json.loads((ROOT/'plan.json').read_text());settings=plan['cgPreview']
frames=ROOT/'renders/cg-frames'
missing=[f for f in range(1,181) if not (frames/f'frame-{f:04d}.png').is_file()]
if missing:raise SystemExit(f'Cannot assemble: {len(missing)} actual CG frames still missing.')
music=ROOT/settings['musicAuditionFile'];paper=ROOT/'public/paper-fold-sfx.wav';mix=ROOT/'public/cg-preview-mix.wav'
subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(music),'-i',str(paper),'-filter_complex',f"[0:a]atrim=0:6,afade=t=out:st=5.2:d=0.8,volume={settings['musicGain']}[m];[1:a]volume={settings['paperGain']}[p];[m][p]amix=inputs=2:normalize=0,alimiter=limit=0.85[a]",'-map','[a]','-c:a','pcm_s24le',str(mix)],check=True)
dest=ROOT/settings.get('outputFile','renders/Frosthavn-航空折纸动效-6s.mp4')
credit='Life in Silico by Scott Buckley — CC BY 4.0 — www.scottbuckley.com.au. Excerpt, fades and mix adjustments.'
subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-framerate','30','-start_number','1','-i',str(frames/'frame-%04d.png'),'-i',str(mix),'-t','6','-map','0:v:0','-map','1:a:0','-c:v','libx264','-crf','17','-pix_fmt','yuv420p','-c:a','aac','-b:a','256k','-ar','48000','-movflags','+faststart','-metadata','title=Frosthavn — original folding-paper airline CG preview','-metadata',f'comment={credit}','-metadata','description=Original CG preview only. No gameplay footage is included.',str(dest)],check=True)
(ROOT/'evidence/cg-preview.json').write_text(json.dumps({'file':str(dest.relative_to(ROOT)),'durationSeconds':6,'frames':180,'width':1280,'height':720,'fps':30,'gameplayFootage':False,'music':credit,'paperGain':settings['paperGain'],'paperGainChangeDb':settings.get('paperGainIncreaseDb',0),'subjectiveListeningVerified':False,'sha256':hashlib.sha256(dest.read_bytes()).hexdigest()},ensure_ascii=False,indent=2))
print(dest)
