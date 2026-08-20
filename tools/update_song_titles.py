from pathlib import Path
import hashlib,re

ROOT=Path(__file__).resolve().parents[1]
HEADER="New Song Titles — 2026 Expansion"

BANKS={
"water":["Salt on the Stairwell","The Tide Took the Long Way Home","Low Water at Closing Time","Mooring Rope in the Rain","Where the Hull Starts Singing","Brine Under the Door","The Harbor Kept One Light On","Silt in the Wedding Shoes","Last Ferry Before the Weather","A Cup Left Warm by the Quay"],
"industrial":["Shift Change at the Furnace","Grease Under Sunday Nails","The Gantry After Everyone Left","Steel Dust in the Coat Pocket","Lunch Break Beneath the Crane","When the Bearings Go Quiet","The Foreman’s Empty Thermos","Rust on the Timecard","Night Shift Through Bay Three","A Warm Handrail in Winter"],
"botanical":["Glasshouse at First Rain","Roots Beneath the Kitchen Tile","The Orchid Leaned Toward the Door","Pollen on a Black Sleeve","Green Light Through the Conservatory","After the Last Watering","A Fern Growing Through Concrete","Seed Packet in the Coat Pocket","The Garden Outlived the Argument","Sap on the Window Latch"],
"space":["Apogee Without Witnesses","Orbit Keeps the Scar","The Last Warm Room Before Vacuum","Antenna Dust at Perihelion","Gravity in the Coat Pocket","The Moon Missed Our Exit","Two Cups at the Observation Deck","Constellation Behind the Blinds","Someone Left the Airlock Light On","Return Burn for an Empty Seat"],
"ice":["The Last Warm Room","Thaw Line Confession","Gloves Drying by the Radiator","Blue Ice Under the Floorboards","When the Freezer Door Stayed Open","Meltwater in the Boot Tray","A Match Struck Below Zero","Frost on the Inside Glass","The Heater Failed at Dawn","Warm Breath on a Frozen Key"],
"rail":["Platform After Closing","Sleeper Car Weather","The 3:17 Never Called Our Names","Coffee Before the Last Train","Your Coat on Seat Twelve","Signalman’s Kitchen Light","Rain Between Two Platforms","The Ticket Stayed in My Pocket","End of the Line, Still Warm","A Window Facing the Wrong Direction"],
"textile":["Loose Thread Gospel","Hemline Under Load","Needle Left in the Cushion","Your Sleeve on the Banister","Stitches in the Morning Light","The Seam Gave Way at Dinner","Thread Count for Two Empty Beds","A Button Found Under the Piano","The Loom Kept Turning","Pins in a Porcelain Dish"],
"electrical":["After the Breaker Opens","Copper Under the Tongue","The Substation at Supper Time","One Lamp Left on in Bay Four","Current Through a Wedding Ring","The Relay Clicked Twice","Insulation Dust on Your Cuff","When the Busbar Cooled","A Fuse Wrapped in Brown Paper","Grounded Before the Rain"],
"film":["Reel Burn at Closing Time","The Projection Booth Stayed Warm","One Frame Before the Kiss","Ticket Stub in the Ashtray","Dust Across the Silver Screen","The Usher Locked the Side Door","Film Grain on Your Collar","House Lights After Midnight","The Scene We Never Reshot","A Torn Poster in the Lobby"],
"circus":["Rigging After the Vows","Sawdust in the Bridal Shoes","The Trapeze Kept Swinging","Backstage After the Last Bow","A Red Ribbon on the Scaffold","The Ringmaster Ate Alone","Canvas Roof in Heavy Rain","The Clown Washed Off the Paint","One Chair Beneath the High Wire","The Calliope After Closing"],
"desert":["Heatline Survey","Water Bottle Under the Seat","No Shade Past Kilometer Nine","Dust in the Lunch Tin","The Road Bent in the Heat","A Motel Key Full of Sand","Sunburn Through a Work Shirt","Wind Against the Tin Roof","The Well Was Deeper Than Memory","Last Bus Across the Salt Flat"],
"clock":["Escapement at 3:17","The Second Hand Hesitated","Mainspring on the Kitchen Table","We Missed an Hour Together","The Clockmaker’s Cold Tea","One Gear Beneath the Floorboard","Pendulum Through the Thin Wall","The Watch Stopped at Breakfast","Timecard with No Punch Out","A Minute Left in the Drawer"],
"default":["Kitchen Light After Midnight","The Coat You Left on My Chair","Rain in the Service Alley","Sunday Morning Through Thin Curtains","A Key Warm from Your Pocket","The Room After Everyone Leaves","Coffee Cooling Beside the Window","Three Blocks Past the Last Goodbye","Your Name on the Back of a Receipt","The Door That Wouldn’t Quite Close","Laundry Turning in the Next Room","One Streetlamp Before Home"]}

