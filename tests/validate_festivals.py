"""Targeted static audit for the three native Frosthavn festivals."""
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "ContentPack"
patches = json.loads((PACK / "content.json").read_text())["Changes"]
def require(value, message):
    if not value:
        raise AssertionError(message)

by_target = {}
for patch in patches:
    by_target.setdefault(patch.get("Target"), []).append(patch)

dates = {}
for patch in by_target["Data/Festivals/FestivalDates"]:
    dates.update(patch.get("Entries", {}))
expected = {
    "spring9": ("spring", "ArcticPassage_Harbor", "900 1800"),
    "summer18": ("summer", "ArcticPassage_Icefjord", "1800 2600"),
    "winter21": ("winter", "ArcticPassage_Town", "1800 2600"),
}
vanilla = {"spring13", "spring24", "summer11", "summer28", "fall16", "fall27", "winter8", "winter25",
           "spring15", "spring16", "spring17", "summer20", "summer21", "winter12", "winter13",
           "winter15", "winter16", "winter17"}
require(set(expected).issubset(dates), "Missing one of the three festival dates")
require(not (set(expected) & vanilla), "Festival date overlaps a standard active festival")

character_ids = set()
for patch in by_target.get("Data/Characters", []):
    character_ids.update(patch.get("Entries", {}))
items = {}
for patch in by_target.get("Data/BigCraftables", []):
    items.update(patch.get("Entries", {}))
runtime_path = ROOT / "Code/ArcticPassage/FestivalRuntime.cs"
runtime = runtime_path.read_text()
phenomena = (ROOT / "Code/ArcticPassage/PolarPhenomena.cs").read_text()
lighting = (ROOT / "Code/ArcticPassage/NightLighting.cs").read_text()
for date, (season, location, hours) in expected.items():
    loaders = [p for p in by_target.get("Data/Festivals/" + date, []) if p.get("Action") == "Load"]
    require(len(loaders) == 1, f"{date}: expected exactly one native festival data loader")
    data_path = PACK / loaders[0]["FromFile"]
    event = json.loads(data_path.read_text())
    require(event["conditions"] == location + "/" + hours, f"{date}: festival location/time mismatch")
    require("set-up_y1" in event and "set-up_y2" in event, f"{date}: missing recurring setup variants")
    for year in ("y1", "y2"):
        script = event["set-up_" + year]
        require("changeToTemporaryMap " + location in script, f"{date}: wrong temporary map")
        actors = event["Set-Up_additionalCharacters_" + year].split("/")
        require(len(actors) == 6, f"{date}: expected six resident placements")
        tilemap = ET.parse(PACK / "assets/maps" / f"{location.removeprefix('ArcticPassage_')}_{season}.tmx").getroot()
        width = int(tilemap.get("width"))
        properties = {}
        for tileset in tilemap.findall("tileset"):
            first_gid = int(tileset.get("firstgid"))
            for tile in tileset.findall("tile"):
                properties[first_gid + int(tile.get("id"))] = {
                    prop.get("name"): prop.get("value") for prop in tile.findall("./properties/property")
                }
        layers = {layer.get("name"): [int(value.strip()) for value in layer.find("data").text.strip().split(",")]
                  for layer in tilemap.findall("layer")}
        for actor in actors:
            name, x, y, facing = actor.split()
            x, y = int(x), int(y)
            index = y * width + x
            back, solid = layers["Back"][index], layers["Buildings"][index]
            walkable = back > 0 and "Passable" not in properties.get(back, {}) and (
                not solid or "Passable" in properties.get(solid, {})
            )
            require(name in character_ids, f"{date}: missing resident data for {name}")
            require(walkable, f"{date}: resident {name} spawns on a blocked tile {x},{y}")
            require(f"{name}" in event, f"{date}: missing local festival dialogue for {name}")
        require("startedMessage" in event and "locationDisplayName" in event, f"{date}: missing festival notice")
        require(all(npc in event for npc in [a.split()[0] for a in actors]), f"{date}: missing resident dialogue")

    item_id = {
        "spring": "ArcticPassage_HarborKnot",
        "summer": "ArcticPassage_MidnightSunDisplay",
        "winter": "ArcticPassage_WinterLantern",
    }[season]
    require(item_id in items and items[item_id]["CanBePlacedIndoors"], f"{date}: missing placeable annual keepsake")
    image_path = PACK / "assets/items" / {
        "spring": "harbor-knot.png", "summer": "midnight-sun-display.png", "winter": "winter-lantern.png"
    }[season]
    require(Image.open(image_path).size == (16, 32), f"{date}: keepsake atlas has wrong dimensions")

for required in [
    'e.Button != SButton.F', 'nameof(Event.caughtFish)', 'nameof(Event.canPlayerUseTool)',
    'Key("spring", "fishCatch", Game1.year)', 'ref string __6',
    'Game1.player.Money < price', 'Game1.player.Money -= price',
    'Key(festival, "reward", Game1.year)', 'Game1.player.addItemByMenuIfNecessaryElseHoldUp(item)',
    'new Response("shore"', 'WarmTown()', 'Key("winter", "friendship", Game1.year)',
]:
    require(required in runtime, f"Festival runtime is missing required player-facing behavior: {required}")
require('private static void ChallengeCatch(Event __instance' in runtime
        and 'Game1.player.stats.Get("FishCaught")' not in runtime,
        "Festival fishing must use its native event callback, not a lifetime counter the engine never increments here")
require('Game1.activeClickableMenu is ItemGrabMenu' in runtime
        and 'Game1.addHUDMessage(new HUDMessage(T(boughtKey)' in runtime,
        "Paid meals must retain their native full-inventory item menu")
require('FestivalRuntime.CurrentFestival() == "winter"' in phenomena,
        "Clear winter festival aurora condition is missing")
require('"winter" => "ArcticPassage_Town"' in lighting and 'FestivalForEvent(location.currentEvent)' in lighting and '0, location.Name);' in lighting,
        "Winter festival does not inherit the town lightmap sources")

for lang in ("default", "zh"):
    pack_text = json.loads((PACK / f"i18n/{lang}.json").read_text())
    runtime_text = json.loads((ROOT / f"Code/ArcticPassage/Runtime/i18n/{lang}.json").read_text())
    for key in ["festival.spring.name", "festival.summer.name", "festival.winter.name",
                "festival.spring.dialogue.Ada", "festival.summer.dialogue.Nora", "festival.winter.dialogue.Levin"]:
        require(key in pack_text and pack_text[key], f"{lang}: missing Content Patcher text {key}")
    for key in ["festival.spring.prompt", "festival.summer.quizPrompt", "festival.winter.viewTaken", "festival.answer.shore"]:
        require(key in runtime_text and runtime_text[key], f"{lang}: missing runtime text {key}")

print("PASS three native festival dates, six walkable residents, year variants, local dialogue, interactive activities, guarded transactions, annual rewards, and bilingual placeable art")
print("NOTE native temporary-map entry, minigame callbacks, exit/return, and next-year replay still require ordinary in-game verification")
