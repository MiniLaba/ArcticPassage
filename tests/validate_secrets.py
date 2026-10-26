"""Static scope audit for the seven authored exploration secrets and ship-model reward."""
from pathlib import Path
import json
import re
import xml.etree.ElementTree as ET
from collections import deque

ROOT = Path(__file__).resolve().parents[1]
runtime = ROOT / "Code/ArcticPassage"
source = (runtime / "SecretDiscoveries.cs").read_text()
guide = (runtime / "FieldGuide.cs").read_text()
expected = ["foxTracks", "icebergLookout", "midnightSun", "snowyOwl", "whaleShadow", "polarNightLights", "oldShipLog"]
assert all(f'("{key}",' in source for key in expected), "the seven frozen secrets changed or are incomplete"
assert re.findall(r'^\s*\("([A-Za-z]+)", "ArcticPassage_', source, re.M) == expected, "out-of-scope secret entries were added"
assert "YesterdayWasSnowy" in source and "PolarForecast.ForDate" in source
assert "PolarPhenomena.Available(\"midnightSun\")" in source
assert "WildlifeSightings.Available(WildlifeSightings.All[5])" in source
assert "WildlifeSightings.Available(WildlifeSightings.All[8])" in source
assert "friendship.Points >= 500" in source and "ArcticPassage_Roan" in source
assert "Game1.player.modData[Prefix + entry.Id] = stamp" in source
assert "Game1.player.mailbox.Add(ShipModelMail)" in source
assert "case SButton.D7" in guide and "book.Page == 6" in guide and "guide.RecordSecret" in guide

def map_layers(location, season):
    path = ROOT / "ContentPack/assets/maps" / f"{location}_{season}.tmx"
    root = ET.parse(path).getroot()
    width, height = int(root.get("width")), int(root.get("height"))
    props = {}
    for tileset in root.findall("tileset"):
        first = int(tileset.get("firstgid"))
        props.update({first + i: {} for i in range(int(tileset.get("tilecount")))})
        for tile in tileset.findall("tile"):
            props[first + int(tile.get("id"))] = {
                prop.get("name"): prop.get("value") for prop in tile.findall("./properties/property")
            }
    layers = {
        layer.get("name"): [int(v.strip()) for v in layer.find("data").text.strip().split(",")]
        for layer in root.findall("layer")
    }
    def walk(x, y):
        if not (0 <= x < width and 0 <= y < height): return False
        back = layers["Back"][y * width + x]
        building = layers["Buildings"][y * width + x]
        return back > 0 and "Passable" not in props[back] and (
            not building or "Passable" in props[building]
        )
    seen = set()
    spawn = tuple(json.loads((ROOT / "docs/build-index.json").read_text())["maps"][location]["points"]["spawn"])
    if not walk(*spawn): return width, layers, props, set()
    seen.add(spawn)
    queue = deque([spawn])
    while queue:
        x, y = queue.popleft()
        for nxt in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if nxt not in seen and walk(*nxt):
                seen.add(nxt); queue.append(nxt)
    return width, layers, props, seen

positions = {
    "Tundra": {"spring": [(25, 4), (25, 5), (25, 33)], "summer": [(25, 4)],
               "fall": [(25, 5)], "winter": [(25, 5), (25, 33)]},
    "Icefjord": {s: [(11, 21)] for s in ("spring", "summer", "fall", "winter")},
    "Town": {s: [(24, 15)] for s in ("spring", "summer", "fall", "winter")},
    "Harbor": {s: [(21, 7)] for s in ("spring", "summer", "fall", "winter")},
}
maps = {}
for name, seasons in positions.items():
    for season, points in seasons.items():
        width, layers, props, seen = map_layers(name, season)
        maps[name, season] = (width, layers, props, seen)
        for point in points:
            assert point in seen, f"secret discovery point is not reachable: {name}_{season} {point}"

# Whale remains offshore. A walkable observation tile must be inside its existing view radius.
width, layers, props, seen = map_layers("Icefjord", "summer")
whale = (48, 33)
assert any(abs(x - whale[0]) + abs(y - whale[1]) <= 16 for x, y in seen), "whale has no reachable viewing shore"

# The old-log discovery is attached to an existing Harbor stop, without adding a new NPC route.
roan = json.loads((ROOT / "ContentPack/assets/data/Roan_schedule.json").read_text())
assert any("ArcticPassage_Harbor" in value for value in roan.values()), "Roan has no existing harbor route for the log scene"

content = json.loads((ROOT / "ContentPack/content.json").read_text())
patches = content["Changes"]
boat = [p for p in patches if p.get("Target") == "Data/BigCraftables" and "ArcticPassage_OldShipModel" in p.get("Entries", {})]
assert boat and boat[-1]["Entries"]["ArcticPassage_OldShipModel"]["CanBePlacedIndoors"] is True
mail = [p for p in patches if p.get("Target") == "Data/mail" and "ArcticPassage_OldShipModelMail" in p.get("Entries", {})]
assert mail and "%item bigobject ArcticPassage_OldShipModel %%" in json.loads((ROOT / "ContentPack/i18n/default.json").read_text())["mail.oldShipModel"]
assert (ROOT / "ContentPack/assets/items/old-ship-model.png").is_file()

for lang in ("default", "zh"):
    text = json.loads((runtime / f"Runtime/i18n/{lang}.json").read_text())
    assert "guide.tab.6" in text and all(f"guide.secret.{key}.clue" in text for key in expected)
    assert all(f"guide.secret.{key}.body" in text for key in expected)

# The deterministic forecast offers at least one winter morning after fresh snow.
MASK = 0xffffffff
def raw(ordinal):
    value = (ordinal + 0x9E3779B9) & MASK
    value ^= value >> 16; value = value * 0x7FEB352D & MASK
    value ^= value >> 15; value = value * 0x846CA68B & MASK
    value ^= value >> 16
    return "blizzard" if value % 100 < 13 else "gale" if value % 100 < 42 else "calm"
def forecast(ordinal):
    current = raw(ordinal)
    return "calm" if current != "calm" and raw(ordinal - 1) != "calm" else current
assert any(
    forecast((year - 1) * 112 + 3 * 28 + day - 2) == "blizzard"
    for year in range(1, 8) for day in range(2, 29)
), "no reachable morning after a winter blizzard"
print("PASS seven scope-frozen discoveries: reachable clue tiles, winter track dates, wildlife/sky links, friendship-gated ship log, and placeable mail reward")
