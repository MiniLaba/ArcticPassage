import { useEffect, useRef, useState } from 'react';
import type { Lang } from './content';
import { northernAudio } from './NorthernAudio';
import { BayImage } from './Expedition';

export default function FlightScene({ lang, onArrive }: { lang: Lang; onArrive: () => void }) {
  const en = lang === 'en', t = (zh: string, english: string) => en ? english : zh;
  const [run, setRun] = useState(0), [stage, setStage] = useState(0), [skip, setSkip] = useState(false), [sound, setSound] = useState(false);
  const began = useRef(0);
  useEffect(() => {
    if (skip) { setStage(3); return; }
    began.current = performance.now();
    const motion = window.matchMedia('(prefers-reduced-motion: reduce)');
    if (motion.matches) { setSkip(true); setStage(3); return; }
    const timers = [window.setTimeout(() => setStage(1), 2100), window.setTimeout(() => setStage(2), 4900), window.setTimeout(() => setStage(3), 9000)];
    return () => timers.forEach(window.clearTimeout);
  }, [run, skip]);
  useEffect(() => {
    if (!sound || skip || stage === 3) return;
    let stopped = false, audio: Awaited<ReturnType<typeof northernAudio>> | undefined;
    void northernAudio('flight', Math.max(.4, (9000 - performance.now() + began.current) / 1000)).then(value => { if (stopped) value.stop(); else audio = value; }).catch(() => setSound(false));
    return () => { stopped = true; audio?.stop(); };
    // Stage labels do not restart the engine.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [sound, skip, run]);
  useEffect(() => { if (stage === 3) setSound(false); }, [stage]);
  function replay() { setSkip(false); setStage(0); setRun(n => n + 1); }
  const labels = en ? ['Across the fjord', 'On final approach', 'Touchdown · slowing down', 'Welcome to Frosthavn'] : ['越过冰峡湾', '对准雪跑道', '接地 · 减速滑行', '欢迎来到霜灯港'];
  return <div className="nf-flight">
    <div className="xp-flight-head"><span>MOONBIRD AIR <i>MM 027</i></span><span>{t('月月鸟航空 · 霜灯港', 'FROSTHAVN / NORTHSTAR')}</span></div>
    <div className={'xp-film ' + (skip ? 'is-landed' : '')} key={run} role="img" aria-label={t('网页演出：滑橇飞机越过同一片海湾，在雪跑道接地、减速并停靠。','Website film: a ski aircraft crosses the bay, touches down on the snow runway, slows and parks.')}>
      <div className="xp-film-camera"><BayImage eager/><i className="xp-film-shadow"/><img className="xp-film-plane" src="/assets/prologue/aircraft.webp" width="600" height="224" alt=""/><i className="xp-film-dust"/></div>
      <div className="xp-film-label"><div><span aria-live="polite">{labels[stage]}</span><div className="xp-film-progress">{labels.map((_, i) => <i className={i <= stage ? 'done' : ''} key={i}/>)}</div></div><small>{t('网页艺术演出 · 非游戏录屏', 'WEBSITE ART · NOT GAMEPLAY')}</small></div>
    </div>
    <div className="nf-flight-controls">
      {stage < 3 ? <button type="button" onClick={() => { setSkip(true); setStage(3); }}>{t('跳过，直接抵达 ↗', 'Skip to arrival ↗')}</button> : <button type="button" onClick={replay}>{t('重看这次降落 ↻', 'Replay the landing ↻')}</button>}
      <button type="button" aria-pressed={sound} disabled={stage === 3} onClick={() => setSound(!sound)}>{sound ? t('声音开', 'Sound on') : t('声音关', 'Sound off')}</button>
    </div>
    {stage === 3 && <div className="xp-flight-welcome"><span className="xp-kicker">A WINDOW LIT FOR YOU</span><h2 id="fh-dialog-title">{t('下一站，霜灯港。', 'Next stop: Frosthavn.')}</h2><p>{t('海湾到了，炉火还温着。把行李放下，先在镇里走走。', 'The bay is here, and the fire is still warm. Set your bags down. Take a walk through town.')}</p><button type="button" className="xp-button" onClick={onArrive}>{t('进入小镇 →', 'Enter the town →')}</button></div>}
    {stage !== 3 && <span id="fh-dialog-title" className="xp-sr-only">{t('搭乘月月鸟航空','Fly with Moonbird Air')}</span>}
  </div>;
}
