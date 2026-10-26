"""Add the one-scope fieldwork reward as a native placeable and ordinary mail."""
from pathlib import Path
import json
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "ContentPack"
TAG = "R05 fieldwork reward: "
ITEM_ID = "ArcticPassage_FieldAtlasDisplay"
MAIL_ID = "ArcticPassage_ResearchDisplay"

def main():
    content_path = PACK / "content.json"
    content = json.loads(content_path.read_text())
    content["Changes"] = [p for p in content["Changes"] if not p.get("LogName", "").startswith(TAG)]
    text = {lang: json.loads((PACK / f"i18n/{lang}.json").read_text()) for lang in ("default", "zh")}
    def patch(target, **kw):
        content["Changes"].append({"Action":"EditData", "Target":target, "LogName":TAG+target, **kw})

    en_name = "Field-atlas display"
    zh_name = "野外图集展示架"
    en_desc = "A small framed chart made from the harbor team's field notes. Place it indoors as a record of patient observation."
    zh_desc = "用港口团队野外记录装裱的小幅图表。可摆在室内，纪念一次次耐心观察。"
    for lang, values in [("default", (en_name, en_desc)), ("zh", (zh_name, zh_desc))]:
        text[lang].update({
            "research.reward.name": values[0],
            "research.reward.desc": values[1],
            "mail.researchReward": (
                "Your records are complete.^The catch log, field samples and careful views of the coast now form a useful atlas. I made this small display for the guesthouse or your home. Thank you for looking without disturbing the wildlife.^-Levin %item bigobject " + ITEM_ID + " %%[#]A field atlas for Frosthavn"
                if lang == "default" else
                "你的野外记录已经齐全。^渔获档案、研究样本和对海岸的细致观察，如今拼成了一本实用图集。我做了这个小展示架，你可以摆在旅舍或家中。谢谢你以不惊扰野生动物的方式观察。^-莱文 %item bigobject " + ITEM_ID + " %%[#]霜灯港野外图集"
            )
        })

    art = Image.new("RGBA", (16, 32))
    d = ImageDraw.Draw(art)
    # Native 16x32 BigCraftable cell; the object reads as a compact wooden
    # map stand, with coast/ice marks rather than arbitrary treasure imagery.
    d.ellipse((1, 27, 14, 31), fill="#4b6472")
    d.rectangle((3, 9, 12, 25), fill="#72583f", outline="#344958")
    d.rectangle((4, 8, 11, 22), fill="#c4ae7b", outline="#394d5a")
    d.rectangle((5, 9, 10, 21), fill="#e1e0c9")
    d.polygon([(5, 12), (7, 10), (8, 14), (7, 18), (9, 20), (6, 19)], fill="#668b9a")
    d.line((8, 12, 10, 10, 10, 16, 8, 18), fill="#567b8c", width=1)
    d.line((5, 15, 10, 15), fill="#b77357", width=1)
    d.rectangle((5, 23, 10, 25), fill="#c9b185")
    d.line((5, 25, 3, 29), fill="#69523d", width=2)
    d.line((10, 25, 12, 29), fill="#69523d", width=2)
    d.line((4, 29, 12, 29), fill="#b39160", width=1)
    path = PACK / "assets/items/field-atlas-display.png"
    path.parent.mkdir(parents=True, exist_ok=True)
    art.save(path)

    patch("Mods/WhiteBay.ArcticPassage/FieldAtlasDisplay", Action="Load", FromFile="assets/items/field-atlas-display.png")
    patch("Data/BigCraftables", Entries={ITEM_ID:{
        "Name":"ArcticPassage_FieldAtlasDisplay",
        "DisplayName":"{{i18n:research.reward.name}}",
        "Description":"{{i18n:research.reward.desc}}",
        "Price":0,"Fragility":0,"CanBePlacedIndoors":True,"CanBePlacedOutdoors":False,
        "Texture":"Mods/WhiteBay.ArcticPassage/FieldAtlasDisplay","SpriteIndex":0
    }})
    patch("Data/mail", Entries={MAIL_ID:"{{i18n:mail.researchReward}}"})
    content_path.write_text(json.dumps(content, ensure_ascii=False, indent=2)+"\n")
    for lang in text:
        (PACK / f"i18n/{lang}.json").write_text(json.dumps(text[lang], ensure_ascii=False, indent=2)+"\n")
    print("Built native field-atlas display and its single player-earned research letter.")

if __name__ == "__main__": main()
