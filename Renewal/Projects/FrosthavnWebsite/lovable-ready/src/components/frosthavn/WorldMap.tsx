import {useEffect,useRef,useState} from 'react';
import {WORLD_POSTER} from './worldAsset';
import './WorldMap.css';

type Season='winter'|'spring'|'summer'|'autumn';
type View='bay'|'airport'|'town'|'harbour'|'camp'|'glacier';
export type World={setSeason:(s:Season)=>void;setNight:(n:boolean)=>void;focus:(v:View)=>void;setYearPlaying:(v:boolean)=>void;zoom:(n:number)=>void;rotate:(n:number)=>void;reset:()=>void;setVisible:(v:boolean)=>void;dispose:()=>void};
export type WorldOptions={label:string;reducedMotion:boolean;onError:()=>void;onSeason:(s:Season)=>void;onNight?:(night:boolean)=>void};
const seasons:readonly [Season,string,string][]=[['winter','冬','Winter'],['spring','春','Spring'],['summer','夏','Summer'],['autumn','秋','Autumn']];
const views:readonly [View,string,string][]=[['bay','海湾总览','The whole bay'],['airport','雪跑道','Airstrip'],['town','彩屋小镇','Town'],['harbour','工作渔港','Harbour'],['camp','高地营地','Camp'],['glacier','冰川','Glacier']];

