"""Build the seventh-page exploration discoveries and Roan's native boat-model reward."""
from pathlib import Path
import json
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "ContentPack"
RUNTIME = ROOT / "Code/ArcticPassage/Runtime/i18n"
TAG = "R08 authored discoveries: "
ITEM_ID = "ArcticPassage_OldShipModel"
MAIL_ID = "ArcticPassage_OldShipModelMail"

DISCOVERIES = {
    "foxTracks": (
        ("Arctic fox tracks", "After a fresh winter squall, look for small tracks at the northern tundra path at dawn.",
         "Four small prints cross the new snow and lead toward the fox's distant route."),
        ("北极狐足迹", "冬季风雪过后的清晨，沿苔原北侧小路寻找细小脚印。",
         "四组足迹穿过新雪，通向北极狐远远经过的路线。")),
    "icebergLookout": (
        ("The quiet lookout", "A less-traveled shore path on the west side of the fjord reaches a bench above the ice.",
         "The hidden bench gives a still view across the icebergs, far from the working pier."),
        ("静观冰山", "沿峡湾西侧较少经过的岸路走到长椅，那里能安静地俯瞰浮冰。",
         "隐蔽的长椅远离繁忙码头，可以静静看着冰山与浮冰。")),
    "midnightSun": (
        ("Midnight sun", "On a late summer night, take the high tundra path while the horizon is still bright.",
         "The low sun remains at the horizon. This is a field note, not a change to the clock."),
        ("午夜太阳", "夏夜很深时沿苔原高处小路前行，地平线仍留着亮光。",
         "太阳仍低悬在地平线附近。这是一则自然笔记，不会改变游戏时钟。")),
    "snowyOwl": (
        ("Snowy owl", "A pale shape returns to the northern ridge on some autumn and winter mornings.",
         "The owl lifts from the rocks after a respectful, distant observation."),
        ("雪鸮", "秋冬的部分清晨，北侧山脊会出现一道浅色身影。",
         "保持距离观察后，雪鸮从岩石上振翅离开。")),
    "whaleShadow": (
        ("A whale beyond the ice", "On selected summer afternoons, wait at the fjord water beyond the floating ice.",
         "A back and brief blow appear offshore, then vanish behind the ice. The sighting is never a catch."),
        ("浮冰外的鲸影", "夏季某些午后，在峡湾浮冰外侧的海水边等候片刻。",
         "远海露出鲸背与一阵短促喷气，随后消失在冰山后。这不是一项渔获。")),
    "polarNightLights": (
        ("Lights in the long night", "Visit the town lamps after dark during winter's short blue day.",
         "Warm windows and harbor lamps hold their colour against the winter twilight."),
        ("极夜灯光", "冬日短暂的蓝色暮光之后，沿着小镇与港口的灯火慢慢走。",
         "窗里的暖光和码头灯火，在漫长冬夜中留住了温度。")),
    "oldShipLog": (
        ("Roan's old ship log", "Find Roan at the harbor once your friendship has grown; ask about the old crossing.",
         "Roan shares a page from his grandfather's route book. The miniature boat is a keepsake, not a travel unlock."),
        ("罗安的旧航海记录", "与罗安熟悉之后，在港口找到他，听听那次旧航程的故事。",
         "罗安分享了祖父航线簿中的一页。小船模型只是纪念物，不会解锁新航线。"))
}

def draw_model():
    image = Image.new("RGBA", (16, 32))
    d = ImageDraw.Draw(image)
    d.ellipse((1, 28, 14, 31), fill="#4b6472")
    d.rectangle((3, 20, 12, 27), fill="#76583e", outline="#344958")
    d.rectangle((4, 21, 11, 25), fill="#a97758")
    d.polygon([(3, 18), (13, 18), (10, 23), (6, 23)], fill="#a84f45", outline="#493e3c")
    d.line((8, 6, 8, 18), fill="#584c42", width=1)
    d.polygon([(8, 7), (12, 10), (8, 12)], fill="#e3d7bb", outline="#716856")
    d.polygon([(7, 8), (4, 10), (7, 12)], fill="#d4c9ae", outline="#716856")
    d.line((3, 18, 13, 18), fill="#d7bc92", width=1)
    d.point((8, 19), fill="#e0c18e")
    return image

