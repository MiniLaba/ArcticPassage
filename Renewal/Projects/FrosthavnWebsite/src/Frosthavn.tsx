import { useEffect, useRef, useState } from 'react';
import { copy, DOWNLOAD, type Lang } from './content';
import FlightScene from './FlightScene';
import InstallGuide from './InstallGuide';
import { createNorthernMusic, type NorthernMusic, type NorthernMusicState } from './NorthernMusic';
import './Frosthavn.css';
import './Upgrade.css';
import './Prologue.css';
import ScrollJourney from './ScrollJourney';
import WindowFlight from './WindowFlight';
import './ScrollJourney.css';
import { Atlas, Windows, FieldJournal, Chronicle, BayImage } from './Expedition';
import SeasonVoyage from './SeasonVoyage';
import './PlayerExperience.css';
import { TrailerSection } from './Trailer';

type Modal = 'flight' | 'install' | null;
function Arrow({ diagonal = false }: { diagonal?: boolean }) {
  return <svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d={diagonal ? 'M5 19 19 5M5 5h14v14' : 'M4 12h16m-6-6 6 6-6 6'} stroke="currentColor" strokeWidth="1.4"/></svg>;
}
function Moonbird() {
  return <svg viewBox="0 0 64 64" aria-hidden="true"><path d="M45 8A25 25 0 1 0 55 43 22 22 0 0 1 45 8Z" fill="currentColor"/><path d="m21 34 8-5 8 5 11-7" stroke="currentColor" strokeWidth="3" fill="none" strokeLinecap="round"/></svg>;
}
function Star() { return <svg viewBox="0 0 24 24" aria-hidden="true"><path d="m12 1 2 8 9 3-9 2-2 9-3-9-8-2 8-3Z" fill="currentColor"/></svg>; }
function Dialog({ modal, close, lang, arrive }: { modal: Modal; close: () => void; lang: Lang; arrive: () => void }) {
  const ref = useRef<HTMLDialogElement>(null);
  useEffect(() => {
    if (modal && !ref.current?.open) ref.current?.showModal();
    if (!modal) ref.current?.close();
  }, [modal]);
  return <dialog ref={ref} className={'fh-dialog fh-dialog-v2 ' + (modal === 'flight' ? 'fh-flight-dialog' : 'fh-install-dialog')} aria-labelledby="fh-dialog-title" onCancel={close} onClick={e => { if (e.target === ref.current) close(); }}>
    <div className="sx-dialog-bar"><span>{lang==='en'?'MOONBIRD AIR / BOARDING GUIDE':'月月鸟航空 / 登机指南'}</span><button type="button" className="fh-close" onClick={close} aria-label={copy[lang].close}>×</button></div>
    {modal === 'flight' && <FlightScene lang={lang} onArrive={arrive}/>}
    {modal === 'install' && <InstallGuide lang={lang}/>}
  </dialog>;
}
function Routes({ en }: { en: boolean }) {
  const nodes: [string, number, number, string][] = [
    ['airport', 65, 166, en ? 'AIRSTRIP' : '雪原机场'], ['town', 210, 240, en ? 'TOWN' : '镇区'],
    ['harbour', 390, 240, en ? 'HARBOUR' : '渔港'], ['fjord', 550, 240, en ? 'ICEFJORD' : '峡湾'],
    ['tundra', 210, 115, en ? 'TUNDRA' : '苔原'], ['trail', 390, 45, en ? 'TRAIL' : '山路'],
    ['camp', 390, 145, en ? 'CAMP' : '营地'], ['glacier', 550, 45, en ? 'GLACIER' : '冰川'],
  ];
  return <div className="fh-route-diagram"><svg viewBox="0 0 620 295" role="img" aria-label={en ? 'Actual connections: airstrip to town; town to tundra and harbour; harbour boat to icefjord; tundra to camp and trail; trail to camp and glacier.' : '实际连接：机场到镇区，镇区到苔原与渔港，渔港乘船到峡湾；苔原到营地与山路，山路到营地及冰川。'}>
    <g fill="none" stroke="#8fa7aa" strokeWidth="1.5"><path d="m65 166 145 74h180M210 240V115l180 30M210 115l180-70h160M390 45v100"/><path d="M390 240h160" stroke="#b87455" strokeDasharray="5 5"/></g>
    {nodes.map(([id, x, y, label]) => <g key={id}><circle cx={x} cy={y} r="5" fill="#f3eee2" stroke="#55777c"/><text x={x} y={y + 24} textAnchor="middle" fill="#35555e" fontSize={en ? '10' : '13'}>{label}</text></g>)}
    <text x="470" y="228" textAnchor="middle" fill="#a5644a" fontSize="10">{en ? 'BOAT' : '固定船线'}</text>
  </svg><p>{en ? 'Paths & crossings. Solid: walk or transfer. Dashed: the boat route after repairs.' : '步道与航线 · 实线为步行与接驳，虚线为修船后开放的船线。'}</p></div>;
}