CATEGORY_TERMS={
"water":"water tide salt brine harbor harbour hull dock ocean sea silt sump dredge keel berth hydro aquatic aqueous ferry vessel mooring",
"industrial":"steel iron rust gantry furnace factory piston gear bearing freight crane shaft ore weld mechanical metal",
"botanical":"plant root xylem phloem leaf chlorophyll greenhouse garden germination seed orchid stomata tree fungal mycelium",
"space":"orbit orbital star stellar moon apogee perigee ionosphere gravity vacuum cosmic zenith parallax parsec hadron particle",
"ice":"ice icy frost frozen permafrost glacier glacial cryo krio krios cold thaw sub-zero svalbard hibern",
"rail":"rail train transit platform sleeper commuter station signal switchman carriage terminal",
"textile":"thread stitch seam loom needle fabric vellum knit hem lace weave tailor garment",
"electrical":"circuit voltage current cable wire relay breaker conductor cathode solder signal substation busbar electric",
"film":"film nitrate projection cinema screen reel drive-in polaroid frame aperture glazier glass",
"circus":"circus trapeze ringmaster aerialist roustabout calliope high-wire carnival rigging scaffold",
"desert":"arid desert sand drought heat haze sun-sick salt flat dry",
"clock":"clock pendulum escapement mainspring time gear sprocket calibration chronos ticking"
}

