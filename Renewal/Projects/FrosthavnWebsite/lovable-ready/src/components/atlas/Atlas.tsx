import {useEffect,useRef,useState} from 'react';
import {places,type Place} from './places';
import './atlas.css';

import type {AtlasViewer, Season} from './viewer.mjs';
const seasons: Array<[Season,string]>=[['spring','春'],['summer','夏'],['autumn','秋'],['winter','冬']];
const walkSites=['market','port','air','station','church','lookout'];
const asset=(name:string)=>'/atlas/'+name;
type MapBox=[number,number,number];
const home:MapBox=[1500,1500,3000];
const stories: Array<[string,string,string,string]> = [
 ['air','terminal.webp','雪原航站楼','拱壳落地，两道门之间的通廊抵挡横风。'],
 ['market','town.webp','灯市双摊','港街的步行尺度，从摊位之间看得最清楚。'],
 ['vault','vault.webp','岩肩种子库','从苔原上看，整座库房只露出一扇门。'],
 ['camp','camp.webp','镇西冬营','四座雪屋围着一片空地，远处是科考营房。'],
 ['ice','ice.webp','北界冰舌','冰舌的轮廓在终碛内侧收束，接上融水谷。'],
 ['sea','offshore.webp','远海漂冰','桌状冰山与带裂脊的崩解冰块散在外海。']
];
function Compass({small=false}:{small?:boolean}){
 return <svg aria-hidden="true" viewBox="0 0 52 52" className={small?'compass small':'compass'}><circle cx="26" cy="26" r="20" fill="none" stroke="currentColor" strokeWidth="1"/><path d="M26 1 30 22 51 26 30 30 26 51 22 30 1 26 22 22Z" fill="none" stroke="currentColor"/><path d="m26 3 0 23-4-4ZM49 26H26l4-4ZM26 49V26l4 4ZM3 26h23l-4 4Z" fill="currentColor"/></svg>
}
export default function Atlas(){
 const [mode,setMode]=useState<'map'|'model'>('map'),[selected,setSelected]=useState<Place|null>(null),[season,setSeason]=useState<Season>('summer'),[walking,setWalking]=useState(false),[status,setStatus]=useState('idle'),[filter,setFilter]=useState('全部'),[attempt,retry]=useState(0);
 const [box,setBox]=useState<MapBox>([...home]);const canvas=useRef<HTMLCanvasElement>(null),viewer=useRef<AtlasViewer|null>(null);
 const svg=useRef<SVGSVGElement>(null);const drag=useRef<{x:number;y:number;b:MapBox}|null>(null);
 const current=useRef({selected,season});current.current={selected,season};
 useEffect(()=>{
   if(mode!=='model'||!canvas.current)return;const host=canvas.current,controller=new AbortController();setStatus('loading');
   (async()=>{try{
     const mod=await import('./viewer.mjs');
     if(controller.signal.aborted)return;
     const api=await mod.mount(host,controller.signal,()=>{});
     if(controller.signal.aborted||!api)return;
     viewer.current=api;api.season(current.current.season);api.focus(current.current.selected?.point??null,false);setStatus('ready');
   }catch{if(!controller.signal.aborted)setStatus('error')}})();
   return ()=>{controller.abort();viewer.current=null};
 },[mode,attempt]);
 useEffect(()=>{viewer.current?.season(season)},[season]);
 function showPlace(p:Place,open=false){
   setSelected(p);setWalking(false);if(p.id==='camp')setSeason('winter');
   setBox([p.point[0]+1160,2280-p.point[1],Math.max(320,Math.min(1150,p.point[3]*1.5))]);viewer.current?.focus(p.point);
   if(open){setMode('model');document.getElementById('atlas')?.scrollIntoView({behavior:'instant'})}
 }
 function reset(){setWalking(false);setSelected(null);setBox([...home]);viewer.current?.focus(null)}
 function zoom(f:number){if(mode==='model'){viewer.current?.zoom(f);return}setBox(([x,y,z])=>[x,y,Math.min(3000,Math.max(140,z*f))])}
 function changeMode(m:'map'|'model'){setWalking(false);setMode(m);if(m==='map'&&!selected)setBox([...home])}
 function toggleWalk(){
   if(walking){setWalking(false);viewer.current?.focus(selected?.point??null);return}
   const id=selected?.id;
   if(viewer.current?.walk(id&&walkSites.includes(id)?id:'market'))setWalking(true);
 }
 const filtered=places.filter(p=>filter==='全部'||p.group===filter);
 const point=(e:React.PointerEvent<SVGSVGElement>)=>{const mat=svg.current?.getScreenCTM();return mat?new DOMPoint(e.clientX,e.clientY).matrixTransform(mat.inverse()):null};
 return <div className="fa" id="top">
 <header className="fa-nav"><a className="wordmark" href="#top"><Compass small/>霜灯港 <span>Frosthavn</span></a><nav aria-label="主导航"><a href="#atlas">地图与沙盘</a><a href="#notes">场景手记</a></nav></header>
 <main>
 <section className="atlas-cover" aria-labelledby="cover-title"><img className="chart-image" src={asset('coast-chart.webp')} alt="依据霜灯港沙盘高程绘制的海岸地形图" fetchPriority="high"/><div className="cover-ink"/><div className="cover-copy"><p className="overline"><i/> ARCTIC PASSAGE <span>/</span> FIELD ATLAS</p><h1 id="cover-title">霜灯港</h1><div className="latin-title">Frosthavn</div><p className="cover-deck">《星露谷物语》模组 · 焕新版地图预览</p><a href="#atlas" className="primary">展开地图 <span>↘</span></a><button className="cover-action" onClick={()=>{setMode('model');document.getElementById('atlas')?.scrollIntoView()}}>进入三维沙盘 ↗</button></div><div className="cover-bottom"><span>海岸地形图</span><span>3 × 3 KM <b/> 1 : 1 地形沙盘</span></div></section>
 <section className="atlas-section" id="atlas"><div className="section-header"><div><p className="section-kicker">Interactive atlas</p><h2>海湾地图集</h2></div><div className="tabs" aria-label="视图"><button aria-pressed={mode==='map'} onClick={()=>changeMode('map')}>平面地图</button><button aria-pressed={mode==='model'} onClick={()=>changeMode('model')}>三维沙盘</button></div></div>
 <div className="atlas-work"><div className="field"><div className="field-top"><span>{mode==='map'?'地表与游线':'全域地形模型'}</span><button onClick={reset}>↺ 回到全域</button></div>
 <div className={'field-view '+mode}>
 {mode==='map'?<svg ref={svg} role="group" aria-label="可拖动的霜灯港地图，在地点目录或图上选择地标" viewBox={`${box[0]-box[2]/2} ${box[1]-box[2]/2} ${box[2]} ${box[2]}`} onPointerDown={e=>{if((e.target as Element).closest('[data-pin]'))return;const p=point(e);if(p){drag.current={x:e.clientX,y:e.clientY,b:box};e.currentTarget.setPointerCapture(e.pointerId)}}} onPointerMove={e=>{const d=drag.current,m=svg.current?.getScreenCTM();if(!d||!m)return;setBox([Math.max(0,Math.min(3000,d.b[0]-(e.clientX-d.x)/m.a)),Math.max(0,Math.min(3000,d.b[1]-(e.clientY-d.y)/m.d)),d.b[2]])}} onPointerUp={()=>drag.current=null} onPointerCancel={()=>drag.current=null}>
 <image href={asset('survey.svg')} width="3000" height="3000"/>
 {places.map((p,i)=>{const active=selected?.id===p.id;const scale=box[2]/650;return <g key={p.id} data-pin={p.id} transform={`translate(${p.point[0]+1160} ${2280-p.point[1]}) scale(${scale})`} onClick={()=>showPlace(p)} className="map-pin"><title>{p.name}</title><circle r="13" fill="transparent"/><circle r={active?7.8:4.4} fill={active?'#a33a22':'#203b3a'} stroke="#fff4d9" strokeWidth="1.6"/>{(active||(!selected&&[1,4,5,9,11].includes(i)))&&<text x={p.id==='camp'?-9:10} y={p.id==='port'?16:-7} textAnchor={p.id==='camp'?'end':'start'}>{p.name}</text>}</g>})}</svg>:<><canvas ref={canvas} aria-label={walking?'拖动转头，用 WASD 或方向键步行':'可旋转、平移和缩放的霜灯港三维模型'} tabIndex={0} onKeyDown={e=>{if(e.key==='Escape'&&walking)toggleWalk()}}/>{status!=='ready'&&<div className="model-state" role="status">{status==='error'?<><p>三维模型暂时无法显示。</p><button onClick={()=>retry(n=>n+1)}>重新载入</button><button onClick={()=>changeMode('map')}>查看平面图</button></>:<p>正在展开地形与四季植被…</p>}</div>}</>}
 {mode==='map'&&<span className="north" aria-label="北方">N<i>↑</i></span>}
 {walking?<div className="walk-pad" role="group" aria-label="步行方向">{([['forward','前进','↑'],['left','左移','←'],['back','后退','↓'],['right','右移','→']] as const).map(([dir,label,arrow])=><button key={dir} className={dir} aria-label={label} onPointerDown={e=>{e.preventDefault();e.currentTarget.setPointerCapture(e.pointerId);viewer.current?.move(dir,true)}} onLostPointerCapture={()=>viewer.current?.move(dir,false)} onPointerUp={()=>viewer.current?.move(dir,false)} onPointerCancel={()=>viewer.current?.move(dir,false)} onKeyDown={e=>{if(e.key===' '){e.preventDefault();viewer.current?.move(dir,true)}}} onKeyUp={e=>{if(e.key===' ')viewer.current?.move(dir,false)}} onBlur={()=>viewer.current?.move(dir,false)}>{arrow}</button>)}</div>:<div className="zoom"><button title="放大" aria-label="放大" onClick={()=>zoom(.71)}>＋</button><button title="缩小" aria-label="缩小" onClick={()=>zoom(1.41)}>−</button></div>}</div>
 <div className="field-foot">{mode==='map'?<><span>拖动平移 · 点击地标查看地点</span><a href={asset('plan.svg')} target="_blank" rel="noreferrer">完整图例 ↗</a></>:<><span>{walking?'拖动转头 · WASD / 方向键步行':'拖动旋转 · 滚轮或双指缩放'}</span><div className="model-controls"><div className="season-tabs" role="group" aria-label="季节">{seasons.map(([id,label])=><button key={id} type="button" aria-label={label+'季'} aria-pressed={season===id} onClick={()=>{setSeason(id);if(walking)canvas.current?.focus({preventScroll:true})}}>{label}</button>)}</div><button type="button" className="walk-toggle" disabled={status!=='ready'} aria-pressed={walking} onClick={toggleWalk}>{walking?'返回鸟瞰':'第一人称步行'}</button></div></>}</div></div>
 <aside className="directory"><div className="dir-head"><h3>地点与设施</h3><span>{places.length} 处</span></div><div className="filters">{['全部','镇区','郊外','自然地标'].map(g=><button key={g} aria-pressed={filter===g} onClick={()=>setFilter(g)}>{g}</button>)}</div><div className="place-list">{filtered.map(p=><button key={p.id} aria-pressed={selected?.id===p.id} onClick={()=>showPlace(p)}><span>{p.name}</span><small>{p.en}</small><b>↗</b></button>)}</div>
 <div className="place-note" aria-live="polite"><span>{selected?.en||'The bay'}</span><h4>{selected?.name||'霜灯港全域'}</h4><p>{selected?.intro||'三公里见方的海湾里，灯市、港口和工艺院由街巷相连。沿西部驿路可去机场与冬营，登上山脊则能越过镇区望见冰川。'}</p>{selected&&<p className="access">{selected.route}</p>}</div></aside></div>
 </section>
 <section className="notes-section" id="notes"><div className="section-header"><div><p className="section-kicker">Field notes</p><h2>场景手记</h2></div><p className="note-source">取景自焕新版 Blender 场景</p></div>
 <div className="tundra-pair"><figure><img src={asset('spring-tundra.webp')} alt="初融苔原的紫红色对叶虎耳草和嫩绿柳芽" loading="lazy"/><figcaption>春日初融 <i>Spring thaw</i></figcaption></figure><figure><img src={asset('autumn-tundra.webp')} alt="秋季苔原的越橘红叶、金色矮柳与深绿苔垫" loading="lazy"/><figcaption>秋苔原 <i>Autumn tundra</i></figcaption></figure></div>
 <figure className="bay-plate"><img src={asset('hero.webp')} alt="从港池上方望向港街、彩屋和北侧山脊" loading="lazy"/><figcaption>港湾全景 <i>Harbour approach</i></figcaption></figure><div className="story-grid">{stories.map(([id,file,name,caption])=><button key={id} className="story" onClick={()=>{setFilter('全部');showPlace(places.find(p=>p.id===id)!,true)}}><img src={asset(file)} alt={name+'场景取景'} loading="lazy"/><span className="story-title">{name}<i>↗</i></span><span className="story-caption">{caption}</span></button>)}</div></section>
 </main><footer><a href="#top" className="wordmark"><Compass small/> Frosthavn</a><small>霜灯港 · 焕新版地图预览</small><a href="#top">回到页首 ↑</a></footer></div>
}