export default function Frosthavn() {
 const [lang,setLang]=useState<Lang>('zh'),[menu,setMenu]=useState(false),[modal,setModal]=useState<Modal>(null);
 const [selected,setSelected]=useState(0),[musicState,setMusicState]=useState<NorthernMusicState>('loading'),[opening,setOpening]=useState(false),[showMusicDock,setShowMusicDock]=useState(false);
 const [filmPlaying,setFilmPlaying]=useState(false),currentFilm=useRef(false);
 const sound=musicState==='playing',soundBusy=musicState==='loading';
 const audio=useRef<NorthernMusic|null>(null),soundWanted=useRef(true),currentSound=useRef<NorthernMusicState>('loading'),currentModal=useRef<Modal>(null);currentModal.current=modal;
 const en=lang==='en',c=copy[lang],t=(zh:string,english:string)=>en?english:zh;
 useEffect(()=>{
  try{const saved=localStorage.getItem('frosthavn-language');if(saved==='en'||saved==='zh')setLang(saved);}catch{/* optional preference */}
  if(location.hash==='#guide')setModal('install');
  if(location.hash==='#watch'){history.replaceState(null,'','#film');requestAnimationFrame(()=>document.getElementById('film')?.scrollIntoView({behavior:'instant'}));}
  let timer:number|undefined;
  try{if(!sessionStorage.getItem('frosthavn-prologue')&&!window.matchMedia('(prefers-reduced-motion: reduce)').matches){setOpening(true);timer=window.setTimeout(()=>{setOpening(false);sessionStorage.setItem('frosthavn-prologue','seen');},1200);}}catch{/* content is always available */}
  const journey=document.getElementById('top');const observer=new IntersectionObserver(entries=>{const entry=entries[0];if(entry)setShowMusicDock(!entry.isIntersecting);});if(journey)observer.observe(journey);
  return()=>{window.clearTimeout(timer);observer.disconnect();};
 },[]);
 useEffect(()=>{document.documentElement.lang=en?'en':'zh-CN';document.title=en?'Frosthavn — A light left on for you':'霜灯港 Frosthavn — 一盏为你亮起的灯';},[en]);
 useEffect(()=>{const escape=(e:KeyboardEvent)=>{if(e.key==='Escape')setMenu(false);};window.addEventListener('keydown',escape);return()=>window.removeEventListener('keydown',escape);},[]);
 useEffect(()=>{
  try{soundWanted.current=sessionStorage.getItem('frosthavn-music')!=='off';}catch{/* default is enabled */}
  try{audio.current=createNorthernMusic(value=>{currentSound.current=value;setMusicState(value);});}catch{currentSound.current='error';setMusicState('error');return;}
  audio.current.setPassage(Number(document.getElementById('top')?.style.getPropertyValue('--journey-progress')||'0'));
  if(soundWanted.current&&!document.hidden)audio.current.start();else audio.current.setEnabled(false);
  const unlock=(event:Event)=>{
   if(event.target instanceof Element&&event.target.closest('[data-audio-toggle],[data-film-trigger]'))return;
   if(soundWanted.current&&!document.hidden&&currentModal.current!=='flight'&&!currentFilm.current&&currentSound.current!=='playing')audio.current?.start();
  };
  const visible=()=>{if(document.hidden)audio.current?.pause();else if(soundWanted.current&&currentModal.current!=='flight'&&!currentFilm.current)audio.current?.start();};
  document.addEventListener('pointerdown',unlock,{capture:true});document.addEventListener('keydown',unlock,{capture:true});document.addEventListener('touchend',unlock,{capture:true,passive:true});document.addEventListener('visibilitychange',visible);
  return()=>{document.removeEventListener('pointerdown',unlock,{capture:true});document.removeEventListener('keydown',unlock,{capture:true});document.removeEventListener('touchend',unlock,{capture:true});document.removeEventListener('visibilitychange',visible);audio.current?.dispose();audio.current=null;};
 },[]);
 useEffect(()=>{if(modal==='flight'||filmPlaying)audio.current?.pause();else if(soundWanted.current&&!document.hidden)audio.current?.start();},[modal,filmPlaying]);
 useEffect(()=>{const passage=(event:Event)=>audio.current?.setPassage((event as CustomEvent<number>).detail);window.addEventListener('frosthavn:passage',passage);return()=>window.removeEventListener('frosthavn:passage',passage);},[]);
 function toggleSound(){
  const off=currentSound.current==='playing'||currentSound.current==='loading'&&soundWanted.current;
  soundWanted.current=!off;try{sessionStorage.setItem('frosthavn-music',off?'off':'on');}catch{/* optional preference */}
  audio.current?.setEnabled(!off);
 }

 function filmPlayback(playing:boolean){currentFilm.current=playing;if(playing)audio.current?.pause();setFilmPlaying(playing);}
 function toggleLang(){const next=en?'zh':'en';setLang(next);try{localStorage.setItem('frosthavn-language',next);}catch{/* optional */}}
 function goPlace(i:number){setSelected(i);document.getElementById('explore')?.scrollIntoView({behavior:window.matchMedia('(prefers-reduced-motion: reduce)').matches?'instant':'smooth'});}
 function beginFlight(){if(window.matchMedia('(prefers-reduced-motion: reduce)').matches){goPlace(0);return;}window.dispatchEvent(new Event('frosthavn:fly'));}
 function arrive(){setModal(null);window.requestAnimationFrame(()=>goPlace(0));}
 return <div data-music-state={musicState} className={'fh-site fh-v2 xp-site '+(en?'fh-en xp-en ':'')+(opening?'xp-opening':'')}>
  <a className="fh-skip" href="#main">{t('跳至正文','Skip to content')}</a>
  <header className="xp-header"><a href="#top" onClick={event=>{event.preventDefault();window.scrollTo({top:0,behavior:'smooth'});}} className="xp-brand" aria-label="Frosthavn"><Moonbird/><span>FROSTHAVN<small>{t('霜灯港 / 北极生活','AN ARCTIC LIFE')}</small></span></a><nav id="xp-navigation" className={menu?'is-open':''} aria-label={t('主导航','Main navigation')}>{[['seasons',t('四季','Seasons')],['explore',t('海湾','The bay')],['residents',t('邻居','The people')],['nature',t('自然手记','Field notes')],['story',t('旅程','The story')]].map(([id,label])=><a key={id} href={'#'+id} onClick={()=>setMenu(false)}>{label}</a>)}<button type="button" onClick={()=>{setMenu(false);setModal('install');}}>{t('登机指南','Boarding guide')}</button></nav><div className="xp-header-actions"><button type="button" onClick={toggleLang} aria-label={en?'切换为中文':'Switch to English'}>{en?'中':'EN'}</button><a href="#download" className="xp-header-download">{t('下载','Download')} ↗</a><button type="button" className="xp-menu" aria-controls="xp-navigation" aria-expanded={menu} aria-label={t('打开导航','Open navigation')} onClick={()=>setMenu(!menu)}><i/><i/></button></div></header>
  <main id="main">
   <ScrollJourney en={en}>{caption=><section className="xp-hero"><div className="sx-arrival-world" aria-hidden="true"><img src="/assets/experience/original-bay.webp" width="4060" height="1652" alt=""/></div>{caption}<div className="xp-hero-coordinate">MOONBIRD AIR / APPROACHING THE NORTH</div><div className="xp-hero-copy"><span className="xp-kicker"><Star/>{t('献给嘶鸣的一封北方来信','A NORTHERN LETTER FOR SIMING')}</span><h1>{t('一张机票，\n一个北方。','A ticket.\nA little further north.')}</h1><p>{t('越过熟悉的田野，在岩岸与冰山之间，\n有一座小镇，为你留了一盏灯。','Beyond the familiar fields, between bare rock and icebergs, a little town has left a light on for you.')}</p><button type="button" className="xp-button" onClick={beginFlight}>{t('搭乘月月鸟航空','Fly with Moonbird Air')}<Arrow diagonal/></button><a className="xp-hero-wander" href="#explore">{t('先在海湾走走','Wander through the bay')}<Arrow/></a><span className="xp-hero-game">AN ARCTIC JOURNEY / FOR SIMING</span></div><div className="xp-cabin-window"><div className="xp-cabin-view" role="img" aria-label={t('旅客机窗视角：越过冰海与彩屋，在雪跑道接地滑行，停稳后展开海湾。','Passenger window: cross the icy bay, touch down and slow on the snow runway, then open the view after parking.')}><WindowFlight/><div className="xp-cabin-glass"/><span className="xp-window-label">SOMEWHERE NORTH.<br/>A LIGHT LEFT ON FOR YOU.</span></div><span className="xp-cabin-label">06A <span>YOUR WINDOW NORTH</span> ✦</span></div><div className="xp-hero-bottom"><span>THE VALLEY <i>⟶</i> FROSTHAVN</span><a href="#explore">{t('滚动，靠近北方','SCROLL TO FOLLOW THE JOURNEY')} ↓</a><button type="button" data-audio-toggle onClick={toggleSound} aria-pressed={sound}>{sound?t('关闭配乐','Sound off'):soundBusy?t('配乐载入中','Loading music'):t('开启配乐','Sound on')} <span>{sound?'ııı':'◌'}</span></button><i className="xp-scroll-track" aria-hidden="true"/></div></section>}</ScrollJourney>
   <div className="xp-wordmark" aria-hidden="true">FROSTHAVN<span>霜 灯 港</span></div>
   <SeasonVoyage lang={lang}/>
   <Atlas lang={lang} selected={selected} onSelect={setSelected} routes={<Routes en={en}/>}/>
   <Windows lang={lang} onPlace={goPlace}/>
   <section className="xp-postcards" id="days"><div className="xp-section-head"><div><span className="xp-kicker">SMALL THINGS / A WIDER WORLD</span><h2>{t('把日常，\n过到北极去。','Little things.\nA wider world.')}</h2></div><p>{t('一根钓竿，一支犬队。\n两张来自游戏里的明信片。','A fishing line. A dog team.\nTwo postcards from the game itself.')}</p></div><div className="xp-postcard-grid">{[{image:'ice-fishing',title:c.fishing,body:c.fishingBody},{image:'dog-team',title:c.sled,body:c.sledBody}].map((card,i)=><figure className="xp-postcard" key={card.image}><div><img src={'/assets/'+card.image+'.webp'} alt={card.title} width="1100" height="720" loading="lazy"/><span>0{i+1} / NORTHERN DAYS</span></div><figcaption><h3>{card.title}</h3><p>{card.body}</p><small>{t('FROSTHAVN / 海湾日常','FROSTHAVN / NORTHERN DAYS')}</small></figcaption></figure>)}</div><div className="xp-day-cycle">{[t('钓获','A catch'),t('加工','Time & care'),t('交货','A delivery'),t('让港口亮起灯','A harbour brought to life')].map((label,i)=><span key={label}><small>0{i+1}</small>{label}{i<3&&<Arrow/>}</span>)}</div></section>
   <FieldJournal lang={lang}/>
   <Chronicle lang={lang}/>
   <TrailerSection en={en} onPlaybackChange={filmPlayback}/>
   <section className="xp-departure" id="passage"><div className="xp-departure-copy"><span className="xp-kicker">05 / YOUR PASSAGE NORTH</span><h2>{t('下一张机票，\n留给你。','The next ticket\nis yours.')}</h2><p>{t('准备好游戏与行囊。\n从山谷巴士站出发，让故事从抵达开始。','Prepare your game and pack a little curiosity.\nLeave from the Valley bus stop. Let arrival be the beginning.')}</p><button type="button" className="xp-button" onClick={()=>setModal('install')}>{t('打开完整登机指南','Open the boarding guide')}<Arrow diagonal/></button><small>{t('收拾好行囊，从一封月月鸟的来信开始。','Pack a little curiosity. Begin with a letter from Moonbird.')}</small></div><div className="fh-ticket"><div className="fh-ticket-top"><span><Moonbird/>{c.ticketAirline}</span><small>BOARDING PASS</small></div><div className="fh-ticket-main"><span className="fh-eyebrow">{c.ticketClass}</span><div className="fh-ticket-route"><div><small>FROM</small><strong>{c.ticketFrom}</strong><em>THE VALLEY</em></div><span className="fh-ticket-plane">✈</span><div><small>TO</small><strong>{c.ticketTo}</strong><em>FROSTHAVN</em></div></div><div className="fh-ticket-info"><span>FLIGHT<strong>MM 027</strong></span><span>ARRIVAL<strong>{t('北辰雪跑道','NORTHSTAR RUNWAY')}</strong></span></div></div><div className="fh-ticket-stub"><div className="fh-barcode" aria-hidden="true"/><span>{t('一盏为你亮起的灯','A LIGHT LEFT ON FOR YOU')}<small>MOONBIRD AIR / FROSTHAVN</small></span><Star/></div><button type="button" className="fh-ticket-link" onClick={()=>setModal('install')}>{c.ticketButton}<Arrow diagonal/></button></div></section>
   <section className="fh-faq fh-section xp-faq"><span className="xp-kicker">BEFORE YOU GO</span><h2>{c.faq}</h2><div>{c.faqs.map(([q,a])=><details key={q}><summary>{q}<span>+</span></summary><p>{a}</p></details>)}</div></section>
   <section className="xp-download" id="download"><BayImage mode="aurora" alt=""/><div className="xp-download-shade"/><div className="xp-download-content"><Moonbird/><span className="xp-kicker">A LIGHT LEFT ON FOR YOU</span><h2>{t('海湾在这里。\n故事，等你开始。','The bay is here.\nThe story is yours.')}</h2><a className="xp-button" href={DOWNLOAD}>{t('开启你的北方旅程','Begin your northern days')}<Arrow diagonal/></a><p>{t('免费下载 · 电脑版 · 需《星露谷物语》','FREE DOWNLOAD · DESKTOP · STARDEW VALLEY REQUIRED')}</p><button type="button" className="xp-text-button" onClick={()=>setModal('install')}>{t('第一次安装？查看登机指南 ↗','First visit? Open the boarding guide ↗')}</button></div></section>

  </main>
  <footer className="xp-footer"><a className="xp-brand" href="#top" onClick={event=>{event.preventDefault();window.scrollTo({top:0,behavior:'smooth'});}}><Moonbird/><span>FROSTHAVN<small>{t('霜灯港 / 献给嘶鸣','A NORTHERN LETTER FOR SIMING')}</small></span></a><nav aria-label={t('页脚导航','Footer navigation')}><a href="#film">{t('宣传片','The film')}</a><a href="#seasons">{t('海湾四季','The seasons')}</a><a href="#residents">{t('认识邻居','The neighbours')}</a><button type="button" onClick={()=>setModal('install')}>{t('登机指南','Boarding guide')}</button></nav><p>{t('献给《星露谷物语》与每一个向往北方的人。','For Stardew Valley, and those who dream of the north.')}<br/>Stardew Valley © ConcernedApe.</p><span>A LIGHT LEFT ON FOR YOU.<br/>FOR SIMING, FROM THE NORTH.</span></footer>
  <button type="button" className="sx-music-dock" hidden={!showMusicDock} data-audio-toggle data-state={musicState} onClick={toggleSound} aria-pressed={sound} aria-label={sound?t('关闭背景音乐','Turn background music off'):soundBusy?t('取消音乐播放','Cancel music playback'):t('开启背景音乐','Turn background music on')}><span className="sx-music-bars" aria-hidden="true"><i/><i/><i/><i/></span><span><strong>{t('冰海来信','A LETTER FROM THE ICE')}</strong><small>{sound?t('配乐已开启 · 点击关闭','PLAYING · SOUND OFF'):soundBusy?t('配乐载入中','LOADING'):t('点击开启配乐','TAP FOR SOUND')}</small></span><span aria-hidden="true">{sound?'Ⅱ':'♪'}</span></button>
  <Dialog modal={modal} close={()=>setModal(null)} lang={lang} arrive={arrive}/>
 </div>;
}
