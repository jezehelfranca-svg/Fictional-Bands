# Fictional-Bands → Suno / MIDI Production

## Design

The catalog's written genre DNA is the authoritative creative brief. `tools/compose_song.py` extracts each band's identity, genre, tempo, harmonic characteristics, instruments, Suno style, and selected song concept. It creates a complete, reproducible song form instead of a four-bar loop.

This first version is **rule-based**, not an AI music model; it makes no external requests. Suno remains the audio generation and production engine.

## Suno-first (recommended)

1. Run `python tools/compose_song.py --band "Umbral Orchestra" --catalog ep --track 1 --mode suno`.
2. Paste `suno_style.txt` into Suno's Style field.
3. Paste `suno_sections.txt` into Suno's Lyrics field. Write or paste **actual lyrics** under verse/chorus tags; generated tags are only an arrangement scaffold. For an instrumental track, use Suno's instrumental workflow and section cues as guides.
4. Generate alternatives in Suno, compare versions, and approve one. If keeping a release archive, record the approved Suno URL and approval state in the generated `arrangement.json`.
5. Keep finished audio/stems outside Git unless explicitly making a release archive. There is no Suno API, account access, or Inspire integration.

## MIDI-guided (optional)

```bash
python tools/compose_song.py --band "Ablation Cycle" --track 1 --mode both \
  --form progressive --key "C minor" --meter 7/8 --tempo 126 --seed 2026
```

Import `arrangement.mid` into a MIDI-compatible DAW. The conductor track contains tempo, time signature, key signature, section markers, and chord-name text. Four instrument tracks provide editable GM harmony, bass, melodic guide, and drum parts. Assign the band's actual instruments, then refine voicing, rhythms, effects, and arrangement.

MIDI may also serve as a guide in Suno Studio where supported, subject to plan/version and import behavior. This repository does not claim Suno will reproduce each note exactly.

**Limitations:** These are deterministic sketches built with diatonic chord templates, monophonic melody, elementary bass and GM percussion. They do not render VSTs, authentic tabla, vocals, advanced modal harmony, variable tempo, production effects, or Suno audio.

## Controls

- `--key auto` uses C minor if the band's harmonic description mentions minor, else C major. Explicit keys such as `Bb major` and `F# minor` override it.
- `--form auto` selects from genre keywords; alternatives are `pop`, `lofi`, `cinematic`, `progressive`, and `rnb`.
- `--seed` controls reproducible variations. Each project records its source SHA-256.
- `--catalog expansion` selects new track concepts and falls back to EP tracks; `--catalog ep` selects original EP songs.
- Only root-level profile filenames are accepted. Profiles remain unchanged.

## Batch drafting

```bash
for track in 1 2 3 4 5 6; do
  python tools/compose_song.py --band "Weather-Fault" --track "$track" --mode suno
done
```

You can scale this across the band catalog, but it generates structured prompt/arrangement assets, **not 900 finished Suno recordings**.
