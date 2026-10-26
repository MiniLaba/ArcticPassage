"""Targeted static audit for the chapter 6–10 native quest chain."""
from pathlib import Path
import json
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from simple_rgba import png_size
PACK = ROOT / "ContentPack"
patches = json.loads((PACK / "content.json").read_text())["Changes"]
def require(value, message):
    if not value:
        raise AssertionError(message)

by_target = {}
for patch in patches:
    by_target.setdefault(patch.get("Target"), []).append(patch)
quests = {}
for patch in by_target.get("Data/Quests", []):
    quests.update(patch.get("Entries", {}))
def fields(name):
    return quests["ArcticPassage_" + name].split("/")

chain = ["FieldReport", "StormReadiness", "StormSupplies", "StormFish", "StormRoute", "CampVisit", "ShelterLesson", "IceCatch", "MultiWaterCatch", "DriedOrder", "FinalePreparation", "WarmHarbor"]
for a, b in zip(chain, chain[1:]):
    require(fields(a)[5] == "ArcticPassage_" + b, f"Broken chapter transition {a} -> {b}")
require(fields("WarmHarbor")[5] == "-1", "Final chapter must end without an infinite quest loop")
require("#$action" not in quests["ArcticPassage_DriedOrder"],
        "Mail progression must not rely on response-only dialogue directives")
deep = fields("DeepCatch")
require(deep[5] == "ArcticPassage_FieldReport", "Deep-water chapter is not connected to the field-notes chapter")
require(fields("FieldReport")[0] == "ItemDelivery" and fields("FieldReport")[4] == "ArcticPassage_Levin (O)ArcticPassage_FieldReport 1",
        "Field report must be delivered to Levin as a real item")
require(fields("StormReadiness")[0] == "Location" and fields("StormReadiness")[4] == "ArcticPassage_CommunityHouse",
        "Storm preparation must begin at the existing community house")
require("ArcticPassage_StormSuppliesUnlocked" in (ROOT / "Code/ArcticPassage/StoryChapterRuntime.cs").read_text(),
        "Community-house arrival must unlock the supply order from native quest completion")
require(fields("StormRoute")[0] == "Basic" and "MiraInteraction" in (ROOT / "Code/ArcticPassage/StoryChapterRuntime.cs").read_text(),
        "Chapter 7 must confirm the marked safe route on the tundra")
require(fields("CampVisit")[0] == "Location" and fields("CampVisit")[4] == "ArcticPassage_WinterCamp",
        "Chapter 8 must visit the existing field camp")
require(fields("ShelterLesson")[0] == "Basic" and fields("IceCatch")[0] == "Basic",
        "Chapter 8 interaction steps must remain explicit native quest-log entries")
require(fields("CampVisit")[5] == "ArcticPassage_ShelterLesson"
        and fields("ShelterLesson")[5] == "ArcticPassage_IceCatch",
        "Chapter 8 must sequence camp arrival, snow-block lesson, then real ice catch")
chapter_runtime = (ROOT / "Code/ArcticPassage/StoryChapterRuntime.cs").read_text()
for signal in ["completedSpecialOrders.Contains", "SnowShelterLesson.RecordKey", "IceFishing.IsOpen", "calculateBobberTile", "e.QuantityChanged", "FishCaught", "completeQuest(quest.id.Value)"]:
    require(signal in chapter_runtime, f"Chapter 8 progression does not verify the actual interaction: {signal}")
require(fields("DriedOrder")[0] == "Basic" and fields("MultiWaterCatch")[0] == "Basic",
        "Chapter 9 must require real multi-water catches followed by native processed-fish counter trade")
require(fields("WarmHarbor")[0] == "Basic" and fields("FinalePreparation")[4] == "ArcticPassage_Nora (O)388 10",
        "Chapter 10 requires real lantern materials and a staged finale, not a location-only completion")
events = {}
for patch in by_target.get("Data/Events/ArcticPassage_Town", []): events.update(patch.get("Entries", {}))
finale = events.get("ArcticPassage_HarborHomecoming/m ArcticPassage_FinaleReady/t 1800 2400", "")
require("changeToTemporaryMap ArcticPassage_FinaleWinter" in finale and "/skippable/" in finale,
        "The finale must use a skippable native winter tableau without changing the player's date")
for npc in ("Nora", "Roan", "Ada", "Mira", "Levin", "Amma"):
    require("speak ArcticPassage_" + npc in finale, "Missing finale resident: " + npc)