SCENES={
"water":[
"At the end of a storm shift, two people carry salvaged belongings up a stairwell while the water rises one landing at a time. The song follows the small decisions that reveal who they are willing to save, ending with a single household object floating back toward them after they believed everything had been lost.",
"A harbor worker keeps an unofficial lamp burning for boats returning after curfew, even after being ordered to shut the quay down. One night the light guides back someone the neighborhood had already mourned, turning an ordinary act of disobedience into a communal ritual.",
"A couple preparing to leave a flooded district argues over what can fit into one bag: documents, photographs, tools, or a child’s broken instrument. The chorus grows from the objects they abandon, while the final scene focuses on what they carry by hand instead of what they own.",
"After the tide exposes a street that has been underwater for years, former residents walk its mud-covered length and recognize homes only by railings, tiles and rust stains. The song moves from archaeology toward reunion as remembered addresses become living voices again."
],
"industrial":[
"During the last night before a factory closes, a veteran worker shows a younger replacement how to listen for faults by touch rather than by gauge. Their conversation becomes an inheritance story about pride, exhaustion and the knowledge that disappears when a machine is finally switched off.",
"A night-shift mechanic finds a coworker’s forgotten thermos beside a machine that has not run since an accident. Instead of treating it as a memorial, the crew cleans the bay, finishes the abandoned repair and lets the first successful start-up become the emotional climax.",
"Two estranged siblings meet during shift change to empty their father’s locker after his retirement. Grease, folded gloves, handwritten measurements and an old lunch tin expose a version of him neither understood at home, forcing them to reconsider the silence they grew up with.",
"A worker facing redundancy spends one final lunch break beneath the crane where an entire adult life has been measured in whistles and overtime. The song resolves not with heroic escape but with the worker taking one small tool home and finally admitting fear about starting again."
],
"botanical":[
"After inheriting a neglected greenhouse, two siblings disagree over whether to sell the property or restore it. Each plant becomes evidence of their family’s habits and grudges, and the first new leaf after a night of rain quietly changes the decision.",
"A tenant discovers roots breaking through a kitchen tile in an apartment scheduled for demolition. Rather than removing them, the residents trace where the roots came from and uncover a hidden courtyard, turning the song into a story about stubborn life inside planned erasure.",
"A gardener finishing a final watering before leaving town notices that one difficult plant has finally leaned toward the doorway. The image becomes a restrained farewell about care that works slowly and often becomes visible only when someone is about to leave.",
"Two people who stopped speaking continue tending opposite halves of the same community garden. Seasons force them into indirect cooperation until a storm destroys the fence between their plots, making reconciliation physical before either person can name it."
],
"space":[
"Two technicians on an isolated observation station share the last warm drink before one begins a dangerous exterior repair. The vast setting stays subordinate to human detail: condensation on glass, a glove clasp, an unfinished sentence and the empty chair that remains during the return burn.",
"A crew member records ordinary domestic sounds to play during long orbital nights: cutlery, rain, a hallway door and someone laughing in another room. When communications fail, those recordings stop being nostalgia and become the only proof of a life waiting beyond the window.",
"After a navigation fault forces a vessel to miss its planned return window, two people calculate dwindling margins while refusing to discuss the person who should have occupied an empty seat. The eventual correction burn becomes less about engineering victory than finally acknowledging the absence.",
"At perihelion, maintenance dust glows like a false constellation across an observation deck. A character who has spent years studying distant objects realizes the most important pattern is made from fingerprints, coffee rings and marks left by the people living beside them."
],
"ice":[
"When the heater fails before dawn, several people in a remote station move into one room and begin trading practical tasks instead of complaints. The story turns on shared gloves, thawing pipes and one match protected between cupped hands, allowing warmth to become a social act rather than a metaphor.",
"A field worker discovers meltwater where permanent ice should be and must report evidence that will end a season’s work early. The song follows the conflict between professional certainty and personal attachment to the place, resolving when the team packs without pretending the change is temporary.",
"Two people separated by an argument are forced to repair a frozen door together while a storm seals the building from outside. Short, physical instructions gradually replace accusation, and the first opening of the latch becomes the understated release.",
"A traveler finds a familiar key frozen inside a coat inherited from someone who died years earlier. The attempt to identify the lock leads through abandoned rooms and stored boxes until the key finally opens something mundane but emotionally exact."
],
"rail":[
"After the final train, two station workers discover a coat left on an otherwise empty platform. Searching its pockets for identification leads them through ticket stubs, receipts and a handwritten address, and the night becomes a quiet effort to return one object before morning.",
"A commuter repeatedly sees the same stranger drinking coffee before the first train but never speaks. On the day the stranger fails to appear, the routine suddenly reveals how much anonymous people can structure one another’s lives.",
"Two former partners unexpectedly share a sleeper compartment during a weather delay. The train keeps moving while their conversation stalls, forcing the song to use passing stations, blankets, corridor light and unslept hours as the chronology of what they can finally say.",
"A signal worker preparing for retirement leaves the kitchen light on at a remote cabin so a younger colleague can find the path during heavy rain. The gesture becomes the last handover between generations, with no speech needed once the incoming footsteps are heard."
],
"textile":[
"A tailor repairs a wedding garment for someone whose ceremony may not happen. Every removed stitch reveals a previous alteration, turning the workbench into a record of changing bodies, expectations and promises rather than a symbol of perfect romance.",
"Two people clearing their mother’s room find an unfinished piece still attached to the loom. They disagree over whether to preserve it untouched or complete it, and the final section lets the continuing rhythm of the loom become their first shared decision.",
"A loose button discovered beneath a piano brings back the exact morning a family argument fractured the household. The song reconstructs that scene through fabric, furniture and unfinished chores until the narrator chooses to sew the button onto something new instead of preserving it as evidence.",
"A garment worker hides a small personal repair among an exhausting line of identical orders. The secret stitches become a private signature, and the climax comes when another worker recognizes them and answers with a matching mark."
],
"electrical":[
"A maintenance crew loses power during a storm and must trace the fault through a dark facility using hand lamps and remembered routes. The emotional story centers on an experienced technician trusting a younger colleague’s judgment for the first time when the expected fault location proves wrong.",
"After a breaker opens during an important family gathering nearby, one character leaves dinner to restore service. The repair unfolds alongside missed calls and cooling food, ending with the lights returning before the character does and exposing the cost of always being the reliable one.",
"Two workers find a wedding ring beside a busbar during shutdown inspection. Their effort to identify its owner spreads through the crew and gradually uncovers a relationship that had been kept private for years, turning technical isolation into collective recognition.",
"A relay that clicks twice every night becomes the only irregularity in an otherwise perfect system. Following it leads a technician not to a dangerous failure but to a forgotten lamp and a person secretly using the space after hours, shifting the song from suspicion toward human understanding."
],
"film":[
"On the final night of an old cinema, the projectionist discovers one damaged reel that has been repaired by hand dozens of times. Screening it for an almost empty room becomes a story about imperfect preservation, with burns and missing frames treated as evidence of people rather than defects.",
"Two former lovers return separately to the same repertory screening and recognize each other only when the house lights rise. The song avoids reunion fantasy and instead follows the awkward walk through the lobby, where old ticket stubs and torn posters make memory more vivid than conversation.",
"An usher cleaning after midnight finds a handwritten note trapped behind a seat. Trying to return it leads through the cinema’s staff rooms and neighborhood history, ending when the note reaches someone who no longer remembers writing it but remembers the person it was meant for.",
"A filmmaker refuses to reshoot one technically flawed scene because it contains the final unscripted appearance of a friend. The song turns focus pulls, scratches and room tone into emotional evidence, asking what fidelity means when perfection would erase the truth."
],
"circus":[
"After a wedding held beneath a damaged big top, the newly joined families wake to find the rigging still moving in heavy rain. Repairing it together becomes the first test of whether the marriage joined anything beyond two people, with old rivalries expressed through knots, ladders and who trusts whom above the floor.",
"An aerialist returns after closing to retrieve one red ribbon left on the scaffold. A younger performer follows and learns that the ribbon marks every place someone fell and stood up again, turning inherited superstition into a practical archive of survival.",
"The ringmaster eats alone after announcing the circus will not travel next season. One by one the performers enter carrying ordinary leftovers rather than costumes, and the farewell becomes domestic, awkward and more moving than the final show.",
"A clown removes stage paint while hearing the dismantling crew outside. The mirror scene gradually reveals a performer unsure which expression belongs offstage, until another worker knocks and asks for help folding canvas, giving the song a concrete way back into community."
],
"desert":[
"A survey crew crosses an exposed road after their vehicle loses cooling, rationing water while a distant structure keeps appearing closer than it is. The story emphasizes professional competence under fatigue, and the climax comes when one character admits the route calculation was wrong before pride becomes dangerous.",
"At a roadside motel, a traveler finds sand inside a key envelope from a room occupied years earlier. The search for why it was kept turns into a restrained account of a failed departure, with heat, vending-machine light and a parked car carrying more meaning than confession.",
"Two workers share the last patch of shade during a midday shutdown and discover they have received the same layoff notice. Their conversation moves from practical anger to competing plans for home, making the empty road beyond kilometer nine feel like a real choice rather than a metaphor.",
"A maintenance driver carries an unopened water bottle under the passenger seat because it belonged to someone who used to ride the route. When another stranded traveler needs it, giving the bottle away becomes the song’s decisive act of release."
],
"clock":[
"A clockmaker repairing a stopped watch discovers it halted at the exact minute recorded in an old family story. The repair becomes an argument over whether restoring function destroys meaning, ending when the owner chooses to let the mechanism run while keeping the worn dial unchanged.",
"Two people sorting an estate hear a pendulum through a thin wall long after every visible clock has been packed. Finding the hidden mechanism exposes a room neither knew existed and forces them to confront how much of a life can remain structurally present but personally unknown.",
"A factory timecard with no punch-out becomes the only trace of a worker who disappeared decades earlier. The song follows a descendant through records, lunchroom stories and mechanical archives until the missing ending is replaced by several contradictory human memories rather than one clean answer.",
"During breakfast, a watch stops and one character becomes convinced it is an omen. The other quietly opens the case, finds an ordinary mechanical fault and repairs it, but the conversation reveals the real fear was never about the watch."
],
"default":[
"A person returns to an apartment after midnight to collect the last few belongings and finds the kitchen light still on. Ordinary objects—a receipt, cooling coffee, laundry turning in the next room—reconstruct the relationship more accurately than a dramatic confrontation would, ending with one deliberate object left behind.",
"Two people who have avoided each other for months meet in a service alley during sudden rain. Forced beneath the same narrow awning, they speak first about practical things and only later about the unfinished event between them, letting weather and physical distance measure the thaw.",
"A coat left on a chair becomes the center of a household waiting for someone delayed far beyond expectation. Different family members move it, wear it and nearly put it away, while the final scene reveals what returning home now means after the waiting has changed everyone.",
"On a quiet Sunday, one character performs ordinary chores after making a difficult decision the night before. Thin curtains, a warm key, a half-closed door and slowly cooling coffee make the emotional turn visible without explanatory monologues."
]
}

