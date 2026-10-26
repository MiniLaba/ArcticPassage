"""Targeted static test for the 9/8/4/4 research ledger and its earned reward."""
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]
runtime = ROOT / "Code/ArcticPassage"
fish = ["Capelin", "NorthernShrimp", "PolarCod", "AtlanticCod", "ArcticChar", "SnowCrab", "Wolffish", "Halibut", "GoldenRedfish"]
animal = ["bear", "fox", "caribou", "seal", "walrus", "owl", "kittiwake", "sleddog"]
phenomena = ["midnightSun", "polarNight", "aurora", "blizzard"]

research_code = (runtime / "FieldResearch.cs").read_text()
field_code = (runtime / "FieldGuide.cs").read_text()
phenomena_code = (runtime / "PolarPhenomena.cs").read_text()
assert all(f'"{key}"' in research_code for key in fish), "fish collection misses a target species"
assert "fishCaught.Keys.Any" in research_code and "SamplePrefix" in research_code, "ledger must read native catches and submitted samples"
assert "AnimalCount == 8" in research_code and "LandformCount == 4" in research_code and "PhenomenonCount == 4" in research_code
assert all(f'"{key}"' in phenomena_code for key in phenomena)
assert "PolarPhotoperiod" in phenomena_code and "PolarWeather.Today" in phenomena_code and "DrawAurora" in phenomena_code
assert '"guide.research.progress."' in field_code

data = json.loads((ROOT / "ContentPack/content.json").read_text())
patches = data["Changes"]
bc = [p for p in patches if p.get("Target") == "Data/BigCraftables" and "ArcticPassage_FieldAtlasDisplay" in p.get("Entries", {})]
assert bc, "field-atlas reward isn't registered as a placeable"
assert bc[-1]["Entries"]["ArcticPassage_FieldAtlasDisplay"]["CanBePlacedIndoors"] is True
mail = [p for p in patches if p.get("Target") == "Data/mail" and "ArcticPassage_ResearchDisplay" in p.get("Entries", {})]
assert mail and mail[-1]["Entries"]["ArcticPassage_ResearchDisplay"] == "{{i18n:mail.researchReward}}"
mail_text = json.loads((ROOT / "ContentPack/i18n/default.json").read_text())["mail.researchReward"]
assert "%item bigobject ArcticPassage_FieldAtlasDisplay %%" in mail_text
art_patch = [p for p in patches if p.get("Target") == "Mods/WhiteBay.ArcticPassage/FieldAtlasDisplay"]
assert art_patch and (ROOT / "ContentPack/assets/items/field-atlas-display.png").is_file()

for lang in ("default", "zh"):
    values = json.loads((runtime / f"Runtime/i18n/{lang}.json").read_text())
    assert all(f"guide.research.fish.{key}" in values for key in fish)
    assert all(f"guide.phenomena.{key}.body" in values for key in phenomena)
    assert all(f"guide.tab.{i}" in values for i in range(6))
    assert all(f"guide.research.progress.{group}" in values for group in ("fish", "animals", "phenomena", "landforms", "samples"))
    for key, value in values.items():
        if key.startswith(("guide.research.progress.", "guide.phenomena.progress")):
            assert value.count("{{") == value.count("}}")

# Assert the deterministic aurora/blizzard calendar provides reachable dates,
# without editing a save or treating this schedule audit as an in-game sighting.
MASK = 0xffffffff
def raw(ordinal, winter=True):
    value = (ordinal + 0x9E3779B9) & MASK
    value ^= value >> 16; value = value * 0x7FEB352D & MASK
    value ^= value >> 15; value = value * 0x846CA68B & MASK
    value ^= value >> 16
    roll = value % 100
    return "blizzard" if winter and roll < 13 else "gale" if winter and roll < 42 else "calm"
def forecast(ordinal):
    today = raw(ordinal)
    return "calm" if today != "calm" and raw(ordinal - 1) != "calm" else today

aurora_days=[]; blizzard_days=[]
for year in range(1, 8):
    for day in range(1, 29):
        ordinal=(year-1)*112+3*28+day-1
        if day % 4 == 1 and forecast(ordinal)=="calm": aurora_days.append((year,day))
        if forecast(ordinal)=="blizzard": blizzard_days.append((year,day))
assert aurora_days and blizzard_days, "phenomenon calendar contains no reachable clear aurora or blizzard date"
print(f"PASS research ledger: 9 seafood / 8 animal classes / 4 phenomena / 4 landforms; native placeable reward; reachable schedule examples aurora={aurora_days[0]} blizzard={blizzard_days[0]}")