winter = ET.parse(PACK / "assets/maps/Town_winter.tmx").getroot()
width = int(winter.get("width"))
layers = {layer.get("name"): [int(n) for n in layer.find("data").text.strip().split(',')] for layer in winter.findall("layer")}
actors = finale.split('/')[2].split()
positions = [(int(actors[i+1]), int(actors[i+2])) for i in range(0, len(actors), 4)]
require(len(positions) == len(set(positions)) == 7, "Finale actors overlap")
for x,y in positions:
    require(layers["Back"][y*width+x] and not layers["Buildings"][y*width+x], f"Blocked finale actor {x},{y}")
shops = {}
for patch in by_target.get("Data/Shops", []): shops.update(patch.get("Entries", {}))
exports = [item for item in shops["ArcticPassage_Orders"]["Items"] if item.get("Id", "").startswith(("StoryExport_", "LongExport_"))]
require(len(exports) == 6, "Every drying recipe needs a first-export and upgraded-buyer offer")
require(all(item["TradeItemAmount"] == 1 and item["AvailableStock"] == 1 and len(item["ActionsOnPurchase"]) == 2 for item in exports),
        "Exports must consume real processed fish and write a persistent receipt with their payment")

research = (ROOT / "Code/ArcticPassage/FieldResearch.cs").read_text()
festival = (ROOT / "Code/ArcticPassage/FestivalRuntime.cs").read_text()
for condition in [
    'StoryChapterRuntime.WasCompleted("ArcticPassage_DeepCatch")', "AnimalCount < 3", "LandformCount < 1",
    'WildlifeSightings.Has("whale")', 'Game1.player.mailbox.Add(mail)'
]:
    require(condition in research, f"Chapter 6 unlock is missing real field evidence: {condition}")
require('QueueChapterTenLetter' not in festival,
        "Festival attendance must not be a hard gate on the year-round story ending")

objects = {}
for patch in by_target.get("Data/Objects", []):
    objects.update(patch.get("Entries", {}))
require("ArcticPassage_FieldReport" in objects, "Missing physical chapter 6 report item")
require(png_size(PACK / "assets/items/field-report.png") == (16,16), "Chapter report sprite dimensions")
bigcraftables = {}
for patch in by_target.get("Data/BigCraftables", []):
    bigcraftables.update(patch.get("Entries", {}))
require("ArcticPassage_IceShelterModel" in bigcraftables, "Missing chapter 8 snow-house study reward")
require(png_size(PACK / "assets/items/ice-shelter-model.png") == (16,32), "Chapter 8 reward sprite dimensions")
require("ArcticPassage_WindbreakScreen" in bigcraftables
        and png_size(PACK / "assets/items/windbreak-screen.png") == (16,32), "Missing chapter 7 indoor windbreak reward")
mail = {}
triggers = {}
for patch in by_target.get("Data/mail", []): mail.update(patch.get("Entries", {}))
for patch in by_target.get("Data/TriggerActions", []): triggers.update(patch.get("Entries", {}))
require("ArcticPassage_FieldReportLetter" in mail and "ArcticPassage_Chapter10Letter" in mail
        and "ArcticPassage_IceLessonReward" in mail and "ArcticPassage_StormRouteReward" in mail,
        "Missing native fieldwork, chapter reward, or epilogue mail")
require("ArcticPassage_StoryFieldReportQuest" not in triggers and "ArcticPassage_StoryWarmHarborQuest" not in triggers,
        "Quest progression should use native next-quest links rather than repeatable daily AddQuest triggers")

for lang in ("default", "zh"):
    text = json.loads((PACK / f"i18n/{lang}.json").read_text())
    for key in ["story.mail.field", "story.mail.finale", "story.quest.FieldReport.title",
                "story.quest.StormReadiness.title", "story.quest.CampVisit.title",
                "story.quest.StormSupplies.title", "story.quest.StormFish.title", "story.quest.StormRoute.title",
                "story.quest.ShelterLesson.title", "story.quest.IceCatch.title",
                "story.quest.DriedOrder.title", "story.quest.WarmHarbor.title", "story.iceModel.name"]:
        require(text.get(key), f"{lang}: missing chapter translation {key}")

print("PASS chapter 6 fieldwork; chapter 7 community order → actual emergency fish order → tundra route; chapter 8 camp → actual snow-block lesson → native fish catch at open Icefjord site; placeable rewards are linked")
print("NOTE this is static validation; Windows game startup and native event playback, ordinary completion, saved rewards and cold reload are not certified")
