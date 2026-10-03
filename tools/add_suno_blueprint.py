"""Add a Suno "Exclude Styles" negative prompt to every band profile and keep
each "Suno Style Prompt" strictly under Suno's 1,000-character field limit.

"Avoid X, Y and Z." sentences move out of the style prompt into Exclude
Styles: Suno reads every style it is shown as a request, so naming what to
avoid in the style field invites it. The list is then topped up with
opposing genres, textures and vocal artifacts chosen from the band's genre
families. A candidate is never used when the band's own profile mentions
anything it would remove, so a trap band never excludes trap hi-hats.

Usage: python tools/add_suno_blueprint.py [--refresh]
  --refresh  regenerate existing Exclude Styles sections instead of keeping them
"""
from pathlib import Path
import re, sys

ROOT = Path(__file__).resolve().parents[1]
HEADING = "Exclude Styles"
STYLE_LIMIT = 999  # Suno's style field holds 1,000 characters; stay strictly under

# Genre families, detected from the ingredients and the Suno Style Prompt.
FAMILIES = {
    "metal": r"metal|djent|thrash|\bdoom|sludge|grind|deathcore|hardcore|growl|breakdown|shred",
    "rock": r"\brock\b|punk|grunge|shoegaze|post-rock|garage rock|surf|krautrock|britpop|new wave|riffs?\b",
    "electronic": r"techno|\bhouse\b|trance|\bedm\b|electro|synthwave|\bidm\b|dubstep|jungle|drum ?'?n'? ?bass|gabber|hardstyle|\bebm\b|\brave\b|breakbeat|footwork|future bass|bass music",
    "hiphop": r"\brap\b|hip[- ]?hop|\btrap\b|\bdrill\b|grime|boom[- ]bap|turntabl|scratch",
    "jazz": r"jazz|bebop|\bbop\b|\bswing\b|bossa|lounge|big band|saxophone",
    "folk": r"\bfolk|bluegrass|country|americana|celtic|banjo|fiddle|singer[-/ ]?songwriter|hillbilly",
    "ambient": r"ambient|drone|new age|meditative|432 ?hz|relaxing|ethereal|dreamy",
    "orchestral": r"orchestra|cinematic|classical|baroque|chamber|symphonic|opera|choir|choral",
    "pop": r"\bpop\b|k-pop|j-pop|city pop|synthpop|electropop|dance-pop|\bidol",
    "soul": r"\bsoul\b|funk|r&b|gospel|disco|motown|blues|new jack",
    "world": r"highlife|afrobeat|amapiano|cumbia|salsa|zouk|bhangra|tropicalia|dancehall|reggae|\bdub\b|\bska\b|timba|moombahton|raga|flamenco|samba|gnawa|tropical",
    "lofi": r"lo-?fi|chillwave|\bchill\b|cozy|vinyl crackle|cassette",
}

# Opposing genres and textures per family, strongest first.
FOILS = {
    "metal": ["pop rock", "trap hi-hats", "smooth jazz", "acoustic ballad"],
    "rock": ["EDM drops", "trap hi-hats", "smooth jazz", "bubblegum pop"],
    "electronic": ["acoustic folk", "country twang", "acoustic ballad", "smooth jazz"],
    "hiphop": ["country twang", "operatic vocals", "acoustic folk", "power ballad"],
    "jazz": ["EDM drops", "trap hi-hats", "distorted guitar", "four-on-the-floor kick"],
    "folk": ["EDM drops", "trap hi-hats", "dubstep wobble", "synth bass"],
    "ambient": ["trap hi-hats", "EDM drops", "aggressive rap", "busy drum fills"],
    "orchestral": ["trap hi-hats", "EDM drops", "pop punk", "lo-fi hiss"],
    "pop": ["death growls", "lo-fi hiss", "sludge metal", "free jazz"],
    "soul": ["EDM drops", "death growls", "dubstep wobble", "trap hi-hats"],
    "world": ["generic pop EDM", "stadium rock", "dubstep wobble", "trap hi-hats"],
    "lofi": ["EDM drops", "death growls", "stadium rock", "hyperpop"],
}
FALLBACK_FOILS = ["generic pop EDM", "stadium rock", "country twang", "trap hi-hats"]
VOCAL_ARTIFACTS = ["autotune", "chipmunk vocals", "vocal fry"]
PRODUCTION_ARTIFACTS = ["lo-fi hiss", "muddy mix"]

