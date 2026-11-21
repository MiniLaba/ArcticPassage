import { useEffect, useRef, useState, type ReactNode } from 'react';

const clamp=(v:number)=>Math.max(0,Math.min(1,v));
const ease=(v:number)=>{const t=clamp(v);return t*t*(3-2*t);};
function sample(p:number,points:readonly (readonly [number,number])[]){
 for(let i=1;i<points.length;i++){const a=points[i-1]!,b=points[i]!;if(p<=b[0])return a[1]+(b[1]-a[1])*ease((p-a[0])/(b[0]-a[0]));}
 return points[points.length-1]![1];
}

/** The cabin opens only after approach, touchdown, deceleration and a parked hold. */
export default function ScrollJourney({en,children}:{en:boolean;children:(caption:ReactNode)=>ReactNode}){
 const root=useRef<HTMLDivElement>(null),[stage,setStage]=useState(0);
 useEffect(()=>{
  const el=root.current;if(!el)return;
  const motion=window.matchMedia('(prefers-reduced-motion: reduce)');
  let frame=0,flightFrame=0,last=-1,lastP=-1,lastWidth=0;
  const began=performance.now();
  function draw(){
   frame=0;if(!el)return;
   const mobile=innerWidth<=760,header=mobile?67:82;
   const scroll=motion.matches?0:clamp((header-el.getBoundingClientRect().top)/Math.max(1,el.offsetHeight-(innerHeight-header)));
   const intro=motion.matches?0:.07*ease((performance.now()-began)/6000);
   const p=motion.matches?0:intro+(1-intro)*scroll;
   if(p!==lastP||innerWidth!==lastWidth){
    lastP=p;lastWidth=innerWidth;
    // 0–.58 flight; .58–.74 landing/roll; .74–.83 parked; .83–1 reveal.
    const r=ease((p-.83)/.17),ground=ease((p-.45)/.13),roll=clamp((p-.585)/.155);
    const distance=1600*(1-Math.pow(1-roll,3));
    const bump=motion.matches?0:Math.sin((p-.585)*1300)*2.2*clamp(1-Math.abs((p-.605)/.025));
    const x=sample(p,[[0,1790],[.04,1720],[.24,1200],[.44,620],[.58,225]]);
    const y=sample(p,[[0,440],[.24,445],[.44,440],[.58,428]]);
    const zoom=sample(p,[[0,1.2],[.24,1.3],[.44,1.7],[.58,2.3]]);
    const vars:Record<string,string>={
     '--journey-progress':String(p),'--cabin-opacity':String(1-ease((p-.84)/.12)),'--arrival-pan':(55-12*r)+'%','--copy-opacity':String(1-ease(scroll/.16)),
     '--copy-y':-35*ease(scroll/.16)+'px','--caption-opacity':String(ease((p-.22)/.06)),
     '--aerial-x':-x+'px','--aerial-y':-y+'px','--aerial-zoom':String(zoom),
     '--aerial-opacity':String(1-ground),'--ground-opacity':String(ground),
     '--ground-travel':-distance+'px','--ground-drift':-distance/20+'px','--touchdown-y':bump+'px',
     '--flight-opacity':String(1-ease((p-.85)/.1)),'--world-opacity':String(ease((p-.85)/.1)),
     '--wing-opacity':String(ease(p/.025)*(1-ease((p-.84)/.08))),'--air-haze':String(.18+.12*Math.sin(p*Math.PI)),
    };
    for(const [key,value]of Object.entries(vars))el.style.setProperty(key,value);
    const next=p<.1?0:p<.34?1:p<.58?2:p<.74?3:p<.84?4:5;
    if(next!==last){last=next;setStage(next);}
    el.dataset['travel']=scroll>.16?'moving':'opening';
    window.dispatchEvent(new CustomEvent('frosthavn:passage',{detail:p}));
   }
   if(!motion.matches&&performance.now()-began<6000)frame=requestAnimationFrame(draw);
  }
  const queue=()=>{if(!frame)frame=requestAnimationFrame(draw);};
  // A deliberate boarding click plays the whole approach. Ordinary wheel,
  // touch or keyboard input immediately hands the native scroll back to you.
  const stop=()=>{cancelAnimationFrame(flightFrame);flightFrame=0;el.dataset['autopilot']='off';};
  const fly=()=>{
   stop();if(motion.matches)return;
   const header=innerWidth<=760?67:82;
   const end=scrollY+el.getBoundingClientRect().top-header+(el.offsetHeight-(innerHeight-header))*.985;
   const from=scrollY,started=performance.now(),duration=Math.max(4500,14000*Math.min(1,Math.abs(end-from)/Math.max(1,el.offsetHeight-innerHeight)));
   el.dataset['autopilot']='on';
   const move=(now:number)=>{const t=clamp((now-started)/duration);window.scrollTo({top:from+(end-from)*ease(t),behavior:'instant'});queue();if(t<1)flightFrame=requestAnimationFrame(move);else stop();};
   flightFrame=requestAnimationFrame(move);
  };
  const keys=(event:KeyboardEvent)=>{if(['ArrowDown','ArrowUp','PageDown','PageUp','Home','End','Escape',' '].includes(event.key))stop();};
  const motionChanged=()=>{stop();queue();};
  draw();window.addEventListener('scroll',queue,{passive:true});window.addEventListener('resize',queue);motion.addEventListener('change',motionChanged);
  window.addEventListener('pointerdown',stop,{passive:true});window.addEventListener('frosthavn:fly',fly);window.addEventListener('wheel',stop,{passive:true});window.addEventListener('touchstart',stop,{passive:true});window.addEventListener('keydown',keys);
  return()=>{stop();cancelAnimationFrame(frame);window.removeEventListener('scroll',queue);window.removeEventListener('resize',queue);motion.removeEventListener('change',motionChanged);window.removeEventListener('pointerdown',stop);window.removeEventListener('frosthavn:fly',fly);window.removeEventListener('wheel',stop);window.removeEventListener('touchstart',stop);window.removeEventListener('keydown',keys);};
 },[]);
 const shots=en?[
  ['01 / ABOVE THE FJORD','A little further north.','Scroll to follow the journey.'],
  ['02 / THE COAST APPEARS','A bay beyond the glass.','Icebergs give way to rock, then a few warm windows.'],
  ['03 / FINAL APPROACH','The snow runway draws closer.','Stay by the window. We are almost there.'],
  ['04 / TOUCHDOWN','Touch down. Let the world slow.','Snow markers slip past, then gently come to rest.'],
  ['05 / PARKED IN FROSTHAVN','Welcome to Frosthavn.','We have arrived. A light is waiting on the shore.'],
  ['06 / A WORLD OPENS','Now, let the north unfold.','From a small window to a whole northern life.'],
 ]:[
  ['01 / ABOVE THE FJORD','再往北，一点。','滚动，跟随这次旅程。'],
  ['02 / THE COAST APPEARS','海湾，就在机窗之外。','冰山之后是岩岸，岩岸之后，是几扇暖窗。'],
  ['03 / FINAL APPROACH','雪跑道，正在靠近。','再看一眼窗外，我们就要抵达。'],
  ['04 / TOUCHDOWN','接地，让世界慢慢停稳。','雪地标记掠过窗边，滑行渐缓。'],
  ['05 / PARKED IN FROSTHAVN','欢迎来到霜灯港。','飞机已经停稳，岸上有一盏灯在等你。'],
  ['06 / A WORLD OPENS','现在，把北方展开。','从一扇小小的机窗，走进一整个北方。'],
 ];
 return <div className="xp-journey" id="top" ref={root}>
  {children(<div className="xp-journey-script" aria-hidden="true" data-stage={stage}><span>{shots[stage]![0]}</span><h2>{shots[stage]![1]}</h2><p>{shots[stage]![2]}</p><div className="sx-flight-stops"><span className={stage<2?'is-current':''}>{en?'COAST':'越过海湾'}</span><i/><span className={stage===2?'is-current':''}>{en?'APPROACH':'对准跑道'}</span><i/><span className={stage===3?'is-current':''}>{en?'TOUCHDOWN':'接地滑行'}</span><i/><span className={stage>=4?'is-current':''}>{en?'ARRIVED':'停稳抵达'}</span></div></div>)}
  <div className="xp-journey-accessible xp-sr-only" aria-live="polite">{stage>0?shots[stage]![1]:''}</div>
 </div>;
}
