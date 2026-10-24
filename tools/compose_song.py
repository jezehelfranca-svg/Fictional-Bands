#!/usr/bin/env python3
"""Generate Suno composition briefs and optional editable, deterministic MIDI sketches.

Standard-library only. MIDI is an original rule-based sketch, not output from Suno.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
import re
import struct
import unicodedata
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TICKS = 480
PITCHES = {'C': 0, 'C#': 1, 'DB': 1, 'D': 2, 'D#': 3, 'EB': 3, 'E': 4,
           'F': 5, 'F#': 6, 'GB': 6, 'G': 7, 'G#': 8, 'AB': 8, 'A': 9,
           'A#': 10, 'BB': 10, 'B': 11}
NOTE_NAMES = ['C', 'C#', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'Ab', 'A', 'Bb', 'B']
SCALES = {'major': (0, 2, 4, 5, 7, 9, 11), 'minor': (0, 2, 3, 5, 7, 8, 10)}
KEY_SIGNATURES = {
    'major': {'C': 0, 'G': 1, 'D': 2, 'A': 3, 'E': 4, 'B': 5, 'F#': 6,
              'C#': 7, 'F': -1, 'Bb': -2, 'Eb': -3, 'Ab': -4, 'Db': -5, 'Gb': -6, 'Cb': -7},
    'minor': {'A': 0, 'E': 1, 'B': 2, 'F#': 3, 'C#': 4, 'G#': 5, 'D#': 6,
              'A#': 7, 'D': -1, 'G': -2, 'C': -3, 'F': -4, 'Bb': -5, 'Eb': -6, 'Ab': -7},
}
FORMS = {
    'pop': [('Intro', 4, .2), ('Verse 1', 16, .5), ('Pre-Chorus', 8, .7),
            ('Chorus', 16, 1.), ('Verse 2', 16, .6), ('Pre-Chorus 2', 8, .8),
            ('Chorus 2', 16, 1.), ('Bridge', 8, .45), ('Final Chorus', 16, 1.), ('Outro', 4, .2)],
    'lofi': [('Intro', 8, .25), ('Verse 1', 16, .5), ('Chorus', 16, .8),
             ('Interlude', 8, .35), ('Verse 2', 16, .6), ('Chorus 2', 16, .8),
             ('Instrumental', 16, .65), ('Outro', 8, .2)],
    'cinematic': [('Atmospheric Intro', 8, .15), ('Theme A', 16, .45),
                  ('Development', 16, .6), ('Build', 8, .75), ('Climax', 16, 1.),
                  ('Breakdown', 8, .25), ('Reprise', 16, .85), ('Outro', 8, .15)],
    'progressive': [('Intro', 8, .3), ('Verse 1', 16, .5), ('Chorus', 16, .8),
                    ('Instrumental A', 16, .8), ('Verse 2', 16, .55),
                    ('Odd-Meter Breakdown', 16, 1.), ('Solo', 16, .9),
                    ('Final Chorus', 16, 1.), ('Outro', 8, .25)],
    'rnb': [('Intro', 4, .2), ('Verse 1', 16, .45), ('Pre-Chorus', 8, .6),
            ('Chorus', 16, .85), ('Post-Chorus', 8, .7), ('Verse 2', 16, .6),
            ('Chorus 2', 16, .9), ('Bridge', 8, .4), ('Final Chorus', 16, 1.), ('Outro', 4, .2)],
}
PROGRESSIONS = [([0, 4, 5, 3], [0, 5, 3, 4]), ([0, 3, 4, 0], [5, 3, 0, 4]),
                ([0, 5, 1, 4], [0, 3, 5, 4]), ([5, 3, 0, 4], [3, 4, 0, 5])]


@dataclass(frozen=True)
class Track:
    index: int
    title: str
    description: str


def field(text: str, name: str) -> str:
    m = re.search(r'^' + re.escape(name) + r':\s*(.+)$', text, re.M | re.I)
    return m.group(1).strip() if m else ''


def block(text: str, label: str) -> str:
    m = re.search(r'^' + re.escape(label) + r'\s*\n', text, re.M | re.I)
    if not m:
        return ''
    rest = text[m.end():]
    stop = re.search(r'\n\s*\n(?=[A-Z][^\n]{1,65}:|For Fans Of:|Fictional Band Name:|Consolidated Brief Summary|Suno Style Prompt|New Song Titles)', rest)
    return rest[:stop.start()].strip() if stop else rest[:1100].strip()


def parse_tracks(text: str, catalog: str) -> list[Track]:
    anchor = 'New Song Titles — 2026 Expansion' if catalog == 'expansion' else 'Fictional EP Tracklist'
    start = text.find(anchor)
    if start < 0:
        return []
    part = text[start + len(anchor):]
    if catalog == 'ep':
        part = re.split(r'^Consolidated Brief Summary|^New Song Titles', part, maxsplit=1, flags=re.M)[0]
    entries = list(re.finditer(r'^Track\s+(\d+):\s*(.+?)\s*$', part, flags=re.M))
    results = []
    for i, match in enumerate(entries):
        section = part[match.end():entries[i+1].start() if i+1 < len(entries) else len(part)]
        desc = field(section, '- Song Description') or field(section, '- Story & Context')
        if not desc:
            m = re.search(r'^- (?:Song Description|Story & Context):\s*(.+)$', section, re.M)
            desc = m.group(1).strip() if m else ''
        results.append(Track(int(match.group(1)), match.group(2).strip(), desc))
    return results


def parse_band(path: Path) -> dict:
    source = path.read_text(encoding='utf-8', errors='replace')
    if not field(source, 'Fictional Band Name'):
        raise ValueError(f'Not a Fictional-Bands profile: {path}')
    pulse = re.search(r'^\*?\s*Tempo & Pulse:\s*(.+)$', source, flags=re.M | re.I)
    tempo_line = pulse.group(1) if pulse else ''
    ranges = re.findall(r'(\d{2,3})\s*[-–]\s*(\d{2,3})\s*BPM', tempo_line, re.I)
    if ranges:
        tempo = round(sum((int(a)+int(b))/2 for a, b in ranges) / len(ranges))
    else:
        singles = re.findall(r'\b(\d{2,3})\s*BPM\b', tempo_line, re.I)
        tempo = int(singles[0]) if singles else 110
    harmony = re.search(r'^\*?\s*Harmonic Palette:\s*(.+)$', source, re.M | re.I)
    harmony = harmony.group(1).strip() if harmony else ''
    genre = field(source, 'Genre') or source.splitlines()[0].strip()
    style = block(source, 'Suno Style Prompt')
    style = re.split(r'\n\s*New Song Titles', style, maxsplit=1)[0].strip()
    instruments = block(source, 'Typical Instruments Used:') or block(source, 'Typical Instruments:')
    return {'name': field(source, 'Fictional Band Name'), 'genre': genre,
            'ingredients': field(source, 'Ingredients'), 'tempo': max(45, min(210, tempo)),
            'harmony': harmony, 'instruments': instruments, 'style': style,
            'source': source, 'source_sha256': hashlib.sha256(source.encode()).hexdigest()}


def choose_form(profile: dict, requested: str) -> str:
    if requested != 'auto':
        return requested
    text = (profile['ingredients'] + ' ' + profile['genre']).lower()
    for words, name in [(('progressive', 'djent', 'math rock', 'prog rock'), 'progressive'),
                        (('cinematic', 'film score', 'orchestral'), 'cinematic'),
                        (('lo-fi', 'lofi', 'jazz hop'), 'lofi'),
                        (('r&b', 'neo soul', 'nu soul'), 'rnb')]:
        if any(w in text for w in words):
            return name
    return 'pop'


def choose_key(profile: dict, requested: str) -> tuple[str, str, int]:
    if requested == 'auto':
        requested = 'C minor' if re.search(r'\bminor\b', profile['harmony'], re.I) else 'C major'
    m = re.fullmatch(r'([A-Ga-g])([#b]?)\s+(major|minor)', requested.strip(), re.I)
    if not m:
        raise ValueError('Key must be e.g. "C major", "F# minor", "Bb major", or "auto"')
    root = m.group(1).upper() + m.group(2)
    mode = m.group(3).lower()
    canonical = root[0] + root[1:]
    if canonical not in KEY_SIGNATURES[mode]:
        raise ValueError(f'Unsupported key signature: {canonical} {mode}')
    return canonical, mode, PITCHES[canonical.upper()]


def validate_meter(meter: str) -> tuple[int, int]:
    m = re.fullmatch(r'(\d{1,2})/(2|4|8|16)', meter)
    if not m:
        raise ValueError('Meter must be e.g. 4/4, 5/4, or 7/8')
    numerator, denominator = map(int, m.groups())
    if not (1 <= numerator <= 16):
        raise ValueError('Meter numerator must be between 1 and 16')
    return numerator, denominator


def slugify(value: str) -> str:
    value = unicodedata.normalize('NFKD', value)
    value = value.encode('ascii', 'ignore').decode().lower()
    return re.sub(r'[^a-z0-9]+', '-', value).strip('-') or 'untitled'


def chord_notes(degree: int, root_pc: int, mode: str, octave: int = 4) -> list[int]:
    scale = SCALES[mode]
    return [12 * octave + root_pc + scale[(degree+step) % 7] + (12 if degree+step >= 7 else 0)
            for step in (0, 2, 4)]


def chord_name(degree: int, root_pc: int, mode: str) -> str:
    pitches = chord_notes(degree, root_pc, mode)
    intervals = (pitches[1]-pitches[0], pitches[2]-pitches[0])
    quality = {(4, 7): '', (3, 7): 'm', (3, 6): 'dim', (4, 8): 'aug'}.get(intervals, '')
    return NOTE_NAMES[pitches[0] % 12] + quality


def arrange(profile: dict, track: Track, *, form: str, key: str, meter: str,
            tempo: int, seed: int) -> dict:
    root, mode, pc = choose_key(profile, key)
    numerator, denominator = validate_meter(meter)
    if not 45 <= tempo <= 210:
        raise ValueError('Tempo must be between 45 and 210 BPM')
    rng = random.Random(seed)
    pattern = rng.choice(PROGRESSIONS)
    sections = []
    bar = 0
    for i, (name, length, energy) in enumerate(FORMS[form]):
        degrees = pattern[0] if 'Chorus' in name or 'Climax' in name else pattern[1]
        if 'Bridge' in name or 'Breakdown' in name or 'Development' in name:
            degrees = (degrees[2:] + degrees[:2])
        chords = [{'bar': bar + b + 1, 'degree': degrees[(b // 2 + i % 2) % len(degrees)],
                   'name': chord_name(degrees[(b // 2 + i % 2) % len(degrees)], pc, mode)}
                  for b in range(length)]
        sections.append({'name': name, 'start_bar': bar+1, 'bars': length,
                         'energy': energy, 'chords': chords})
        bar += length
    return {'schema_version': 1, 'band': profile['name'], 'genre': profile['genre'],
            'song': track.title, 'story': track.description,
            'source_sha256': profile['source_sha256'], 'seed': seed, 'tempo_bpm': tempo,
            'key': f'{root} {mode}', 'root_pc': pc, 'mode': mode,
            'time_signature': meter, 'beats_per_bar': numerator,
            'denominator': denominator, 'form': form, 'total_bars': bar,
            'sections': sections}


def style_prompt(profile: dict, arrangement: dict) -> str:
    style = re.sub(r'\s+', ' ', profile['style']).strip()
    if not style:
        style = f"{profile['genre']}; {profile['ingredients']}. {profile['instruments'][:300]}"
    if len(style) > 620:
        style = style[:620].rsplit(' ', 1)[0].rstrip(',; ') + '.'
    desc = f" Full-length {arrangement['form']} arrangement, {arrangement['tempo_bpm']} BPM, {arrangement['key']}, {arrangement['time_signature']}. Distinct verses, evolving transitions, dynamic choruses, instrumental variation, and a resolved outro."
    return (style + desc).strip()


def suno_sections(arrangement: dict) -> str:
    lines = []
    for section in arrangement['sections']:
        name = section['name']
        energy = section['energy']
        direction = ('sparse atmospheric instrumentation' if energy < .4 else
                     'restrained groove and evolving vocal phrasing' if energy < .65 else
                     'build intensity and rhythmic interplay' if energy < .85 else
                     'full dynamic instrumentation and hook')
        lines.append(f'[{name}: {direction}]')
        lines.append('')
    return '\n'.join(lines).rstrip() + '\n'


def vlq(number: int) -> bytes:
    value = [number & 0x7f]
    number >>= 7
    while number:
        value.insert(0, (number & 0x7f) | 0x80)
        number >>= 7
    return bytes(value)


def meta(kind: int, data: bytes) -> bytes:
    return b'\xff' + bytes([kind]) + vlq(len(data)) + data


def smf_track(events: list[tuple[int, int, bytes]]) -> bytes:
    data = bytearray()
    clock = 0
    for at, priority, payload in sorted(events, key=lambda x: (x[0], x[1])):
        if at < clock:
            raise ValueError('MIDI events must be ordered')
        data += vlq(at - clock) + payload
        clock = at
    data += b'\x00\xff\x2f\x00'
    return b'MTrk' + struct.pack('>I', len(data)) + data


def note(events: list, channel: int, pitch: int, start: int, duration: int, velocity: int) -> None:
    pitch = max(0, min(127, pitch))
    velocity = max(1, min(127, velocity))
    events.append((start, 2, bytes([0x90 | channel, pitch, velocity])))
    events.append((start + max(1, duration), 1, bytes([0x80 | channel, pitch, 0])))


def midi_bytes(arrangement: dict, profile: dict) -> bytes:
    num, den = arrangement['beats_per_bar'], arrangement['denominator']
    bar_ticks = TICKS * 4 * num // den
    root = arrangement['root_pc']
    mode = arrangement['mode']
    rng = random.Random(arrangement['seed'])
    n_tracks = 5
    name, key_mode = arrangement['key'].split()
    signature = KEY_SIGNATURES[key_mode][name]
    tempo_us = 60000000 // arrangement['tempo_bpm']
    meta_events = [(0, 0, meta(0x03, b'Conductor / Chord Markers')),
                   (0, 0, meta(0x51, tempo_us.to_bytes(3, 'big'))),
                   (0, 0, meta(0x58, bytes([num, den.bit_length()-1, 24, 8]))),
                   (0, 0, meta(0x59, struct.pack('bb', signature, int(key_mode == 'minor'))))]
    instr = profile['instruments'].lower() + profile['ingredients'].lower()
    chord_program = 88 if any(x in instr for x in ('synth', 'juno', 'pad', 'ambient')) else 4
    lead_program = 30 if any(x in instr for x in ('guitar', 'djent', 'metal')) else (80 if 'synth' in instr else 73)
    chord_events = [(0, 0, meta(0x03, b'Harmony - editable GM guide')),
                    (0, 0, bytes([0xc0, chord_program]))]
    bass_events = [(0, 0, meta(0x03, b'Bass')),
                   (0, 0, bytes([0xc1, 38 if 'synth' not in instr else 39]))]
    lead_events = [(0, 0, meta(0x03, b'Melody / Vocal guide')),
                   (0, 0, bytes([0xc2, lead_program]))]
    drum_events = [(0, 0, meta(0x03, b'Drums - GM percussion guide'))]
    for section in arrangement['sections']:
        start = (section['start_bar'] - 1) * bar_ticks
        meta_events.append((start, 0, meta(0x06, section['name'].encode('utf-8'))))
        e = section['energy']
        for chord in section['chords']:
            onset = (chord['bar'] - 1) * bar_ticks
            degree = chord['degree']
            tones = chord_notes(degree, root, mode)
            meta_events.append((onset, 0, meta(0x01, chord['name'].encode('utf-8'))))
            for pitch in tones:
                note(chord_events, 0, pitch, onset, bar_ticks - 12, int(42 + 32*e))
            bass_pitch = tones[0] - 24
            note(bass_events, 1, bass_pitch, onset, int(bar_ticks * .66), int(50+30*e))
            if e > .45:
                note(bass_events, 1, bass_pitch + 7, onset + bar_ticks*3//4,
                     max(1, bar_ticks//5), int(38+26*e))
            steps = max(1, bar_ticks // (TICKS//2))
            for ix in range(steps):
                if rng.random() > (.17 + .55*e):
                    continue
                tone = rng.choice(tones) + 12
                t = onset + ix * (TICKS//2)
                if t >= onset + bar_ticks:
                    break
                note(lead_events, 2, tone, t, min(TICKS//2 - 18, onset + bar_ticks - t - 1),
                     int(46+32*e))
            eighth = TICKS//2
            for off in range(0, bar_ticks, eighth):
                if rng.random() < (.18 + .68*e):
                    note(drum_events, 9, 42, onset + off, 60, int(32+30*e))
            if e >= .3:
                for off in range(0, bar_ticks, TICKS):
                    beat = off // TICKS
                    if beat % 2 == 0:
                        note(drum_events, 9, 36, onset+off, 90, int(52+28*e))
                    elif e >= .45:
                        note(drum_events, 9, 38, onset+off, 90, int(48+28*e))
    chunks = [smf_track(t) for t in (meta_events, chord_events, bass_events, lead_events, drum_events)]
    return b'MThd' + struct.pack('>IHHH', 6, 1, n_tracks, TICKS) + b''.join(chunks)


def resolve_profile(band: str, repo: Path) -> Path:
    # Only root-level profile files, never path traversal or arbitrary input.
    path = repo / band
    if path.parent != repo or not path.is_file():
        raise ValueError(f'Band profile not found in repository root: {band}')
    return path


def generate(repo: Path, band: str, output: Path, *, track_index: int = 1,
             catalog: str = 'expansion', title: str | None = None,
             form: str = 'auto', key: str = 'auto', meter: str = '4/4',
             tempo: int | None = None, seed: int = 42, mode: str = 'both') -> list[Path]:
    profile = parse_band(resolve_profile(band, repo))
    tracks = parse_tracks(profile['source'], catalog)
    if not tracks and catalog == 'expansion':
        tracks = parse_tracks(profile['source'], 'ep')
    selected = next((t for t in tracks if t.index == track_index), None)
    if not title and selected is None:
        raise ValueError(f'Track {track_index} not found (catalog={catalog})')
    chosen = Track(track_index, title or selected.title, selected.description if selected else '')
    structure = choose_form(profile, form)
    arrangement = arrange(profile, chosen, form=structure, key=key, meter=meter,
                          tempo=tempo or profile['tempo'], seed=seed)
    folder = output / slugify(profile['name']) / slugify(chosen.title)
    folder.mkdir(parents=True, exist_ok=True)
    arrangement['source_profile'] = band
    arrangement['selected_catalog'] = catalog
    arrangement['suno_url'] = None
    arrangement['approved'] = False
    arrangement['notes'] = ('Generated MIDI is an original deterministic harmonic/rhythmic sketch. '
                            'It does not reproduce Suno audio or encode production effects.')
    writes: list[Path] = []
    data_file = folder / 'arrangement.json'
    data_file.write_text(json.dumps(arrangement, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    writes.append(data_file)
    if mode in ('suno', 'both'):
        for filename, content in [('suno_style.txt', style_prompt(profile, arrangement) + '\n'),
                                  ('suno_sections.txt', suno_sections(arrangement)),
                                  ('song_brief.txt', f"Band: {profile['name']}\nTitle: {chosen.title}\nGenre: {profile['genre']}\nStory: {chosen.description}\n\nInsert original lyrics beneath the section tags in suno_sections.txt. Section tags alone are an instrumental/arrangement scaffold, not finished vocal lyrics.\n")]:
            path = folder / filename
            path.write_text(content, encoding='utf-8')
            writes.append(path)
    if mode in ('midi', 'both'):
        path = folder / 'arrangement.mid'
        path.write_bytes(midi_bytes(arrangement, profile))
        writes.append(path)
    return writes


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--band', required=True, help='Exact root-level Fictional-Bands profile filename')
    parser.add_argument('--repo', type=Path, default=ROOT)
    parser.add_argument('--output', type=Path, default=ROOT / 'generated')
    parser.add_argument('--track', type=int, default=1)
    parser.add_argument('--catalog', choices=['expansion', 'ep'], default='expansion')
    parser.add_argument('--title', help='Optional custom song title')
    parser.add_argument('--form', choices=['auto', *FORMS], default='auto')
    parser.add_argument('--key', default='auto', help='auto or C major, C minor, F# minor, etc.')
    parser.add_argument('--meter', default='4/4')
    parser.add_argument('--tempo', type=int)
    parser.add_argument('--seed', type=int, default=42)
    parser.add_argument('--mode', choices=['suno', 'midi', 'both'], default='both')
    args = parser.parse_args()
    try:
        for path in generate(args.repo.resolve(), args.band, args.output,
                             track_index=args.track, catalog=args.catalog,
                             title=args.title, form=args.form, key=args.key,
                             meter=args.meter, tempo=args.tempo, seed=args.seed, mode=args.mode):
            print(path)
    except (ValueError, OSError) as exc:
        parser.error(str(exc))


if __name__ == '__main__':
    main()