def main():
    content_path = PACK / "content.json"
    content = json.loads(content_path.read_text())
    content["Changes"] = [p for p in content["Changes"] if not p.get("LogName", "").startswith(TAG)]
    pack_text = {lang: json.loads((PACK / f"i18n/{lang}.json").read_text()) for lang in ("default", "zh")}
    runtime_text = {lang: json.loads((RUNTIME / f"{lang}.json").read_text()) for lang in ("default", "zh")}

    def patch(target, **args):
        content["Changes"].append({"Action": "EditData", "Target": target, "LogName": TAG + target, **args})

    runtime_text["default"].update({
        "guide.tab.6": "Hidden traces",
        "guide.keys": "K / Esc: close   1–7 / left-right: pages   up-down: select   R: record nearby clues",
        "guide.secret.progress": "{{count}} / {{total}} discoveries",
        "guide.secret.unknown": "Unfound clue",
        "guide.secret.clueTitle": "A quiet clue",
        "guide.secret.help": "Reach the place when its season, time and conditions match, then press R to record the discovery.",
        "guide.secret.recordButton": "Record nearby discovery  R",
        "guide.secret.tooFar": "The clue is not ready or you are not close enough to it yet.",
        "guide.secret.recorded": "Discovery recorded:",
    })
    runtime_text["zh"].update({
        "guide.tab.6": "隐藏线索",
        "guide.keys": "K / Esc：关闭　1—7 / 左右：翻页　上下：选择　R：记录附近线索",
        "guide.secret.progress": "已发现 {{count}} / {{total}}",
        "guide.secret.unknown": "尚未揭开的线索",
        "guide.secret.clueTitle": "一条安静的线索",
        "guide.secret.help": "在合适的季节、时段和天气来到地点，走近后按 R 记录发现。",
        "guide.secret.recordButton": "记录附近发现　R",
        "guide.secret.tooFar": "线索还未出现，或你离它还不够近。",
        "guide.secret.recorded": "已记录发现：",
    })

    for key, (en, zh) in DISCOVERIES.items():
        runtime_text["default"].update({
            f"guide.secret.{key}.name": en[0],
            f"guide.secret.{key}.clue": en[1],
            f"guide.secret.{key}.body": en[2],
        })
        runtime_text["zh"].update({
            f"guide.secret.{key}.name": zh[0],
            f"guide.secret.{key}.clue": zh[1],
            f"guide.secret.{key}.body": zh[2],
        })

    en_name, en_desc = "Old harbor boat model", "A small wooden keepsake of the old Greenland crossing. A reminder of a route once kept by hand."
    zh_name, zh_desc = "旧航线船模", "格陵兰旧航线的木制纪念模型，记着一段曾靠双手守护的航程。"
    for lang, values in [("default", (en_name, en_desc)), ("zh", (zh_name, zh_desc))]:
        pack_text[lang].update({
            "secret.shipModel.name": values[0],
            "secret.shipModel.desc": values[1],
            "mail.oldShipModel": (
                "I found this model in my grandfather's chart chest. The old boat kept close to the ice and carried more stories than cargo. I thought you should have it.^-Roan %item bigobject " + ITEM_ID + " %%[#]The old crossing"
                if lang == "default" else
                "我在祖父的航海图柜里找到了这只船模。那条旧船总沿着浮冰谨慎前行，装下的故事比货物还多。我想把它交给你。^-罗安 %item bigobject " + ITEM_ID + " %%[#]旧日航线"
            )
        })

    art_path = PACK / "assets/items/old-ship-model.png"
    art_path.parent.mkdir(parents=True, exist_ok=True)
    draw_model().save(art_path)
    patch("Mods/WhiteBay.ArcticPassage/OldShipModel", Action="Load", FromFile="assets/items/old-ship-model.png")
    patch("Data/BigCraftables", Entries={ITEM_ID: {
        "Name": ITEM_ID,
        "DisplayName": "{{i18n:secret.shipModel.name}}",
        "Description": "{{i18n:secret.shipModel.desc}}",
        "Price": 0, "Fragility": 0, "CanBePlacedIndoors": True, "CanBePlacedOutdoors": False,
        "Texture": "Mods/WhiteBay.ArcticPassage/OldShipModel", "SpriteIndex": 0
    }})
    patch("Data/mail", Entries={MAIL_ID: "{{i18n:mail.oldShipModel}}"})

    content_path.write_text(json.dumps(content, ensure_ascii=False, indent=2) + "\n")
    for lang in pack_text:
        (PACK / f"i18n/{lang}.json").write_text(json.dumps(pack_text[lang], ensure_ascii=False, indent=2) + "\n")
    for lang in runtime_text:
        (RUNTIME / f"{lang}.json").write_text(json.dumps(runtime_text[lang], ensure_ascii=False, indent=2) + "\n")
    print("Built seven scope-frozen hidden discoveries and the native old-ship-model mail reward.")

if __name__ == "__main__":
    main()