# A candidate is dropped when the band's profile matches its pattern.
CLASHES = {
    "pop rock": r"pop[- ]?rock|power pop|pop[- ]?punk",
    "trap hi-hats": r"\btrap\b|\bdrill\b|phonk|hi-?hat rolls?|rattling hi-?hats",
    "smooth jazz": r"jazz|\bsax|lounge|bossa|\bswing\b",
    "acoustic ballad": r"ballad|acoustic|unplugged",
    "EDM drops": r"\bedm\b|\bdrops?\b|dubstep|brostep|festival|big room|riddim|trance|hardstyle",
    "bubblegum pop": r"bubblegum|\bpop\b|\bidol",
    "acoustic folk": r"\bfolk|acoustic|bluegrass|celtic|americana|banjo|fiddle|singer[-/ ]?songwriter",
    "country twang": r"country|twang|bluegrass|americana|honky|pedal steel|banjo|western|hillbilly|rockabilly",
    "operatic vocals": r"opera|soprano|\baria\b|choir|choral|classical|bel canto|symphonic",
    "power ballad": r"ballad|arena",
    "distorted guitar": r"distort|metal|djent|\brock\b|grunge|punk|shoegaze|fuzz|overdrive|noise|thrash|\bdoom|sludge|riff",
    "four-on-the-floor kick": r"\bhouse\b|techno|disco|four[- ]on[- ]the[- ]floor|\bdance|\bedm\b|trance|garage|hi-?nrg|eurobeat|electro swing|nu rave",
    "dubstep wobble": r"dubstep|wobble|brostep|riddim|bass music|glitch hop|neurofunk|future bass",
    "synth bass": r"synth|808|sub[- ]?bass|reese|electronic|moog|bass music",
    "aggressive rap": r"\brap|hip[- ]?hop|\bdrill\b|grime|\btrap\b|spoken|\bmc\b|toasting",
    "busy drum fills": r"math rock|\bprog|drum ?'?n'? ?bass|jungle|breakcore|fusion|technical|polyrhythm|djent|blast ?beat|footwork|juke",
    "pop punk": r"punk",
    "lo-fi hiss": r"lo-?fi|hiss|tape|vinyl|cassette|crackle|dusty|degraded|bit-?crush|\bvhs\b|warble|flutter",
    "death growls": r"growl|death|metal|grind|hardcore|scream|guttural|harsh vocal|djent",
    "sludge metal": r"sludge|\bdoom|stoner|metal",
    "free jazz": r"jazz|avant|improvis|\bfree\b",
    "generic pop EDM": r"\bpop\b|\bedm\b|dance[- ]pop|electropop",
    "stadium rock": r"stadium|arena|\brock\b|anthem",
    "hyperpop": r"hyperpop|pc music|bubblegum bass|glitchcore|nightcore",
    "autotune": r"auto-?tune|vocoder|pitch[- ]correct|robotic|talk ?box|cyber|android|synthetic voc|vocal chops?|glitch(?:ed)? vocal",
    "chipmunk vocals": r"chipmunk|pitched[- ]up|nightcore|helium|kawaii|hyperpop",
    "vocal fry": r"vocal fry|\bfry\b|whisper|breathy|murmur|asmr|spoken",
    "muddy mix": r"\bmud|murk|sludge|swamp|smear",
}
# Near-synonyms: once one is chosen, the other adds nothing.
OVERLAPS = [{"EDM drops", "generic pop EDM"}, {"acoustic folk", "acoustic ballad"}, {"death growls", "sludge metal"}]
# What an author-written exclusion already covers, so derived items don't repeat it.
COVERS = {
    "trap hi-hats": r"\btrap\b",
    "EDM drops": r"\bedm\b|\bdrops?\b|risers?",
    "generic pop EDM": r"\bedm\b",
    "autotune": r"auto-?tune|pitch[- ]correct",
    "lo-fi hiss": r"lo-?fi|hiss|vinyl",
    "distorted guitar": r"distort|fuzz",
    "stadium rock": r"stadium|arena",
}
DERIVED = set(CLASHES) | {i for pool in FOILS.values() for i in pool} | {"vocals"}
AVOID = re.compile(r"(?:^|(?<=[.!?] ))Avoid\b([^.]*)\.\s*")
INSTRUMENTAL = re.compile(r"instrumental only|\bno vocals\b|without vocals|purely instrumental", re.I)


def heading_line(text, label):
    """The line holding a section heading such as 'Suno Style Prompt' or '### Suno Style Prompt'."""
    return re.search(r"(?m)^(#*\s*)" + re.escape(label) + r"\s*:?\s*$", text)


def style_prompt(text):
    """(start, end, prompt) of the paragraph under the Suno Style Prompt heading."""
    h = heading_line(text, "Suno Style Prompt")
    if not h:
        return None
    m = re.compile(r"\n+([^\n]+)").match(text, h.end())
    return (m.start(1), m.end(1), m.group(1)) if m else None


