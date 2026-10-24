# Fictional-Bands

A fictional artist and genre-DNA catalog with a **Suno-first composition workflow**. Every original band profile remains the source of truth; no profile migrations or Suno account credentials are required.

## Generate a full-song Suno arrangement

Requires Python 3.10+ and no third-party packages.

```bash
python tools/compose_song.py --band "Ablation Cycle" --track 1 --mode suno
```

Output under `generated/ablation-cycle/<song>/`:

- `suno_style.txt` — existing band Suno style combined with full-song tempo, key, meter, and arrangement guidance.
- `suno_sections.txt` — structurally differentiated section tags for Suno's lyrics field. **Add your own sung lyrics beneath the tags**; generated tags are not finished vocal lyrics.
- `song_brief.txt` — source concept and instructions.
- `arrangement.json` — reproducible sections, bar counts, chord labels, provenance, seed, and fields for tracking an approved Suno generation.

For an editable five-track MIDI **composition sketch** alongside Suno files:

```bash
python tools/compose_song.py --band "Weather-Fault" --track 1 --mode both --key "C major" --tempo 108 --form rnb --seed 9
```

MIDI is a standard Type 1 file with a conductor/chord-marker track plus GM harmony, bass, melodic guide, and drum tracks. Import it into compatible DAWs or MIDI-compatible production workflows. **It is generated locally from deterministic harmonic/rhythm templates, not extracted from Suno or Google Flow.** MIDI does not encode real VST instruments, custom tabla samples, acoustic production, or finished vocals.

Use `--catalog ep` for the original EP instead of the expansion; `--track N` selects the song. `--form auto|pop|lofi|cinematic|progressive|rnb` chooses an arrangement; `--key auto` follows the band's documented harmonic mode (C major or C minor), and explicit keys override it. `--meter 4/4|5/4|7/8` sets time signature; `--seed` controls reproducible variation.

See [docs/COMPOSITION_WORKFLOW.md](docs/COMPOSITION_WORKFLOW.md) for DAW, Suno, and batch usage.

## Testing

```bash
python -m unittest discover -s tests -v
```

The existing `tools/update_song_titles.py` workflow remains separate and unchanged. Compositions are created only by explicitly running the new command. Generated outputs are gitignored until you choose to archive approved releases.
