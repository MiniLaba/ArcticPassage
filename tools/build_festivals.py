"""Build three scope-frozen native festivals using existing Frosthavn maps."""
from pathlib import Path
import json
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "ContentPack"
RUNTIME = ROOT / "Code/ArcticPassage/Runtime/i18n"
TAG = "R08 native festivals: "

FESTIVALS = {
    "spring9": {
        "id": "spring", "location": "ArcticPassage_Harbor", "map": "ArcticPassage_Harbor",
        "hours": "900 1800", "spawn": "24 23 2",
        "actor_tiles": [(16, 23), (21, 23), (28, 23), (34, 23), (40, 23), (46, 23)],
        "name": ("Harbor Opening Day", "春季开航日"), "place": ("the harbor", "渔港"),
        "message": ("Harbor Opening Day is underway. Join the fishing challenge, guess a catch, or try today's soup (F).", "春季开航日开始了。按 F 参加钓鱼挑战、猜鱼重，或品尝今日热汤。"),
        "dialogue": [
            ("ArcticPassage_Ada", "The first spring catch tells us how the ice is changing.", "春季第一尾渔获，会告诉我们海冰正在如何变化。"),
            ("ArcticPassage_Mira", "I've made a small pot of fish-and-potato stew for the pier.", "我为码头准备了一锅炖鱼配土豆。"),
            ("ArcticPassage_Roan", "A good cast begins with watching the water, not rushing it.", "好的抛竿要先看水势，不必急着出手。"),
            ("ArcticPassage_Nora", "The prize is small. The stories from the first catch last longer.", "奖品不大，但第一尾鱼带来的故事会留得更久。"),
            ("ArcticPassage_Levin", "We'll note the weight, then return the fish to the cold water.", "我们会记下重量，再把鱼放回冷水里。"),
            ("ArcticPassage_Amma", "The wind is kind today. Keep the line clear of the working boats.", "今天风势温和，记得让钓线避开作业船。"),
        ],
        "item": "ArcticPassage_HarborKnot", "art": "harbor-knot.png",
        "item_name": ("Harbor knot keepsake", "港湾绳结纪念摆件"),
        "item_desc": ("A carefully dressed fishing float tied with the harbor's red signal cord.", "用港口红色信号绳系成的纪念浮漂，可摆在室内。"),
        "accent": "#b45f50",
    },
    "summer18": {
        "id": "summer", "location": "ArcticPassage_Icefjord", "map": "ArcticPassage_Icefjord",
        "hours": "1800 2600", "spawn": "35 34 2",
        "actor_tiles": [(17, 33), (22, 33), (27, 33), (32, 33), (37, 33), (39, 34)],
        "name": ("Midnight Sun Bay Day", "极昼海湾日"), "place": ("the fjord lookout", "峡湾观景岸"),
        "message": ("Midnight Sun Bay Day is bright along the fjord. Press F to join a nature quiz or watch the seabirds.", "峡湾的极昼海湾日仍亮如白昼。按 F 参加自然问答或观察海鸟。"),
        "dialogue": [
            ("ArcticPassage_Ada", "At this hour, the low sun still reaches the ice beyond the bay.", "到了这个时辰，低悬的太阳仍照得到海湾外的浮冰。"),
            ("ArcticPassage_Mira", "There is room at the picnic blanket. Take a cup before the walk.", "野餐毯旁还有空位，散步前先喝一杯吧。"),
            ("ArcticPassage_Roan", "The birds are feeding beyond the outer ice. We watch from shore.", "海鸟正在外侧浮冰附近觅食，我们从岸上观察就好。"),
            ("ArcticPassage_Nora", "No flash near the nesting ledges, please. A quiet view is enough.", "请不要在巢区附近使用闪光灯，安静地看一会儿就很好。"),
            ("ArcticPassage_Levin", "The midnight sun is a season, not a change to the clock.", "午夜太阳是一段季节体验，不会改变游戏时钟。"),
            ("ArcticPassage_Amma", "The dogs have shade and water. We'll keep the path open.", "犬队已经安排了阴凉处和饮水，我们会把通道留出来。"),
        ],
        "item": "ArcticPassage_MidnightSunDisplay", "art": "midnight-sun-display.png",
        "item_name": ("Midnight sun horizon", "午夜太阳地平线摆件"),
        "item_desc": ("A small painted horizon keeps the pale summer light above the fjord.", "描绘夏日浅金色阳光停在峡湾地平线上的纪念摆件。"),
        "accent": "#d9b56f",
    },
    "winter21": {
        "id": "winter", "location": "ArcticPassage_Town", "map": "ArcticPassage_Town",
        "hours": "1800 2600", "spawn": "36 23 2",
        "actor_tiles": [(18, 23), (24, 23), (30, 23), (42, 23), (48, 23), (50, 23)],
        "name": ("Polar Night Lantern Walk", "极夜灯光节"), "place": ("Frosthavn", "霜灯港"),
        "message": ("The Polar Night Lantern Walk has begun. Press F to share soup, exchange a wish, or watch the winter sky.", "极夜灯光节开始了。按 F 分享热汤、交换心愿，或仰望冬夜。"),
        "dialogue": [
            ("ArcticPassage_Ada", "The lamps are low and warm. We keep the dark sky visible above them.", "灯光只留温暖的一圈，也让上方的暗夜天空看得见。"),
            ("ArcticPassage_Mira", "The soup is ready. There is enough for everyone who made the walk.", "热汤已经好了，走到这里的每个人都能喝上一碗。"),
            ("ArcticPassage_Roan", "The harbor lights help boats find the safe edge of the ice.", "港灯能帮船只辨认浮冰边缘的安全水道。"),
            ("ArcticPassage_Nora", "Leave one lantern unlit for the stars and the aurora, if it comes.", "留一盏灯不点亮，给星星和可能出现的极光留出位置。"),
            ("ArcticPassage_Levin", "On clear nights, look north. On rough nights, the warm windows are enough.", "晴夜可以望向北方；风雪夜里，窗中的暖光就足够了。"),
            ("ArcticPassage_Amma", "The dogs are resting indoors tonight. Let the snow path stay quiet.", "犬队今晚在室内休息，请让积雪小路保持安静。"),
        ],
        "item": "ArcticPassage_WinterLantern", "art": "winter-lantern.png",
        "item_name": ("Frosted harbor lantern", "霜纹港灯摆件"),
        "item_desc": ("A sheltered lantern with a frosted shade, made for a winter window.", "带磨砂灯罩的小型室内港灯，适合摆在冬日窗边。"),
        "accent": "#d58c5f",
    },
}