export default function WorldMap({en,onPlan}:{en:boolean;onPlan:()=>void}){
 const shell=useRef<HTMLDivElement>(null),host=useRef<HTMLDivElement>(null),world=useRef<World|null>(null),isVisible=useRef(true);
 const [attempt,setAttempt]=useState(0),[status,setStatus]=useState<'idle'|'loading'|'ready'|'error'>('idle');
 const [season,setSeason]=useState<Season>('winter'),[night,setNight]=useState(false),[view,setView]=useState<View>('bay'),[yearPlaying,setYearPlaying]=useState(false),[full,setFull]=useState(false),[reduced,setReduced]=useState(false),[fullSupported,setFullSupported]=useState(false);
 const initial=useRef({season,night});initial.current={season,night};
 useEffect(()=>{setFullSupported(!!document.fullscreenEnabled);setReduced(matchMedia('(prefers-reduced-motion: reduce)').matches);const observer=new IntersectionObserver(entries=>{isVisible.current=!!entries[0]?.isIntersecting;world.current?.setVisible(isVisible.current);});if(shell.current)observer.observe(shell.current);const change=()=>setFull(document.fullscreenElement===shell.current);document.addEventListener('fullscreenchange',change);return()=>{observer.disconnect();document.removeEventListener('fullscreenchange',change);};},[]);
 useEffect(()=>{
  if(!attempt||!host.current)return;
  const target=host.current;let live=true,active:World|null=null;
  setStatus('loading');
  void import('./worldBundle.mjs').then(async module=>{
   if(!live)return;
   active=await module.createWorld(target,{label:en?'Explore Frosthavn in three dimensions':'可旋转浏览的霜灯港立体海湾',reducedMotion:matchMedia('(prefers-reduced-motion: reduce)').matches,onError:()=>{if(live){setStatus('error');setYearPlaying(false);}},onSeason:s=>{if(live)setSeason(s);},onNight:value=>{if(live)setNight(value);}});
   if(!live){active.dispose();return;}
   world.current=active;active.setSeason(initial.current.season);active.setNight(initial.current.night);active.setVisible(isVisible.current);setStatus('ready');
  }).catch(()=>{if(live){setStatus('error');setYearPlaying(false);}});
  return()=>{live=false;world.current=null;active?.dispose();target.replaceChildren();};
 },[attempt]);
 useEffect(()=>{host.current?.querySelector('canvas')?.setAttribute('aria-label',en?'Explore Frosthavn in three dimensions':'可旋转浏览的霜灯港立体海湾');},[en,status]);
 function chooseSeason(next:Season){setSeason(next);setYearPlaying(false);world.current?.setSeason(next);world.current?.setNight(night);}
 function chooseNight(value:boolean){setNight(value);setYearPlaying(false);world.current?.setNight(value);}
 function chooseView(next:View){setView(next);world.current?.focus(next);}
 function cycle(){const next=!yearPlaying;setYearPlaying(next);world.current?.setYearPlaying(next);}
 function close(){setAttempt(0);setStatus('idle');setView('bay');setYearPlaying(false);}
 async function fullscreen(){try{if(document.fullscreenElement===shell.current)await document.exitFullscreen();else await shell.current?.requestFullscreen();}catch{/* The inline scene remains usable when fullscreen is unavailable. */}}
 const ready=status==='ready';
 return <div className="sx-world" id="bay-3d" ref={shell} data-scene-status={status} data-world-season={season} data-world-view={view}>
  <div className="sx-world-top"><div className="sx-world-seasons" role="group" aria-label={en?'Choose the model season':'选择立体海湾的季节'}>{seasons.map(([id,zh,label])=><button key={id} type="button" disabled={!ready} aria-pressed={season===id} onClick={()=>chooseSeason(id)}>{en?label:zh}</button>)}</div><div className="sx-world-day" role="group" aria-label={en?'Choose daylight or night':'选择白昼或夜色'}><button type="button" disabled={!ready} aria-pressed={!night&&!yearPlaying} onClick={()=>chooseNight(false)}>{en?'Daylight':'白昼'}</button><button type="button" disabled={!ready} aria-pressed={night&&!yearPlaying} onClick={()=>chooseNight(true)}>{season==='summer'?(en?'Midnight sun':'午夜太阳'):(en?'Night & aurora':'夜色 · 极光')}</button></div></div>
  <div className="sx-world-stage">
   <div className="sx-world-canvas" ref={host}/>
   {!ready&&<div className="sx-world-cover"><img src={WORLD_POSTER} alt={en?'The three-dimensional Frosthavn bay from the film':'宣传片中的霜灯港立体海湾'} width="1600" height="900" loading="lazy"/><div className="sx-world-wash"/><div className="sx-world-invitation"><span>FROSTHAVN / A LIVING DIORAMA</span><h3>{en?'A whole bay,\nwithin reach.':'转个角度，\n走近霜灯港。'}</h3>{status==='error'?<><p role="status">{en?'The 3D scene is unavailable on this device.':'此设备暂时无法打开立体海湾。'}</p><button type="button" onClick={onPlan}>{en?'Open the illustrated map ↗':'查看平面导览 ↗'}</button><button type="button" className="sx-world-retry" onClick={()=>setAttempt(a=>a+1)}>{en?'Try again':'重新尝试'}</button></>:<button type="button" disabled={status==='loading'} onClick={()=>setAttempt(a=>a+1)}>{status==='loading'?(en?'Opening the bay…':'正在展开海湾…'):(en?'Explore the 3D bay ↗':'走进立体海湾 ↗')}</button>}</div></div>}
   {ready&&<><div className="sx-world-stamp">FROSTHAVN <span>{en?'THE BAY IN 3D':'立体海湾'}</span></div><div className="sx-world-tools"><button type="button" onClick={()=>world.current?.rotate(1)} aria-label={en?'Rotate left':'向左旋转'}>↶</button><button type="button" onClick={()=>world.current?.rotate(-1)} aria-label={en?'Rotate right':'向右旋转'}>↷</button><i/><button type="button" onClick={()=>world.current?.zoom(1)} aria-label={en?'Zoom in':'拉近'}>＋</button><button type="button" onClick={()=>world.current?.zoom(-1)} aria-label={en?'Zoom out':'拉远'}>−</button><i/><button type="button" onClick={()=>{setView('bay');world.current?.reset();}} aria-label={en?'Return to the overview':'回到海湾总览'}>⌂</button>{fullSupported&&<button type="button" onClick={()=>void fullscreen()} aria-label={full?(en?'Exit fullscreen':'退出全屏'):(en?'View fullscreen':'全屏浏览')}>{full?'↙':'⛶'}</button>}</div></>}
  </div>
  <div className="sx-world-bottom"><div className="sx-world-views" role="group" aria-label={en?'Choose a viewpoint':'选择观景位置'}>{views.map(([id,zh,label])=><button type="button" key={id} disabled={!ready} aria-pressed={view===id} onClick={()=>chooseView(id)}>{en?label:zh}</button>)}</div><div className="sx-world-year">{!reduced&&<button type="button" disabled={!ready} aria-pressed={yearPlaying} onClick={cycle}>{yearPlaying?(en?'Pause the year Ⅱ':'暂停四季 Ⅱ'):(en?'Watch a year ▷':'走过一年 ▷')}</button>}{ready&&<button type="button" onClick={close}>{en?'Leave 3D':'退出漫游'}</button>}</div></div>
  <div className="sx-world-note"><span className="sx-world-desktop">{en?'Drag to orbit · Ctrl / ⌘ + scroll to zoom':'拖动旋转 · Ctrl / ⌘ + 滚轮缩放'}</span><span className="sx-world-mobile">{en?'Two fingers to orbit & zoom · One finger to scroll the page':'双指旋转缩放 · 单指上下浏览页面'}</span><span>{en?'Scenery from the film. Game paths are in the illustrated guide.':'宣传片同款立体镇景 · 游戏通路见平面导览'}</span></div>
 </div>;
}
