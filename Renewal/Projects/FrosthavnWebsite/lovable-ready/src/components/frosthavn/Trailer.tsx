import { useEffect, useRef, useState } from 'react';
import type Hls from 'hls.js';
import { FILM } from './film';
import './Trailer.css';

export function FilmPlay() {
 return <svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="m9 5 11 7-11 7V5Z" stroke="currentColor" strokeWidth="1.3" strokeLinejoin="round"/></svg>;
}
export function TrailerSection({ en, onPlaybackChange }: { en: boolean; onPlaybackChange: (playing: boolean) => void }) {
 const [watching,setWatching]=useState(false);
 function close(){setWatching(false);onPlaybackChange(false);}
 return <section className="sx-film" id="film" aria-labelledby="sx-film-heading">
  <div className="sx-film-heading"><span className="xp-kicker">THE FILM / 03:20</span><h2 id="sx-film-heading">{en?'Your window\ninto Frosthavn.':'把北方的故事，\n放映给你。'}</h2><p>{en?'A flight, four seasons, and a little life by the bay.\nWatch the Frosthavn film at your own pace.':'一趟航班，四季流转，一段港湾生活。\n停一会儿，看一场属于霜灯港的电影。'}</p><span className="sx-film-language">{en?'ENGLISH AUDIO · CHINESE SUBTITLES':'英文配音 · 中文字幕'}</span></div>
  <div className="sx-film-media">{watching?<><TrailerPlayer en={en} onPlaybackChange={onPlaybackChange}/><button type="button" className="sx-film-collapse" onClick={close}>{en?'Back to the cover':'收起影片'} ↑</button></>:<button type="button" className="sx-film-poster" data-film-trigger onClick={()=>{onPlaybackChange(true);setWatching(true);}} aria-label={en?'Play the Frosthavn film on this page':'在页面内播放霜灯港宣传片'}>
   <img src={FILM.poster} width="1920" height="1080" loading="lazy" decoding="async" alt={en?'Stardew Valley Arctic exploration mod, Frosthavn':'霜灯港：闺蜜给我做的星露谷北极探索 MOD'}/>
   <span className="sx-film-play"><FilmPlay/></span>
  </button>}<div className="sx-film-caption"><span>MOONBIRD AIR / FROSTHAVN</span><span>{en?'THE OFFICIAL FILM':'霜灯港 · 官方宣传片'}</span></div></div>
 </section>;
}
export default function TrailerPlayer({ en, onPlaybackChange }: { en: boolean; onPlaybackChange: (playing: boolean) => void }) {
 const ref=useRef<HTMLVideoElement>(null),switchToSmooth=useRef<()=>void>(()=>{});
 const playback=useRef(onPlaybackChange);playback.current=onPlaybackChange;
 const [smooth,setSmooth]=useState(false),[error,setError]=useState(false),[blocked,setBlocked]=useState(false);
 useEffect(()=>{
  const video=ref.current;if(!video)return;
  let disposed=false,engine:Hls|null=null,fallback=false;
  const play=()=>{if(disposed)return;void video.play().then(()=>{if(!disposed)setBlocked(false);}).catch(()=>{if(!disposed){setBlocked(true);playback.current(false);}});};
  const useFallback=()=>{
   if(disposed)return;
   if(fallback){setError(true);return;}
   fallback=true;setSmooth(true);setError(false);engine?.destroy();engine=null;
   const at=video.currentTime||0;
   video.src=FILM.fallback;
   video.addEventListener('loadedmetadata',()=>{if(!disposed){video.currentTime=Math.min(at,video.duration||at);play();}},{once:true});video.load();
  };
  switchToSmooth.current=useFallback;
  video.addEventListener('error',useFallback);
  const observer=new IntersectionObserver(entries=>{if(!entries[0]?.isIntersecting&&!video.paused)video.pause();},{threshold:0});observer.observe(video);
  const saveData=(navigator as Navigator & {connection?:{saveData?:boolean}}).connection?.saveData;
  if(saveData)useFallback();
  else if(video.canPlayType('application/vnd.apple.mpegurl')){video.src=FILM.stream;play();}
  else void import('hls.js').then(({default:Hls})=>{
   if(disposed)return;
   if(!Hls.isSupported()){useFallback();return;}
   engine=new Hls({maxBufferLength:12,maxMaxBufferLength:24,backBufferLength:10,enableWorker:true});
   engine.on(Hls.Events.MANIFEST_PARSED,play);
   engine.on(Hls.Events.ERROR,(_,data)=>{if(data.fatal&&!disposed)useFallback();});
   engine.loadSource(FILM.stream);engine.attachMedia(video);
  }).catch(useFallback);
  return()=>{disposed=true;observer.disconnect();switchToSmooth.current=()=>{};video.removeEventListener('error',useFallback);engine?.destroy();video.pause();video.removeAttribute('src');video.load();playback.current(false);};
 },[]);
 return <div className="sx-film-player">
  <div className="sx-film-screen"><video ref={ref} controls playsInline autoPlay preload="metadata" poster={FILM.poster} aria-label={en?'Frosthavn trailer, English audio with Chinese narrative subtitles':'霜灯港宣传片，英文配音与中文叙事字幕'} onPlay={()=>{setBlocked(false);playback.current(true);}} onPause={()=>playback.current(false)} onEnded={()=>playback.current(false)}/>{blocked&&!error&&<button type="button" className="sx-film-resume" onClick={()=>{void ref.current?.play().then(()=>setBlocked(false)).catch(()=>setBlocked(true));}}><FilmPlay/>{en?'Play the film':'播放宣传片'}</button>}</div>
  <div className="sx-film-player-bar"><span>{en?'A JOURNEY THROUGH THE ARCTIC YEAR':'飞越四季 · 港湾生活'} <i>03:20</i></span><button type="button" disabled={smooth} onClick={()=>switchToSmooth.current()}>{smooth?(en?'Smooth playback':'流畅播放中'):(en?'Smooth playback':'流畅播放')}</button></div>
  {error&&<p className="sx-film-error" role="alert">{en?'The film could not be loaded. ':'视频暂时无法载入。'}<a href={FILM.fallback} target="_blank" rel="noreferrer">{en?'Open video directly ↗':'直接打开视频 ↗'}</a></p>}
 </div>;
}