def draw_item(kind, color):
    im = Image.new("RGBA", (16, 32))
    d = ImageDraw.Draw(im)
    d.ellipse((1, 28, 14, 31), fill="#445b68")
    if kind == "spring":
        d.line((7, 8, 7, 27), fill="#645648", width=1)
        d.polygon([(2, 20), (4, 12), (8, 8), (12, 12), (14, 20), (11, 25), (5, 25)], fill="#b5534d", outline="#4e5050")
        d.ellipse((5, 13, 10, 19), fill="#e9d9b7", outline="#6e6254")
        d.line((7, 20, 10, 25), fill="#ddc69a", width=2)
        d.line((3, 27, 12, 27), fill="#765e47", width=2)
    elif kind == "summer":
        d.line((7, 13, 7, 28), fill="#715d4e", width=2)
        d.rectangle((3, 21, 11, 27), fill="#72573f", outline="#4d5260")
        d.ellipse((1, 2, 14, 15), fill="#f0d38a", outline="#987951")
        d.ellipse((4, 5, 11, 12), fill="#e9aa5e")
        d.line((3, 18, 12, 18), fill="#91abb0", width=1)
        d.line((2, 29, 13, 29), fill="#c4b083", width=1)
    else:
        d.line((7, 28, 7, 12), fill="#526274", width=2)
        d.rectangle((3, 5, 11, 14), fill="#394d5e", outline="#263a4c")
        d.rectangle((5, 7, 9, 12), fill="#f0bf78")
        d.rectangle((4, 2, 10, 4), fill="#526274")
        d.rectangle((5, 0, 9, 1), fill="#82949a")
        d.line((2, 29, 13, 29), fill="#c1b18c", width=1)
    return im

