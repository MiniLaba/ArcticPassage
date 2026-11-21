import {useEffect,useRef,useState} from 'react';
import type {Lang} from './content';

const seasons=[
 {id:'winter',name:['冬 · 暖窗','WINTER / LAMPLIGHT'],title:['长夜里，\n也有一盏灯。','A light through the long night.'],body:['雪落在屋顶，炉火留在窗里。先把行李放下，港口的日子可以慢慢开始。','Snow on the roofs, a fire behind the glass. Set your bags down. There is time to begin.'],time:'22:00'},
 {id:'spring',name:['春 · 融水','SPRING / MELTWATER'],title:['冰雪退去，\n海岸醒来。','The coast begins to wake.'],body:['融水穿过裸岩，细小的绿意贴着地面生长。沿着熟悉的小路，再认识一次海湾。','Meltwater finds the bare rock. Low plants return. Walk the familiar paths and notice what has changed.'],time:'10:30'},
 {id:'summer',name:['夏 · 长日','SUMMER / LONG LIGHT'],title:['把一天，\n过得长一点。','Let the day linger.'],body:['苔原舒展，海风越过码头。给钓鱼、散步和一场没有催促的相遇，多留一点时间。','The tundra opens, and a sea breeze crosses the pier. Leave more time for a cast, a walk, an unhurried meeting.'],time:'18:00'},
 {id:'fall',name:['秋 · 归港','AUTUMN / HOMECOMING'],title:['秋色贴着岩岸，\n慢慢变深。','Autumn gathers on the shore.'],body:['低矮的植被染上赭红，晚归的船靠近灯火。把今日的收获带回去，明天又是新的一天。','Low plants turn russet. A late boat follows the lights. Bring the day’s catch home. Tomorrow can wait.'],time:'16:30'},
] as const;
const clamp=(v:number)=>Math.max(0,Math.min(1,v));
export default function SeasonVoyage({lang}:{lang:Lang}){
 const ref=useRef<HTMLElement>(null),[active,setActive]=useState(0);const en=lang==='en',n=en?1:0;
 useEffect(()=>{
  const el=ref.current;if(!el)return;const reduced=matchMedia('(prefers-reduced-motion: reduce)');let frame=0,last=-1;
  const paint=()=>{frame=0;const header=innerWidth<=760?67:82;const p=clamp((header-el.getBoundingClientRect().top)/Math.max(1,el.offsetHeight-(innerHeight-header)));const v=p*3;const i=Math.min(3,Math.floor(v));const next=Math.min(3,Math.round(v));
   if(!reduced.matches){for(let j=0;j<4;j++){const opacity=j===i?1:j===i+1?v-i:0;el.style.setProperty('--season-'+j,String(opacity));}el.style.setProperty('--season-pan',(46+p*12)+'%');el.style.setProperty('--season-scale',String(1.025+p*.035));el.style.setProperty('--winter-glow',String(1-Math.min(1,p*4)));if(next!==last){last=next;setActive(next);}}
  };
  const queue=()=>{if(!frame)frame=requestAnimationFrame(paint);};paint();addEventListener('scroll',queue,{passive:true});addEventListener('resize',queue);return()=>{cancelAnimationFrame(frame);removeEventListener('scroll',queue);removeEventListener('resize',queue);};
 },[]);
 function choose(i:number){const el=ref.current;if(!el)return;if(matchMedia('(prefers-reduced-motion: reduce)').matches){for(let j=0;j<4;j++)el.style.setProperty('--season-'+j,j===i?'1':'0');setActive(i);return;}const header=innerWidth<=760?67:82;window.scrollTo({top:scrollY+el.getBoundingClientRect().top-header+(el.offsetHeight-(innerHeight-header))*(i/3),behavior:'smooth'});}
 const s=seasons[active]!;
 return <section className="sx-voyage" id="seasons" ref={ref} aria-label={en?'Four seasons in Frosthavn':'霜灯港的四季'}><div className="sx-season-stage">
  <div className="sx-season-images" aria-hidden="true">{seasons.map((s,i)=><img key={s.id} className={'sx-season-image sx-season-'+i} src={'/assets/experience/town-'+s.id+'.webp'} width="1448" height="1086" alt="" loading={i===0?'eager':'lazy'}/>)}</div><div className="sx-season-shade"/>
  <div className="sx-season-copy" aria-live="polite"><span className="xp-kicker">ONE BAY / FOUR SEASONS</span><span className="sx-season-name">{s.name[n]} <i>{s.time}</i></span><h2 key={s.id+'title'}>{s.title[n]}</h2><p key={s.id+'body'}>{s.body[n]}</p></div>
  <div className="sx-season-bottom"><span>{en?'SCROLL THROUGH THE YEAR':'滚动，走过海湾的一年'} ↓</span><div role="group" aria-label={en?'Choose a season':'选择季节'}>{seasons.map((s,i)=><button type="button" key={s.id} aria-pressed={i===active} onClick={()=>choose(i)}><small>0{i+1}</small>{s.name[n].split(en?' / ':' · ')[0]}</button>)}</div><a href="#explore">{en?'Find your way ↗':'去镇里走走 ↗'}</a></div>
 </div></section>;
}
