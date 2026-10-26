"""Targeted audit for the authored wildlife atlas and native-save sighting catalogue."""
from pathlib import Path
import json
import re
import struct
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
source = (ROOT / "Code/ArcticPassage/WildlifeSightings.cs").read_text()
rows = re.findall(r'new\("([a-z]+)", "(ArcticPassage_[A-Za-z]+)", new\((\d+), (\d+)\), (\d+), "([a-z ]+)", (\d+), (\d+), ([0-9.]+)(?:, (\d+), (\d+))?\)', source)
expected = ["bear", "fox", "caribou", "seal", "walrus", "owl", "kittiwake", "sleddog", "whale", "shark"]
assert [row[0] for row in rows] == expected, f"wildlife scope/order changed: {[row[0] for row in rows]}"
assert len({row[4] for row in rows}) == len(rows), "wildlife sprite frames overlap"
assert all(ROOT.joinpath("ContentPack/assets/maps", row[1].removeprefix("ArcticPassage_") + "_winter.tmx").exists() for row in rows), "a wildlife location lacks a winter map"
assert all(int(row[6]) < int(row[7]) for row in rows), "wildlife time window is invalid"
for row in rows:
    species, location, x, y = row[:4]
    if species not in {"walrus", "whale", "shark"}: continue
    map_root = ET.parse(ROOT / "ContentPack/assets/maps" / f"{location.removeprefix('ArcticPassage_')}_winter.tmx").getroot()
    width = int(map_root.get("width")); index = int(y) * width + int(x)
    gids = [int(v.strip()) for v in map_root.find("layer[@name='Back']/data").text.replace("\n", "").split(",") if v.strip()]
    gid = gids[index]
    water_gids = set()
    for tileset in map_root.findall("tileset"):
        first = int(tileset.get("firstgid"))
        for tile in tileset.findall("tile"):
            if any(p.get("name") == "Water" and p.get("value") == "I" for p in tile.findall("properties/property")):
                water_gids.add(first + int(tile.get("id")))
    assert gid in water_gids, f"marine sprite {species} must be staged over open water at {x},{y}"
assert "WhiteBay.ArcticPassage/FieldGuide/animal_" in source and "Game1.player.modData" in source, "wildlife records must use farmer save data"
assert "sleddog\" && !Game1.player.mailReceived.Contains(\"ArcticPassage_Shed\")" in source, "working dogs should remain tied to the repaired yard"
assert "PolarBearActive && (from==2 || to==2)" in (ROOT / "Code/ArcticPassage/SledTravel.cs").read_text(), "polar-bear sighting safety hold missing"

for language in ["default", "zh"]:
    data = json.loads((ROOT / f"Code/ArcticPassage/Runtime/i18n/{language}.json").read_text())
    assert all(f"guide.wildlife.{name}.name" in data for name in expected), f"{language}: wildlife names incomplete"
    assert all(f"guide.wildlife.{name}.body" in data for name in expected), f"{language}: wildlife field notes incomplete"
    assert "guide.wildlife.safety" in data and "sled.wildlifeClosed" in data

atlas = ROOT / "Code/ArcticPassage/Runtime/assets/wildlife/sightings.png"
assert atlas.exists(), "generated wildlife atlas missing; run tools/build_runtime.py"
raw = atlas.read_bytes()
assert raw[:8] == b"\x89PNG\r\n\x1a\n"
width, height = struct.unpack(">II", raw[16:24])
assert (width, height) == (320, 48), f"atlas dimensions unexpected: {width}x{height}"
staged = ROOT.parent / ".development/RuntimeMod/assets/wildlife/sightings.png"
if staged.exists():
    assert staged.read_bytes() == raw, "staged runtime wildlife atlas differs from generated source"
print("PASS eight Greenland wildlife classes plus whale/shark distant research sightings; dated native-save records, bilingual notes, safety hold, and two-frame code-drawn atlas")