CATEGORY_TERMS={k:v for k,v in CATEGORY_TERMS.items()}

def category(text):
    low=text.lower()
    scores={k:sum(low.count(w) for w in words.split()) for k,words in CATEGORY_TERMS.items()}
    best=max(scores,key=scores.get)
    return best if scores[best]>0 else "default"

def field(text,label,fallback):
    m=re.search(r"^"+re.escape(label)+r":\s*(.+)$",text,re.M|re.I)
    return m.group(1).strip() if m else fallback

def genre_name(text):
    for line in text.splitlines():
        s=line.strip()
        if s and not s.startswith("#"):
            return s
    return "the band’s established fusion"

def pick_titles(path,text,n=6):
    cat=category(text)
    pool=BANKS[cat]+BANKS["default"]
    seed=int(hashlib.sha256((path.name+"|"+text[:500]).encode("utf-8","ignore")).hexdigest(),16)
    start=seed%len(pool)
    step=7 if len(pool)%7 else 5
    chosen=[]
    i=0
    while len(chosen)<n and i<len(pool)*2:
        t=pool[(start+i*step)%len(pool)]
        if t not in chosen and t.lower() not in text.lower(): chosen.append(t)
        i+=1
    return chosen

def existing_titles(text):
    m=re.search(r"\n?"+re.escape(HEADER)+r"\n(?P<body>.*)$",text,re.S)
    if not m:return []
    return re.findall(r"(?m)^- ([^\n]+?)(?=\n- Song Description:|\n- [^\n]+$|\Z)",m.group("body"))

