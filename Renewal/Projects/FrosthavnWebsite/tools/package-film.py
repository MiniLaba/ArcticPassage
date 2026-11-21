# coding: utf-8
"""Package the approved film for static hosting without recompressing its HD stream."""
from pathlib import Path
import subprocess,json,hashlib,math
R=Path(__file__).resolve().parents[1];promo=R.parent/'FrosthavnPromo-v2';info=json.loads((promo/'evidence/director-v9-edit.json').read_text());src=promo/info['file'];sha=hashlib.sha256(src.read_bytes()).hexdigest();assert sha==info['videoSha256'];key='v9-'+sha[:10];out=R/'public/assets/film'/key;out.mkdir(parents=True,exist_ok=True)
def ff(args):subprocess.run(['ffmpeg','-y','-hide_banner','-loglevel','error']+list(map(str,args)),check=True)
ff(['-i',src,'-map','0:v:0','-map','0:a:0','-c','copy','-f','hls','-hls_time','6','-hls_playlist_type','vod','-hls_segment_type','fmp4','-hls_fmp4_init_filename','init.mp4','-hls_flags','independent_segments','-hls_segment_filename',out/'part-%03d.m4s',out/'hd.m3u8'])
(out/'master.m3u8').write_text('#EXTM3U\n#EXT-X-VERSION:7\n#EXT-X-STREAM-INF:BANDWIDTH=6500000,RESOLUTION=1920x1080,FRAME-RATE=30.000,CODECS="avc1.640028,mp4a.40.2"\nhd.m3u8\n')
cover=R.parent/'FrosthavnPromo-v2/covers/stardew-v5/霜灯港-闺蜜给我做的星露谷MOD-精修版.png'
ff(['-i',cover,'-frames:v','1','-vf','scale=1920:1080','-q:v','2',out/'poster-stardew-v5.jpg'])
ff(['-i',src,'-vf','scale=1280:720','-c:v','libx264','-preset','medium','-crf','23','-maxrate','900k','-bufsize','1800k','-pix_fmt','yuv420p','-threads','4','-c:a','aac','-b:a','128k','-movflags','+faststart',out/'smooth.mp4'])
files=[{'file':p.name,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}for p in sorted(out.iterdir())if p.is_file()];assert max(f['bytes']for f in files)<25*1024*1024
meta={'edition':'V9 / Aviation welcome and captain cabin PA','sourceFile':str(src),'sourceSha256':sha,'duration':199.7,'hdVideo':'1920x1080 H.264, stream copied; original audio copied','smoothVideo':'1280x720 H.264/AAC compatibility and data-saving fallback','base':'/assets/film/'+key,'files':files,'references':['https://developers.cloudflare.com/workers/static-assets/billing-and-limitations/','https://github.com/video-dev/hls.js']};(R/'docs/FilmMedia-2026-10-29.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2))
(R/'src/film.ts').write_text('export const FILM = '+json.dumps({'stream':meta['base']+'/master.m3u8','fallback':meta['base']+'/smooth.mp4','poster':meta['base']+'/poster-stardew-v5.jpg','duration':'3:20','edition':'v9'},indent=2)+' as const;\n')
print(key,'files',len(files),'largest',max(f['bytes']for f in files),'total',sum(f['bytes']for f in files),flush=True)