def profile(text):
    """The band's sonic description: everything before the tracklist, plus the style prompt."""
    cut = re.search(r"(?m)^#*\s*(?:For Fans Of|Fictional Band Name|Fictional EP Tracklist)", text)
    head = text[:cut.start()] if cut else text[:4000]
    sp = style_prompt(text)
    return head + "\n" + (sp[2] if sp else "")


def families(signal):
    scores = {k: len(re.findall(p, signal, re.I)) for k, p in FAMILIES.items()}
    return [k for k in sorted(scores, key=lambda k: -scores[k]) if scores[k] > 0]


def harvest_avoids(prompt):
    """Split 'Avoid ...' sentences out of a style prompt: (prompt without them, items)."""
    items = []
    for m in AVOID.finditer(prompt):
        for part in re.split(r",\s*|\s+and\s+|\s+or\s+", m.group(1)):
            part = re.sub(r"[\"“”]", "", part).strip()
            if part and len(part.split()) <= 5 and part.lower() not in map(str.lower, items):
                items.append(part)
    return AVOID.sub("", prompt).strip(), items


def exclude_styles(text, authored):
    """Comma-separated Exclude Styles: authored items first, then derived ones."""
    sp = style_prompt(text)
    ingredients = re.search(r"(?m)^\**Ingredients:?\**\s*(.+)$", text)
    first_line = text.strip().splitlines()[0] if text.strip() else ""
    signal = " ".join(filter(None, [first_line, ingredients and ingredients.group(1), sp and sp[2]]))
    owned = profile(text)
    chosen = list(authored[:5])
    covered = " ".join(chosen)

    def usable(item):
        if item in chosen or any(item in g and g & set(chosen) for g in OVERLAPS):
            return False
        if re.search(COVERS.get(item, r"\b" + re.escape(item.split()[0])), covered, re.I):
            return False
        pattern = CLASHES.get(item)
        return not (pattern and re.search(pattern, owned, re.I))

    fams = families(signal)
    # Two foils from the primary family and one from the secondary family,
    # topped up from the primary family and then the fallbacks.
    for fam, quota in zip(fams, (2, 1)):
        for item in FOILS[fam]:
            if quota and len(chosen) < 3 and usable(item):
                chosen.append(item)
                quota -= 1
    for item in (FOILS[fams[0]] if fams else []) + FALLBACK_FOILS:
        if len(chosen) < 3 and usable(item):
            chosen.append(item)
    if INSTRUMENTAL.search(sp[2] if sp else ""):
        chosen.append("vocals")
    else:
        chosen += [v for v in VOCAL_ARTIFACTS if usable(v)][:1]
    chosen += [p for p in PRODUCTION_ARTIFACTS if usable(p)][:1]
    return ", ".join(chosen[:6])


def clamp_style(prompt):
    """Cut a style prompt at the last clean clause boundary that fits Suno's field."""
    if len(prompt) <= STYLE_LIMIT:
        return prompt
    cut = prompt[:STYLE_LIMIT - 1]
    for sep, floor in ((". ", 600), (", ", 750), (" ", 0)):
        i = cut.rfind(sep)
        if i > floor:
            cut = cut[:i]
            break
    return cut.rstrip(" ,;:-") + "."


def update(path, refresh):
    text = path.read_text(encoding="utf-8", errors="replace")
    sp = style_prompt(text)
    if not sp:
        return False
    original = text
    start, end, prompt = sp
    prompt, harvested = harvest_avoids(prompt)
    prompt = clamp_style(prompt)
    text = text[:start] + prompt + text[end:]
    end = start + len(prompt)

    existing = re.search(r"\n+#*\s*" + re.escape(HEADING) + r"\s*:?\s*\n+([^\n]*)", text)
    # Keep hand-written exclusions; only items from this tool's vocabulary are regenerated.
    kept = [i.strip() for i in existing.group(1).split(",") if i.strip() not in DERIVED] if existing else []
    authored = [i for i in kept if i] + [a for a in harvested if a.lower() not in map(str.lower, kept)]
    if refresh or harvested or not existing:
        if existing:
            text = text[:existing.start()] + text[existing.end():]
            end = style_prompt(text)[1]
        prefix = heading_line(text, "Suno Style Prompt").group(1)
        section = f"\n\n{prefix}{HEADING}\n{exclude_styles(text, authored)}"
        text = text[:end] + section + text[end:]
    if text != original:
        path.write_text(text, encoding="utf-8")
        return True
    return False


if __name__ == "__main__":
    refresh = "--refresh" in sys.argv[1:]
    changed = 0
    for p in sorted(ROOT.iterdir()):
        if p.is_file() and p.name != "README.md" and not p.name.startswith("."):
            changed += update(p, refresh)
    print(f"Updated {changed} band profiles.")
