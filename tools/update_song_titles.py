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

def category(text):
    low=text.lower()
    scores={k:sum(low.count(w) for w in words.split()) for k,words in CATEGORY_TERMS.items()}
    best=max(scores,key=scores.get)
    return best if scores[best]>0 else "default"

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

def update(path):
    text=path.read_text(encoding="utf-8",errors="replace")
    titles=pick_titles(path,text)
    section=HEADER+"\n"+"\n".join(f"- {t}" for t in titles)
    pat=re.compile(r"\n?"+re.escape(HEADER)+r"\n(?:- .*\n?)+",re.M)
    if pat.search(text): text=pat.sub("\n\n"+section+"\n",text).rstrip()+"\n"
    else: text=text.rstrip()+"\n\n"+section+"\n"
    path.write_text(text,encoding="utf-8")

for p in ROOT.iterdir():
    if p.is_file() and p.name!="README.md" and not p.name.startswith("."):
        update(p)
