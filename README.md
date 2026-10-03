# Fictional-Bands

One file per fictional band: the invented genre, its DNA and lore, the band, an EP tracklist, and paste-ready Suno fields.

## Suno fields

Each profile ends its generated sections with two blocks that map onto Suno's custom-mode fields:

| Block | Suno field | Rule |
|---|---|---|
| `Suno Style Prompt` | Style of Music | Strictly under 1,000 characters. No artist names. Describes only what the track should contain. |
| `Exclude Styles` | Exclude Styles | 3 to 6 opposing genres, textures and vocal artifacts. Never contradicts the style prompt. |

[`tools/add_suno_blueprint.py`](tools/add_suno_blueprint.py) maintains both. It moves "Avoid …" sentences out of the style prompt into Exclude Styles (Suno treats every style it is shown as a request), tops the list up from the band's genre families without excluding anything the band uses, and trims any style prompt over the limit at a clause boundary. The [workflow](.github/workflows/add-suno-blueprint.yml) runs it whenever band files change; run it locally with:

```bash
python tools/add_suno_blueprint.py            # add missing sections only
python tools/add_suno_blueprint.py --refresh  # regenerate every section after changing the rules
```

Hand-written items in an Exclude Styles line are kept on `--refresh`; only items from the tool's own vocabulary are regenerated.