def main():
    content_path = PACK / "content.json"
    content = json.loads(content_path.read_text())
    content["Changes"] = [p for p in content["Changes"] if not p.get("LogName", "").startswith(TAG)]
    strings = {lang: json.loads((PACK / f"i18n/{lang}.json").read_text()) for lang in ("default", "zh")}
    runtime = {lang: json.loads((RUNTIME / f"{lang}.json").read_text()) for lang in ("default", "zh")}
    runtime["default"]["guide.phenomena.aurora.where"] = "Icefjord, glacier lookout or Winter 21 lantern walk · clear winter nights after 18:00."
    runtime["zh"]["guide.phenomena.aurora.where"] = "冰峡湾、冰川观景台或冬21极夜灯光节 · 晴朗冬夜18:00后。"
    def patch(target, **values):
        content["Changes"].append({"Action":"EditData", "Target":target, "LogName":TAG+target, **values})
    dates = {}
    items = {}
    for date, data in FESTIVALS.items():
        i = data["id"]
        date_name = "{{i18n:festival." + i + ".name}}"
        dates[date] = date_name
        event = {
            "name": date_name,
            "conditions": data["location"] + "/" + data["hours"],
            "locationDisplayName": "{{i18n:festival." + i + ".place}}",
            "startedMessage": "{{i18n:festival." + i + ".started}}",
            "set-up_y1": "neutral/-1000 -1000/farmer " + data["spawn"] + "/changeToTemporaryMap " + data["map"] + "/viewport -1000 -1000/globalFadeToClear",
            "set-up_y2": "neutral/-1000 -1000/farmer " + data["spawn"] + "/changeToTemporaryMap " + data["map"] + "/viewport -1000 -1000/globalFadeToClear",
        }
        additions = []
        for n, (npc, en, zh) in enumerate(data["dialogue"]):
            key = "festival." + i + ".dialogue." + npc.rsplit("_", 1)[-1]
            strings["default"][key] = en
            strings["zh"][key] = zh
            event[npc] = "{{i18n:" + key + "}}"
            x, y = data["actor_tiles"][n]
            direction = "down"
            additions.append(f"{npc} {x} {y} {direction}")
        placed = "/".join(additions)
        event["Set-Up_additionalCharacters_y1"] = placed
        event["Set-Up_additionalCharacters_y2"] = placed
        festival_file = PACK / "assets/festivals" / (date + ".json")
        festival_file.parent.mkdir(parents=True, exist_ok=True)
        festival_file.write_text(json.dumps(event, ensure_ascii=False, indent=2) + "\n")
        content["Changes"].append({"Action":"Load", "Target":"Data/Festivals/"+date,
                                    "FromFile":"assets/festivals/"+date+".json", "LogName":TAG+date})
        en_name, zh_name = data["item_name"]
        en_desc, zh_desc = data["item_desc"]
        strings["default"].update({f"festival.reward.{i}.name":en_name, f"festival.reward.{i}.desc":en_desc})
        strings["zh"].update({f"festival.reward.{i}.name":zh_name, f"festival.reward.{i}.desc":zh_desc})
        texture = "Mods/WhiteBay.ArcticPassage/Festival" + i.title()
        art_path = PACK / "assets/items" / data["art"]
        draw_item(i, data["accent"]).save(art_path)
        content["Changes"].append({"Action":"Load", "Target":texture, "FromFile":"assets/items/"+data["art"], "LogName":TAG+texture})
        items[data["item"]] = {
            "Name":data["item"], "DisplayName":"{{i18n:festival.reward."+i+".name}}",
            "Description":"{{i18n:festival.reward."+i+".desc}}", "Price":0, "Fragility":0,
            "CanBePlacedIndoors":True, "CanBePlacedOutdoors":False, "Texture":texture, "SpriteIndex":0
        }
        # Festival-facing English and Chinese text, plus activity prompt translations.
        for suffix, (en, zh) in {
            "name":data["name"], "place":data["place"], "started":data["message"]
        }.items():
            key = f"festival.{i}.{suffix}"
            strings["default"][key] = en
            strings["zh"][key] = zh

    # Dates and rewards are native game data; the activity key remains a small runtime layer.
    patch("Data/Festivals/FestivalDates", Entries=dates)
    patch("Data/BigCraftables", Entries=items)
    en_runtime = {
        "festival.key": "F: festival activities",
        "festival.spring.prompt": "Harbor Opening Day",
        "festival.spring.cast": "Enter the pier fishing challenge",
        "festival.spring.quiz": "Guess the weight of today's cod",
        "festival.spring.soup": "Buy fish-and-potato stew — 100g",
        "festival.spring.castStart": "Cast from the public pier. Return here and press F after landing a fish.",
        "festival.spring.noCatch": "The challenge is still waiting for a landed fish. Your bait and time remain yours.",
        "festival.spring.quizPrompt": "The cod on the scale weighs 2.1 kg. Which range is closest?",
        "festival.spring.quizWrong": "Not quite. The crew records the estimate; the next cast is still yours.",
        "festival.spring.quizRight": "A close estimate. The harbor crew awards this year's keepsake.",
        "festival.spring.mealNoMoney": "The stew costs 100g. Nothing was taken.",
        "festival.spring.mealBought": "A hot harbor meal for the walk along the pier.",
        "festival.summer.prompt": "Midnight Sun Bay Day",
        "festival.summer.birds": "Watch the seabirds from shore",
        "festival.summer.quiz": "Nature quiz: what keeps nesting birds safe?",
        "festival.summer.quizPrompt": "Where should visitors watch seabirds?",
        "festival.summer.quizWrong": "The note is added to the field guide. Keep the nesting ledges quiet.",
        "festival.summer.quizRight": "Correct: stay on shore and keep a respectful distance. You receive this year's display.",
        "festival.winter.prompt": "Polar Night Lantern Walk",
        "festival.winter.soup": "Share a bowl of hot fish soup — 100g",
        "festival.winter.view": "Take the lantern walk and watch the north",
        "festival.winter.mealNoMoney": "The soup costs 100g. Nothing was taken.",
        "festival.winter.soupBought": "You share a warm supper with the harbor crew. The town remembers it.",
        "festival.winter.viewTaken": "The lanterns stay low. The northern sky remains open if the clouds clear.",
        "festival.rewarded": "You received: {{item}}",
        "festival.already": "You have already received this year's festival keepsake.",
        "festival.notFestival": "These activities are available during the local festival only.",
        "festival.cancel": "Leave for now",
    }
    zh_runtime = {
        "festival.key": "F：节日活动",
        "festival.spring.prompt": "春季开航日",
        "festival.spring.cast": "参加码头钓鱼挑战",
        "festival.spring.quiz": "猜一猜今天这条鳕鱼的重量",
        "festival.spring.soup": "购买炖鱼配土豆　100金",
        "festival.spring.castStart": "从公共码头抛竿。钓上一条鱼后回到这里按 F 提交挑战。",
        "festival.spring.noCatch": "挑战还在等一尾真正上钩的鱼。鱼饵和时间仍由你安排。",
        "festival.spring.quizPrompt": "秤上的鳕鱼重 2.1 千克，哪个范围最接近？",
        "festival.spring.quizWrong": "估得不太准。船员记下了答案，下一竿还是你的。",
        "festival.spring.quizRight": "估得很准。港口船员把今年的纪念摆件送给你。",
        "festival.spring.mealNoMoney": "这碗炖鱼需要 100 金，钱没有扣除。",
        "festival.spring.mealBought": "一份热腾腾的港口炖鱼，适合沿码头慢慢走时吃。",
        "festival.summer.prompt": "极昼海湾日",
        "festival.summer.birds": "留在岸上观察海鸟",
        "festival.summer.quiz": "自然问答：怎样保护筑巢海鸟？",
        "festival.summer.quizPrompt": "游客应在哪里观察海鸟？",
        "festival.summer.quizWrong": "记录已经写进野外手记。请让筑巢岩岸保持安静。",
        "festival.summer.quizRight": "答对了：留在岸上并保持距离。今年的极昼摆件归你了。",
        "festival.winter.prompt": "极夜灯光节",
        "festival.winter.soup": "分享一碗热鱼汤　100金",
        "festival.winter.view": "沿灯笼小路散步，仰望北方天空",
        "festival.winter.mealNoMoney": "这碗热汤需要 100 金，钱没有扣除。",
        "festival.winter.soupBought": "你和港口船员一起吃了热汤，小镇会记住这份心意。",
        "festival.winter.viewTaken": "灯笼保持低亮；云层散开时，北方天空仍清晰可见。",
        "festival.rewarded": "你收到了：{{item}}",
        "festival.already": "今年的节日纪念品已经领过了。",
        "festival.notFestival": "这些活动只在本地节日当天开放。",
        "festival.cancel": "先逛一会儿",
    }
    runtime["default"].update(en_runtime)
    runtime["zh"].update(zh_runtime)
    # Correct-answer response labels and quiz distractors live in data translations.
    for lang, values in {
        "default": {"festival.answer.low":"Under 1 kg", "festival.answer.mid":"1–3 kg", "festival.answer.high":"Over 3 kg", "festival.answer.cliffs":"On the nesting cliffs", "festival.answer.boat":"From a boat beside the colony", "festival.answer.shore":"From shore, at a respectful distance"},
        "zh": {"festival.answer.low":"不足 1 千克", "festival.answer.mid":"1—3 千克", "festival.answer.high":"超过 3 千克", "festival.answer.cliffs":"走到筑巢岩壁旁", "festival.answer.boat":"乘船靠近鸟群", "festival.answer.shore":"留在岸上并保持距离"},
    }.items():
        runtime[lang].update(values)
    content_path.write_text(json.dumps(content, ensure_ascii=False, indent=2) + "\n")
    for lang in strings:
        (PACK / f"i18n/{lang}.json").write_text(json.dumps(strings[lang], ensure_ascii=False, indent=2) + "\n")
    for lang in runtime:
        (RUNTIME / f"{lang}.json").write_text(json.dumps(runtime[lang], ensure_ascii=False, indent=2) + "\n")
    print("Built native festival dates, dialogue, seasonal activities and three placeable keepsakes.")

if __name__ == "__main__":
    main()