def description(path,text,title,index):
    cat=category(text)
    scenes=SCENES.get(cat,SCENES["default"])
    seed=int(hashlib.sha256((path.name+"|"+title).encode("utf-8","ignore")).hexdigest(),16)
    scene=scenes[seed%len(scenes)]
    genre=genre_name(text)
    instruments=field(text,"Central Instruments","the band’s defining instruments")
    mood=field(text,"Mood","the established emotional tension")
    coda=(
        f" Musically, {genre} should shape the scene through {instruments}, with the arrangement moving from concrete environmental detail toward a decisive final image. "
        f"Keep the emotional register grounded in {mood.lower().rstrip('.')} rather than abstract declarations; each verse must change the situation, and the chorus should turn a physical detail from the title into the song’s central memory."
    )
    return scene+coda

def section_for(path,text,titles):
    out=[HEADER,""]
    for i,title in enumerate(titles,1):
        out.append(f"Track {i}: {title}")
        out.append(f"- Song Description: {description(path,text,title,i)}")
        out.append("")
    return "\n".join(out).rstrip()+"\n"

def update(path):
    text=path.read_text(encoding="utf-8",errors="replace")
    titles=existing_titles(text)
    if not titles:
        titles=pick_titles(path,text)
    titles=titles[:6]
    section=section_for(path,text,titles)
    pat=re.compile(r"\n?"+re.escape(HEADER)+r"\n.*$",re.S)
    if pat.search(text):
        text=pat.sub("\n\n"+section,text).rstrip()+"\n"
    else:
        text=text.rstrip()+"\n\n"+section
    path.write_text(text,encoding="utf-8")

for p in ROOT.iterdir():
    if p.is_file() and p.name!="README.md" and not p.name.startswith("."):
        update(p)
