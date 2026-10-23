"""Render the project's authored chamber scores. No random note generation.

Requires FluidSynth, ffmpeg and the separately installed GeneralUser GS 2.0.3
soundfont. The soundfont isn't distributed with the content pack.
"""
from pathlib import Path
import argparse
import json
import struct
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
PPQ = 480


def vlq(n):
    out = [n & 127]
    while n >> 7:
        n >>= 7
        out.insert(0, (n & 127) | 128)
    return bytes(out)


def midi(path, bpm, beats, bars, chords, melody, programs):
    events = [(0, b'\xff\x51\x03' + int(60000000 / bpm).to_bytes(3, 'big'))]
    for channel, program in enumerate(programs):
        events += [(0, bytes([0xC0 | channel, program])),
                   (0, bytes([0xB0 | channel, 10, [55, 75, 64][channel]])),
                   (0, bytes([0xB0 | channel, 91, 34]))]

    def note(channel, start, length, pitch, velocity):
        tick = round(start * PPQ)
        events.append((tick, bytes([0x90 | channel, pitch, velocity])))
        events.append((tick + round(length * PPQ), bytes([0x80 | channel, pitch, 0])))

    # Two complete cycles let reverb and sustained voices settle before export.
    # The final third is a settling tail, not part of the delivered loop.
    for bar in range(bars * 3):
        index = bar % bars
        chord = chords[(index // 2) % len(chords)]
        start = bar * beats
        section = index // 8
        # Bass and a quiet, open voicing; avoid dense cinematic pads.
        note(2, start, beats * .94, chord[0] - 12, 34)
        for offset, pitch in enumerate(chord):
            note(1, start + offset * .15, beats - .35 - offset * .15, pitch, 30 + offset * 2)
        # Eight-bar written phrases recur with a restrained higher-register answer.
        phrase = melody[index % 8]
        if index < 4 or index >= bars - 4:
            phrase = phrase[:1]
        for offset, length, pitch in phrase:
            transpose = 12 if section == 3 else 0
            note(0, start + offset, length * .90, pitch + transpose, 49 if section % 2 else 44)
    end = round(bars * 3 * beats * PPQ)
    events.append((end, b'\xff\x2f\x00'))
    # Note-offs sort before subsequent note-ons at shared boundaries.
    events.sort(key=lambda e: (e[0], e[1][0] != 0x80, e[1]))
    track = bytearray()
    previous = 0
    for tick, data in events:
        track.extend(vlq(tick - previous)); track.extend(data); previous = tick
    path.write_bytes(b'MThd' + struct.pack('>IHHH', 6, 0, 1, PPQ)
                     + b'MTrk' + struct.pack('>I', len(track)) + track)


# Each phrase is (beat offset, duration, MIDI pitch). Sparse rhythms leave room
# for footsteps, dialogue and surf. These are fictional game compositions,
# without a claim to represent Greenlandic traditional music.
SCORES = {
    'LumenhavenTheme': dict(title='栖光归港', bpm=78, beats=3, bars=48,
        programs=[0, 24, 42],
        chords=[[50, 57, 61, 66], [47, 54, 59, 62], [43, 50, 57, 59], [45, 52, 57, 62]],
        melody=[[(0, 1, 66), (1.5, .5, 69), (2, 1, 73)],
                [(0, 2, 71), (2, 1, 69)],
                [(0, 1.5, 66), (1.5, .5, 64), (2, 1, 62)],
                [(0, 2.5, 66)],
                [(0, 1, 67), (1, 1, 69), (2, 1, 71)],
                [(0, 2, 69), (2, 1, 66)],
                [(0, 1, 64), (1.5, .5, 66), (2, 1, 69)],
                [(0, 2.5, 62)]]),
    'IcefjordTheme': dict(title='冰山的远信', bpm=62, beats=4, bars=32,
        programs=[46, 8, 42],
        chords=[[40, 47, 54, 59], [36, 43, 50, 55], [43, 50, 57, 59], [38, 45, 52, 57]],
        melody=[[(0, 2, 71), (2.5, 1, 66)], [(0, 3, 67)],
                [(0, 1, 62), (2, 1.5, 64)], [(0, 3.5, 67)],
                [(0, 2, 69), (2.5, 1, 71)], [(0, 3, 66)],
                [(0, 1.5, 64), (2, 1, 62)], [(0, 3, 59)]]),
    'PolarNightTheme': dict(title='窗灯与长夜', bpm=58, beats=3, bars=40,
        programs=[0, 8, 48],
        chords=[[47, 54, 61, 66], [43, 50, 54, 59], [50, 57, 61, 64], [45, 52, 59, 62]],
        melody=[[(0, 2, 73)], [(0, 1, 71), (1.5, 1, 66)],
                [(0, 2.5, 69)], [(0, 2, 66)],
                [(0, 1, 64), (1.5, 1, 66)], [(0, 2.5, 69)],
                [(0, 1, 64), (1.5, 1, 62)], [(0, 2.5, 61)]]),
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--soundfont', type=Path, required=True)
    args = parser.parse_args()
    output = ROOT / 'ContentPack/assets/audio'
    source = ROOT / 'art/music'
    output.mkdir(parents=True, exist_ok=True); source.mkdir(parents=True, exist_ok=True)
    report = {}
    for name, score in SCORES.items():
        path = source / (name + '.mid')
        midi(path, **{k: v for k, v in score.items() if k != 'title'})
        duration = score['bars'] * score['beats'] * 60 / score['bpm']
        with tempfile.TemporaryDirectory(prefix='arctic-score-') as temp:
            wav = Path(temp) / 'render.wav'
            subprocess.run(['fluidsynth', '-ni', '-q', '-R', 'yes', '-C', 'no',
                            '-o', 'synth.reverb.room-size=0.26',
                            '-r', '44100', '-F', str(wav), '-T', 'wav',
                            str(args.soundfont.resolve()), str(path)], check=True)
            subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(duration),
                            '-i', str(wav), '-t', str(duration),
                            '-af', 'loudnorm=I=-23:TP=-3:LRA=8', '-ar', '44100',
                            '-c:a', 'vorbis', '-strict', '-2', '-q:a', '5',
                            str(output / (name + '.ogg'))], check=True)
        report[name] = dict(title=score['title'], seconds=duration, bpm=score['bpm'],
                            meter=f"{score['beats']}/4", bars=score['bars'])
        print(name, round(duration, 3), 'seconds', flush=True)
    (source / 'scores.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')


if __name__ == '__main__':
    main()
