/** Local wind / water / propeller synthesis. Only started by a deliberate click. */
export async function northernAudio(kind: 'coast' | 'flight', duration = 9) {
  const ctx = new AudioContext();
  await ctx.resume();
  const master = ctx.createGain();
  master.gain.setValueAtTime(0, ctx.currentTime);
  master.gain.linearRampToValueAtTime(kind === 'coast' ? .13 : .09, ctx.currentTime + .5);
  master.connect(ctx.destination);
  const size = ctx.sampleRate * 6, overlap = Math.floor(ctx.sampleRate * .25);
  const samples = new Float32Array(size + overlap);
  let seed = 7321, last = 0;
  for (let i = 0; i < samples.length; i++) {
    seed = (Math.imul(seed, 1664525) + 1013904223) >>> 0;
    last = (last + .035 * (seed / 2147483648 - 1)) / 1.035;
    samples[i] = last * 4;
  }
  const buffer = ctx.createBuffer(1, size, ctx.sampleRate), data = buffer.getChannelData(0);
  data.set(samples.subarray(0, size));
  for (let i = 0; i < overlap; i++) {
    const p = i / overlap * Math.PI / 2;
    data[i] = samples[size + i]! * Math.cos(p) + samples[i]! * Math.sin(p);
  }
  const wind = ctx.createBufferSource();
  wind.buffer = buffer; wind.loop = true;
  const filter = ctx.createBiquadFilter();
  filter.type = 'lowpass'; filter.frequency.value = kind === 'coast' ? 520 : 300;
  wind.connect(filter).connect(master); wind.start();
  const sources: AudioScheduledSourceNode[] = [wind];
  const cabin = ctx.createGain(); cabin.gain.value = 0; cabin.connect(master);
  if (kind === 'coast') for (const hz of [62, 124]) {
    const motor=ctx.createOscillator(),level=ctx.createGain();motor.type='sine';motor.frequency.value=hz;level.gain.value=.09;motor.connect(level).connect(cabin);motor.start();sources.push(motor);
  }
  if (kind === 'coast') {
    const tide = ctx.createOscillator(), swell = ctx.createGain();
    tide.frequency.value = .11; swell.gain.value = .025;
    tide.connect(swell).connect(master.gain); tide.start(); sources.push(tide);
  } else {
    for (const frequency of [63, 126]) {
      const prop = ctx.createOscillator(), level = ctx.createGain();
      prop.type = 'triangle'; prop.frequency.setValueAtTime(frequency, ctx.currentTime);
      prop.frequency.linearRampToValueAtTime(frequency * .66, ctx.currentTime + duration);
      level.gain.value = .11; prop.connect(level).connect(master); prop.start(); sources.push(prop);
    }
    master.gain.setValueAtTime(.09, ctx.currentTime + Math.max(.6, duration * .6));
    master.gain.linearRampToValueAtTime(0, ctx.currentTime + duration);
  }
  let stopped = false;
  const stop = () => {
    if (stopped) return; stopped = true;
    master.gain.cancelScheduledValues(ctx.currentTime);
    master.gain.setTargetAtTime(0, ctx.currentTime, .025);
    window.setTimeout(() => { for (const source of sources) { try { source.stop(); } catch { /* already stopped */ } } void ctx.close(); }, 120);
  };
  const setPassage = (progress:number) => {
    if(stopped || kind!=='coast')return;
    const flight=progress<.7?1:Math.max(0,1-(progress-.7)/.17);
    cabin.gain.setTargetAtTime(flight,ctx.currentTime,.45);
    filter.frequency.setTargetAtTime(520-230*flight,ctx.currentTime,.6);
  };
  return { stop, setPassage };
}
