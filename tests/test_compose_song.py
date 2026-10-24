import json
import struct
import tempfile
import unittest
from pathlib import Path
from tools.compose_song import (arrange, choose_form, choose_key, generate, midi_bytes,
                                parse_band, parse_tracks, slugify, validate_meter)

PROFILE = '''Weather-Fault
Ingredients: POST-PUNK + NEO / NU SOUL + Tabla

Genre DNA
*   Tempo & Pulse: 90-130 BPM, syncopated grooves.
*   Harmonic Palette: Minor keys and unresolved voicings.

Typical Instruments Used:
Distorted Bass Guitar, Tabla, Analog Synthesizers.

Fictional Band Name: Weather-Fault

Fictional EP Tracklist

Track 1: Grid-Scar Map
- Story & Context: A storm uncovers an old radio frequency.

Track 2: North Point Testament
- Story & Context: The grid has a secret.

Consolidated Brief Summary
Genre: Static Cartography, Sound: rebel soul.

Suno Style Prompt
Static Cartography (Post-punk + neo-soul), distorted bass, tabla, analog synths.

New Song Titles — 2026 Expansion

Track 1: Rain in the Service Alley
- Song Description: A mysterious stranger repairs a transmitter in the rain.

Track 2: Rust on the Timecard
- Song Description: A factory finally closes.
'''

class ComposerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name)
        (self.repo / 'Weather-Fault').write_text(PROFILE, encoding='utf-8')
        self.profile = parse_band(self.repo / 'Weather-Fault')

    def test_extracts_real_profile_sections_and_catalogs(self):
        self.assertEqual(self.profile['tempo'], 110)
        self.assertEqual(self.profile['name'], 'Weather-Fault')
        self.assertIn('Tabla', self.profile['instruments'])
        self.assertIn('distorted bass', self.profile['style'])
        self.assertEqual(parse_tracks(PROFILE, 'expansion')[0].title, 'Rain in the Service Alley')
        self.assertEqual(parse_tracks(PROFILE, 'ep')[1].description, 'The grid has a secret.')

    def test_forms_are_complete_and_chords_remain_in_key(self):
        track = parse_tracks(PROFILE, 'expansion')[0]
        result = arrange(self.profile, track, form=choose_form(self.profile, 'auto'),
                         key='auto', meter='7/8', tempo=110, seed=9)
        self.assertEqual(result['key'], 'C minor')
        self.assertEqual(result['form'], 'rnb')
        self.assertEqual(result['time_signature'], '7/8')
        self.assertEqual(sum(s['bars'] for s in result['sections']), result['total_bars'])
        self.assertTrue(all(s['chords'] for s in result['sections']))
        self.assertTrue(any('Chorus' in s['name'] for s in result['sections']))
        self.assertEqual(len(result['sections'][0]['chords']), result['sections'][0]['bars'])

    def test_midi_is_type_1_with_five_tracks_and_valid_chunk_lengths(self):
        track = parse_tracks(PROFILE, 'expansion')[0]
        arr = arrange(self.profile, track, form='lofi', key='C major', meter='4/4', tempo=95, seed=4)
        mid = midi_bytes(arr, self.profile)
        self.assertEqual(mid[:4], b'MThd')
        self.assertEqual(struct.unpack('>IHHH', mid[4:14]), (6, 1, 5, 480))
        cursor = 14
        for _ in range(5):
            self.assertEqual(mid[cursor:cursor+4], b'MTrk')
            n = struct.unpack('>I', mid[cursor+4:cursor+8])[0]
            self.assertGreater(n, 5)
            self.assertEqual(mid[cursor+8+n-4:cursor+8+n], b'\x00\xff\x2f\x00')
            cursor += 8+n
        self.assertEqual(cursor, len(mid))
        self.assertIn(b'\xff\x58\x04\x04\x02', mid)
        self.assertIn(b'\xff\x51\x03', mid)
        self.assertIn(b'\x99\x24', mid)
        self.assertEqual(midi_bytes(arr, self.profile), mid)

    def test_generated_files_and_seed_determinism(self):
        output = self.repo / 'generated'
        files = generate(self.repo, 'Weather-Fault', output, seed=12)
        self.assertEqual(len(files), 5)
        self.assertTrue(all(p.exists() for p in files))
        dest = output / 'weather-fault' / 'rain-in-the-service-alley'
        metadata = json.loads((dest / 'arrangement.json').read_text())
        self.assertEqual(metadata['seed'], 12)
        self.assertEqual(metadata['source_profile'], 'Weather-Fault')
        self.assertIsNone(metadata['suno_url'])
        self.assertIn('[Intro:', (dest / 'suno_sections.txt').read_text())
        first = (dest / 'arrangement.mid').read_bytes()
        generate(self.repo, 'Weather-Fault', output, seed=12)
        self.assertEqual(first, (dest / 'arrangement.mid').read_bytes())
        generate(self.repo, 'Weather-Fault', output, seed=13)
        self.assertNotEqual(first, (dest / 'arrangement.mid').read_bytes())
        self.assertEqual((self.repo / 'Weather-Fault').read_text(), PROFILE)

    def test_input_validation_and_suno_only(self):
        self.assertEqual(slugify('Kōribana & Ice'), 'koribana-ice')
        self.assertEqual(choose_key(self.profile, 'Bb major')[2], 10)
        self.assertEqual(validate_meter('5/4'), (5, 4))
        with self.assertRaises(ValueError):
            validate_meter('0/4')
        with self.assertRaises(ValueError):
            choose_key(self.profile, 'H major')
        with self.assertRaises(ValueError):
            generate(self.repo, '../README.md', self.repo / 'out')
        with self.assertRaises(ValueError):
            generate(self.repo, 'Weather-Fault', self.repo / 'out', track_index=999)
        files = generate(self.repo, 'Weather-Fault', self.repo / 'other', mode='suno')
        self.assertFalse(any(p.suffix == '.mid' for p in files))

if __name__ == '__main__':
    unittest.main()
