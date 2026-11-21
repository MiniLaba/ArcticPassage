/** One original score, with phase-aligned ice / harbour arrangements. */
export type NorthernMusicState = 'loading' | 'blocked' | 'playing' | 'off' | 'error';
export interface NorthernMusic {
  start(): void;
  pause(): void;
  setEnabled(enabled: boolean): void;
  setPassage(progress: number): void;
  dispose(): void;
}
const LOOP_SECONDS = 128 * 60 / 68;
const clamp = (v: number) => Math.max(0, Math.min(1, v));
const ease = (v: number) => { const t = clamp(v); return t * t * (3 - 2 * t); };

export function createNorthernMusic(onState: (state: NorthernMusicState) => void): NorthernMusic {
  const context = new AudioContext();
  const abort = new AbortController();
  const master = context.createGain(); master.gain.value = 0; master.connect(context.destination);
  const ice = context.createGain(), harbour = context.createGain();
  ice.gain.value = 1; harbour.gain.value = 0; ice.connect(master); harbour.connect(master);
  const air = context.createGain(); air.gain.value = .025; air.connect(master);
  const cabin = context.createGain(); cabin.gain.value = .012; cabin.connect(master);
  const sources: AudioScheduledSourceNode[] = [];
  let disposed = false, enabled = true, held = false, loading = false, failed = false;
  let buffers: AudioBuffer[] | null = null, started = false, progress = 0;
  let lastState: NorthernMusicState | undefined;
  let suspendTimer: number | undefined;
  const state = (value: NorthernMusicState) => { if (!disposed && value !== lastState) { lastState = value; onState(value); } };

  // Low, filtered wind. No birds, insect samples, drums or voice.
  const size = context.sampleRate * 6, noise = context.createBuffer(1, size, context.sampleRate);
  const data = noise.getChannelData(0); let seed = 7321, previous = 0;
  for (let i = 0; i < size; i++) { seed = (Math.imul(seed, 1664525) + 1013904223) >>> 0; previous = (previous + .035 * (seed / 2147483648 - 1)) / 1.035; data[i] = previous * 3; }
  const overlap = Math.floor(context.sampleRate * .2);
  for (let i = 0; i < overlap; i++) { const t = i / overlap; data[i] = data[size - overlap + i]! * (1 - t) + data[i]! * t; }
  const wind = context.createBufferSource(), filter = context.createBiquadFilter();
  wind.buffer = noise; wind.loop = true; filter.type = 'lowpass'; filter.frequency.value = 420;
  wind.connect(filter).connect(air); wind.start(); sources.push(wind);
  for (const frequency of [62, 124]) { const motor = context.createOscillator(); motor.type = 'sine'; motor.frequency.value = frequency; motor.connect(cabin); motor.start(); sources.push(motor); }

  function setPassage(value: number) {
    progress = clamp(value); if (disposed) return;
    const warm = ease((progress - .58) / .28), at = context.currentTime;
    // Linear gains preserve the shared melody's level during the handover.
    ice.gain.setTargetAtTime(1 - warm, at, .75);
    harbour.gain.setTargetAtTime(warm, at, .75);
    cabin.gain.setTargetAtTime(.012 * (1 - ease((progress - .66) / .16)), at, .45);
    air.gain.setTargetAtTime(.018 + warm * .016, at, .8);
  }
  function update() {
    if (disposed) return;
    if (!enabled || held) { if(context.state==='running'&&suspendTimer===undefined)suspend();state('off'); return; }
    if (failed) { state('error'); return; }
    if (!buffers) { state('loading'); return; }
    if (context.state !== 'running') { state('blocked'); return; }
    if (!started) {
      const at = context.currentTime + .04;
      buffers.forEach((buffer, index) => { const source = context.createBufferSource(); source.buffer = buffer; source.loop = true; source.loopStart = 0; source.loopEnd = Math.min(LOOP_SECONDS, buffer.duration); source.connect(index === 0 ? ice : harbour); source.start(at); sources.push(source); });
      started = true; master.gain.setTargetAtTime(.72, at, 1.1); setPassage(progress);
    }
    state('playing');
  }
  async function load() {
    if (disposed || loading || buffers) return;
    loading = true; failed = false; update();
    try {
      buffers = await Promise.all(['ice-letter', 'harbour-light'].map(async name => {
        const response = await fetch('/assets/music/' + name + '.mp3', { signal: abort.signal });
        if (!response.ok) throw new Error('Music could not be loaded');
        return context.decodeAudioData(await response.arrayBuffer());
      }));
    } catch { if (!disposed) failed = true; }
    finally { loading = false; update(); }
  }
  function start() {
    if (disposed) return;
    enabled = true; held = false;window.clearTimeout(suspendTimer);suspendTimer=undefined;
    if(started){master.gain.cancelScheduledValues(context.currentTime);master.gain.setTargetAtTime(.72,context.currentTime,.15);}
    // Resume is called synchronously inside a gesture when available. A blocked
    // resume may remain pending: never await it or lock the sound control.
    void context.resume().then(update).catch(() => update());
    void load(); update();
  }
  function suspend() {
    if(context.state==='running'&&suspendTimer===undefined){
      master.gain.cancelScheduledValues(context.currentTime);master.gain.setTargetAtTime(0,context.currentTime,.025);
      suspendTimer=window.setTimeout(()=>{suspendTimer=undefined;if(!disposed&&(!enabled||held))void context.suspend().catch(()=>{});},120);
    }
    state('off');
  }
  context.onstatechange = update;
  return {
    start, setPassage,
    pause() { if (disposed) return; held = true; suspend(); },
    setEnabled(value) { if (disposed) return; enabled = value; if (value) start(); else suspend(); },
    dispose() { if (disposed) return; disposed = true;window.clearTimeout(suspendTimer);abort.abort(); context.onstatechange = null; for (const source of sources) { try { source.stop(); } catch { /* already stopped */ } } void context.close().catch(() => {}); },
  };
}
