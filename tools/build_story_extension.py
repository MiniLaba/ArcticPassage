"""Connect the existing field, community, camp, processing, and festival systems into chapters 6-10."""
from pathlib import Path
import json
from simple_rgba import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "ContentPack"
TAG = "R07 chapters 6-10: "
REPORT_ID = "ArcticPassage_FieldReport"
REPORT_MAIL = "ArcticPassage_FieldReportLetter"
FINALE_MAIL = "ArcticPassage_Chapter10Letter"
ICE_REWARD_MAIL = "ArcticPassage_IceLessonReward"
ICE_REWARD_ITEM = "ArcticPassage_IceShelterModel"
ROUTE_REWARD_MAIL = "ArcticPassage_StormRouteReward"
ROUTE_REWARD_ITEM = "ArcticPassage_WindbreakScreen"

def main():
    path = PACK / "content.json"
    content = json.loads(path.read_text())
    content["Changes"] = [p for p in content["Changes"] if not p.get("LogName", "").startswith(TAG)]
    locale = {lang: json.loads((PACK / f"i18n/{lang}.json").read_text()) for lang in ("default", "zh")}

    def patch(action, target, **values):
        content["Changes"].append({"Action":action,"Target":target,"LogName":TAG+target,**values})

    # Deep-water fish closes chapter 5. The real fieldwork ledger then opens 6.
    deep_id = "ArcticPassage_DeepCatch"
    for entry in content["Changes"]:
        if entry.get("Target") != "Data/Quests":
            continue
        data = entry.get("Entries", {})
        if deep_id not in data:
            continue
        parts = data[deep_id].split("/")
        parts[5] = "ArcticPassage_FieldReport"
        data[deep_id] = "/".join(parts)

    # Small native inventory item delivered to Levin after the field ledger is real.
    icon = Image.new("RGBA", (16, 16))
    d = ImageDraw.Draw(icon)
    d.polygon([(3,1),(11,1),(14,4),(14,14),(3,14)], fill="#c6b68e", outline="#405767")
    d.line((11,1,11,4,14,4), fill="#786d5b")
    d.rectangle((5,5,10,6), fill="#587b8b")
    d.line((5,8,12,8), fill="#a45c4f")
    d.line((5,10,11,10), fill="#687b75")
    d.point((7,12), fill="#405767")
    art = PACK / "assets/items/field-report.png"
    art.parent.mkdir(parents=True, exist_ok=True)
    icon.save(art)
    patch("Load", "Mods/WhiteBay.ArcticPassage/FieldReport", FromFile="assets/items/field-report.png")
    patch("EditData", "Data/Objects", Entries={REPORT_ID:{
        "Name":REPORT_ID,"DisplayName":"{{i18n:story.report.name}}","Description":"{{i18n:story.report.desc}}",
        "Type":"Basic","Category":-999,"Price":0,"Edibility":-300,
        "Texture":"Mods/WhiteBay.ArcticPassage/FieldReport","SpriteIndex":0,
        "CanBeGivenAsGift":False,"CanBeTrashed":False,"ExcludeFromFishingCollection":True,
        "ExcludeFromShippingCollection":True
    }})
    patch("EditData", "Data/Objects", Entries={"ArcticPassage_"+name:{
        "Name":"ArcticPassage_"+name,"DisplayName":"{{i18n:story.trade."+kind+".name}}",
        "Description":"{{i18n:story.trade.desc}}","Type":"Basic","Category":-999,
        "Price":0,"Edibility":-300,"Texture":"Mods/WhiteBay.ArcticPassage/FieldReport","SpriteIndex":0,
        "CanBeGivenAsGift":False,"ExcludeFromShippingCollection":True
    } for name,kind in [("PortTradeReceipt","first"),("ExportReceipt","daily")]})

    # Chapter 8 reward: a small, placeable snow-house study model, drawn as a
    # native 16x32 big-craftable cell. It is earned only after the existing
    # winter model lesson and a genuine catch from the opened fjord ice hole.
    shelter = Image.new("RGBA", (16, 32))
    sd = ImageDraw.Draw(shelter)
    sd.ellipse((1, 27, 14, 31), fill="#455e70")
    sd.rectangle((3, 19, 12, 27), fill="#805f43", outline="#354c5d")
    sd.polygon([(2, 20), (4, 14), (7, 11), (9, 8), (12, 14), (14, 20)], fill="#e5eff0", outline="#688697")
    sd.polygon([(5, 19), (7, 14), (9, 14), (11, 19)], fill="#b7d4dc")
    sd.rectangle((7, 20, 9, 26), fill="#465d6b")
    sd.line((4, 27, 3, 30), fill="#72583f", width=2)
    sd.line((11, 27, 12, 30), fill="#72583f", width=2)
    patch("Load", "Mods/WhiteBay.ArcticPassage/IceShelterModel", FromFile="assets/items/ice-shelter-model.png")
    shelter_path = PACK / "assets/items/ice-shelter-model.png"
    shelter_path.parent.mkdir(parents=True, exist_ok=True)
    shelter.save(shelter_path)
    patch("EditData", "Data/BigCraftables", Entries={ICE_REWARD_ITEM:{
        "Name":ICE_REWARD_ITEM,"DisplayName":"{{i18n:story.iceModel.name}}",
        "Description":"{{i18n:story.iceModel.desc}}","Price":0,"Fragility":0,
        "CanBePlacedIndoors":True,"CanBePlacedOutdoors":False,
        "Texture":"Mods/WhiteBay.ArcticPassage/IceShelterModel","SpriteIndex":0
    }})
    windbreak = Image.new("RGBA", (16, 32))
    wd = ImageDraw.Draw(windbreak)
    wd.ellipse((1, 27, 14, 31), fill="#455e70")
    wd.rectangle((3, 10, 12, 27), fill="#72543d", outline="#334b5c")
    wd.rectangle((5, 12, 10, 25), fill="#667d82", outline="#c3a578")
    for y in (15, 19, 23):
        wd.line((6, y, 9, y), fill="#d4c39b")
    wd.line((4, 27, 3, 30), fill="#72583f", width=2)
    wd.line((11, 27, 12, 30), fill="#72583f", width=2)
    windbreak_path = PACK / "assets/items/windbreak-screen.png"
    windbreak_path.parent.mkdir(parents=True, exist_ok=True)
    windbreak.save(windbreak_path)
    patch("Load", "Mods/WhiteBay.ArcticPassage/WindbreakScreen", FromFile="assets/items/windbreak-screen.png")
    patch("EditData", "Data/BigCraftables", Entries={ROUTE_REWARD_ITEM:{
        "Name":ROUTE_REWARD_ITEM,"DisplayName":"{{i18n:story.windbreak.name}}",
        "Description":"{{i18n:story.windbreak.desc}}","Price":0,"Fragility":0,
        "CanBePlacedIndoors":True,"CanBePlacedOutdoors":False,
        "Texture":"Mods/WhiteBay.ArcticPassage/WindbreakScreen","SpriteIndex":0
    }})

    en = {
        "story.report.name":"Field report packet", "story.report.desc":"Levin's compiled packet of verified wildlife, landform, and marine observations.",
        "story.mail.field":"Your field notes line up.^Three distinct animal records, a landform marker, and a distant marine observation make a useful first survey. Please bring this packet to the research station so I can check the details.^-Levin %item object "+REPORT_ID+" %%[#]A record from the coast",
        "story.mail.finale":"The fjord order is complete.^The harbor is working again, the field notes are safe, and the town has a route through the winter. Nora would like to see you in the square when you are ready. The fishery, observations, sled trail, and daily orders will stay open.^-Nora[#]A new season in Frosthavn",
        "story.mail.iceModel":"You took the time to learn how the camp's snow blocks fit together, then waited for safe ice before fishing. Amma made this small snow-house study model for your room. The ice opening is a fixed fishing site; keep to the marked platform.^-Amma %item bigobject "+ICE_REWARD_ITEM+" %%[#]A study from the winter camp",
        "story.iceModel.name":"Snow-house study model", "story.iceModel.desc":"A small model of the camp's carefully fitted snow blocks. Indoor display.",
        "story.mail.windbreak":"You checked the marked route with Mira and left enough room for the dogs and the weather to set the pace. She built this small windbreak screen for the guesthouse entry. Keep the trail clear and turn back when visibility falls.^-Mira %item bigobject "+ROUTE_REWARD_ITEM+" %%[#]A safer way through the wind",
        "story.windbreak.name":"Trail windbreak screen", "story.windbreak.desc":"A small slatted entry screen inspired by the camp's marked safe route. Indoor display.",
        "story.trade.first.name":"First export receipt", "story.trade.daily.name":"Harbor export receipt",
        "story.trade.desc":"The counter has received the processed fish and paid directly into your wallet.",
        "story.routeConfirm":"The return markers are clear and the trail stays on firm ground. Keep the wind at your side, leave room for the dog team, and turn back before visibility closes. I'll keep checking the route with you.",
        "story.export.name":"A box for the next crossing", "story.export.desc":"The harbor's new buyer needs four air-dried fish this week. Donate them at the shared community box. —Ada", "story.export.objective":"Donate four air-dried northern fish for export.",
        "story.finale.nora":"The last lantern post is ready. Tonight we can leave work for a moment and remember the winter light that brought us together.",
        "story.finale.roan":"The boat has a sound hull again. Beyond the warm windows, the next crossing is waiting.",
        "story.finale.ada":"Your catches, careful drying and first export have given the harbor a new rhythm. There will be work here tomorrow.",
        "story.finale.mira":"And a marked way home. If the wind rises, the journey can wait.",
        "story.finale.levin":"We learned to watch quietly: the ice, the birds, and the light moving above us.",
        "story.finale.amma":"The team is resting. The soup is warm. Stay with us until the lanterns settle.",
        "story.finale.end":"Frosthavn is part of your story now. Boats, trails, nature notes and harbor orders remain open whenever you return.",
    }
    zh = {
        "story.report.name":"野外调查记录袋", "story.report.desc":"莱文整理的动物、地貌与远海观察核实资料。",
        "story.mail.field":"你的野外记录已经能相互印证。^三种不同动物、一处地貌标记和一条远海观察，组成了第一份可靠调查。请把这份记录袋带到研究站，我来核对细节。^-莱文 %item object "+REPORT_ID+" %%[#]来自海岸的记录",
        "story.mail.finale":"峡湾订单已经顺利完成。^港口重新忙碌起来，野外记录得到了妥善保存，小镇也拥有了穿过冬季的路线。准备好时，诺拉想请你到广场见面。渔业、观察、雪橇路线和日常订单都会继续开放。^-诺拉[#]霜灯港的新季节",
        "story.mail.iceModel":"你认真学会了营地雪块的搭接方式，也等到安全时才在冰面垂钓。阿玛为你做了这件小小的雪屋研究模型，可以摆在室内。冰洞是固定垂钓点，请始终留在标记木平台上。^-阿玛 %item bigobject "+ICE_REWARD_ITEM+" %%[#]冬营的研究模型",
        "story.iceModel.name":"雪屋研究模型", "story.iceModel.desc":"依照营地雪块搭接方式制作的小模型，可摆在室内。",
        "story.mail.windbreak":"你和米拉一起确认了标记路线，也给犬队和天气留出了决定步速的余地。她为旅舍入口做了这件小小的挡风屏风。请保持雪道畅通，能见度下降时及时折返。^-米拉 %item bigobject "+ROUTE_REWARD_ITEM+" %%[#]风雪中的安全路线",
        "story.windbreak.name":"雪道挡风屏风", "story.windbreak.desc":"灵感来自营地标记路线的窄木条挡风屏风，可摆在室内。",
        "story.trade.first.name":"首次港口出口回执", "story.trade.daily.name":"港口出口回执",
        "story.trade.desc":"柜台已收到加工鱼货，货款已直接入账。",
        "story.routeConfirm":"返程标记清楚，步道也始终留在稳固地面。留意侧风，给犬队让出通路，能见度下降前及时折返。我会继续和你一起检查这条路。",
        "story.export.name":"下一航次的鱼货", "story.export.desc":"港口的新买家本周需要4份风干鱼。请交到社区屋共享货箱。——艾达", "story.export.objective":"交付4份北方风干鱼用于出口。",
        "story.finale.nora":"最后一根灯杆也准备好了。今晚先把工作放一放，一起记住让我们相遇的冬夜灯火。",
        "story.finale.roan":"船身重新结实起来。暖窗之外，下一次航行正等着我们。",
        "story.finale.ada":"你的渔获、慢慢风干的鱼货，还有第一笔出口交易，让港口有了新的节奏。明天，这里仍有日常。",
        "story.finale.mira":"还有一条标记清楚的归途。风大起来的时候，出发可以再等一等。",
        "story.finale.levin":"我们学会了安静地看：看浮冰，看海鸟，也看头顶缓缓经过的光。",
        "story.finale.amma":"犬队已经休息，汤也还热着。等提灯稳下来，再和我们坐一会儿吧。",
        "story.finale.end":"霜灯港也成为了你的故事。船、雪道、自然笔记与港口订单，会在你每次归来时继续开放。",
    }
    for lang, values in (("default",en),("zh",zh)):
        locale[lang].update(values)

    quest_data = {}
    def add_quest(key, kind, title, desc, hint, requirement, next_id, reward, reaction_key, _legacy_completion_action=None):
        name = "ArcticPassage_" + key
        locale["default"][f"story.quest.{key}.title"] = title[0]
        locale["zh"][f"story.quest.{key}.title"] = title[1]
        locale["default"][f"story.quest.{key}.desc"] = desc[0]
        locale["zh"][f"story.quest.{key}.desc"] = desc[1]
        locale["default"][f"story.quest.{key}.hint"] = hint[0]
        locale["zh"][f"story.quest.{key}.hint"] = hint[1]
        quest_data[name] = "/".join([
            kind, "{{i18n:story.quest."+key+".title}}", "{{i18n:story.quest."+key+".desc}}",
            "{{i18n:story.quest."+key+".hint}}", requirement, next_id, str(reward), "-1", "false",
            "{{i18n:story.quest."+key+".reply}}"
        ])
        # Quest.questComplete owns progression. StoryChapterRuntime records its
        # completion and queues rewards; location/basic quests do not execute
        # dialogue directives placed in the ItemDelivery response field.
        locale["default"][f"story.quest.{key}.reply"] = reaction_key[0]
        locale["zh"][f"story.quest.{key}.reply"] = reaction_key[1]

    add_quest("FieldReport","ItemDelivery",("Chapter 6 · Northern field notes","第六章·北方自然笔记"),
        ("Levin can turn the verified observations into a shared field record.","莱文会把核实过的观察整理成共同的野外记录。"),
        ("Deliver the field report packet to Levin at the research station.","把野外调查记录袋交给研究站的莱文。"),
        "ArcticPassage_Levin (O)"+REPORT_ID+" 1", "ArcticPassage_StormReadiness", 120,
        ("These are careful observations. I'll add them to the coast record.","记录很细致，我会把它们补进海岸档案。"))
    add_quest("StormReadiness","Location",("Chapter 7 · Before the first gale","第七章·第一场风雪之前"),
        ("The community house is coordinating supplies and a fresh-catch order before the next rough-weather window.","社区屋正在下一段恶劣天气到来前协调补给与鲜鱼订单。"),
        ("Meet the harbor team at the community house to open its storm-supply board.","到社区屋和港口团队会合，开启风雪补给公告板。"),
        "ArcticPassage_CommunityHouse", "ArcticPassage_StormSupplies", 80,
        ("We can prepare together before the weather changes. The community box is ready for the team's fiber order.","天气变化前，大家可以一起做好准备。社区补给箱已经开放，可交付团队所需纤维。"),
        "AddMail Current ArcticPassage_StormSuppliesUnlocked now")
    add_quest("StormSupplies","Basic",("Chapter 7 · Community storm supplies","第七章·社区风雪补给"),
        ("The harbor team needs spare fiber lashings stored at the community house before the gale.","港口团队需要在风雪前把备用纤维绑带存入社区屋。"),
        ("Accept and complete the one-time storm-supply order at the community board; donate 20 fiber to its box.","在社区公告板接下并完成一次性风雪补给单，向补给箱交20份纤维。"),
        "", "ArcticPassage_StormFish", 100,
        ("The emergency lashings are in place. Ada has opened a fresh-catch order for the harbor kitchen.","应急绑带已经备好。艾达已为港口厨房开放鲜鱼订单。"))
    add_quest("StormFish","Basic",("Chapter 7 · Fresh catch for the gale","第七章·风雪前的鲜鱼订单"),
        ("Ada needs a fresh northern fish for the community kitchen. Only a catch made after taking the order counts.","艾达需要一条北方鲜鱼送到社区厨房；只有接单后实际钓获的鱼才计入。"),
        ("Accept the emergency fish order, then make one real northern rod catch.","接下紧急鱼单，再用钓竿实际钓获一条北方鱼。"),
        "", "ArcticPassage_StormRoute", 140,
        ("The fresh catch is recorded. Mira will walk the marked route with you before the next departure.","鲜鱼订单已经完成记录。下一次出发前，米拉会和你一起检查标记路线。"))
    add_quest("StormRoute","Basic",("Chapter 7 · Walk the safe route","第七章·确认安全路线"),
        ("Mira is waiting on the tundra edge to check the wind markers and the clear return path.","米拉正在苔原边缘等你，一起检查风向标和畅通的返程路线。"),
        ("Speak to Mira on the tundra trail, normally between 11:00 and 15:00, to confirm the marked return route.","在苔原步道与米拉交谈，确认标记返程路线；她通常在11点至15点巡查这里。"),
        "", "ArcticPassage_CampVisit", 180,
        ("The route is marked and the return path stays open. Please turn back if visibility drops.","路线已经标记，返程步道始终开放。能见度下降时请及时折返。"),
        "AddMail Current "+ROUTE_REWARD_MAIL+" now")
    add_quest("CampVisit","Location",("Chapter 8 · The winter field camp","第八章·冬季野外营地"),
        ("Visit the field camp with Mira. In winter use the dog team; marked walking returns stay open.","和米拉前往野外营地。冬季可乘犬队，标记步行返程始终开放。"),
        ("Reach the ArcticPassage field camp and read the shelter and ice-safety signs.","抵达北境营地，查看雪屋与冰面安全说明。"),
        "ArcticPassage_WinterCamp", "ArcticPassage_ShelterLesson", 160,
        ("The camp is ready for a quiet visit. The marked ice hole is only fished from its timber platform.","营地已经准备好供人安静参观。固定冰洞只能站在木平台上垂钓。"))
    add_quest("ShelterLesson","Basic",("Chapter 8 · Fit the snow blocks","第八章·搭接雪块模型"),
        ("Use Amma's winter camp model to learn the offset courses used by a snow shelter.","在阿玛的冬季营地操作雪屋模型，学习雪块错缝搭接。"),
        ("Complete all three courses at the snow-house model in the winter field camp.","在冬季野外营地的雪屋模型前完成三层搭接。"),
        "", "ArcticPassage_IceCatch", 90,
        ("The courses are stable and the entrance stays clear. When the marked fjord opening is prepared, fish only from its timber deck.","三层搭接稳固，入口也保持畅通。峡湾标记冰洞开放后，请只在木平台上垂钓。"))
    add_quest("IceCatch","Basic",("Chapter 8 · Fish from the marked ice opening","第八章·在标记冰洞垂钓"),
        ("The camp lesson is complete. On a winter day, clear the surveyed opening beside the fjord platform and make one real rod catch there.","营地课程已经完成。冬日请先清理峡湾平台旁的勘察冰洞，再用钓竿实际钓获一条鱼。"),
        ("Make one ordinary rod catch in the open ice hole at the Icefjord; stay on the timber platform.","站在木平台上，在峡湾开放冰洞中用普通钓竿实际钓获一条鱼。"),
        "", "ArcticPassage_MultiWaterCatch", 180,
        ("A careful lesson and a real catch make a good winter record. Amma has sent you a small snow-house study model.","认真完成课程并实地钓获，才算留下完整的冬日记录。阿玛寄来了一件雪屋研究模型。"),
        "AddMail Current "+ICE_REWARD_MAIL+" now")
    add_quest("MultiWaterCatch","Basic",("Chapter 9 · Two waters, one harbor","第九章·来自两处水域的鱼获"),
        ("The new buyer wants to understand the coast and inland waters before opening the longer route.","新买家想先了解近岸与内陆水域的鱼情，再开通长期航次。"),
        ("Catch and keep one rod fish in each of two different waters: harbor, Icefjord, or tundra stream.","在渔港、冰山峡湾、苔原溪流中任选两处不同水域，各用钓竿实际钓获并收下一条鱼。"),
        "", "ArcticPassage_DriedOrder", 160,
        ("Two waters are now represented. Prepare a dried fish for the first export trade.","两处水域的鱼情都有了记录。请准备一份风干鱼，完成首次出口交易。"))
    add_quest("DriedOrder","Basic",("Chapter 9 · A farther harbor order","第九章·更远的港口订单"),
        ("Air-dry a cod or capelin at the harbor rack, then make the first export trade at Ada's order counter.","用港口晾鱼架风干一条鳕鱼或毛鳞鱼，再到艾达的订单柜台完成首次出口交易。"),
        ("Trade one air-dried Atlantic cod, polar cod, or capelin for the first export receipt at the order counter.","在订单柜台用一份风干大西洋鳕鱼、北极鳕或毛鳞鱼换取首次出口回执。"),
        "", "ArcticPassage_FinalePreparation", 320,
        ("The export route is working. Daily processed-fish trades and the weekly export order are now open.","出口航线已经运转。加工鱼日单与每周出口订单现已开放。"),
        "AddMail Current "+FINALE_MAIL+" now")
    add_quest("FinalePreparation","ItemDelivery",("Chapter 10 · Posts for the lanterns","第十章·为灯火立起木杆"),
        ("Nora is preparing the harbor team's lantern gathering. The celebration can take place without waiting for the annual festival.","诺拉正在准备港口团队的灯火小聚，不必等待年度节日。"),
        ("Bring 10 wood to Nora for the lantern posts.","交给诺拉10份木材，用来准备提灯木杆。"),
        "ArcticPassage_Nora (O)388 10", "ArcticPassage_WarmHarbor", 120,
        ("The lantern posts are ready. Come into town between 18:00 and midnight for our winter-night tableau.","提灯木杆准备好了。傍晚18点至午夜之间进镇，和大家一起看一段冬夜灯火。"))
    add_quest("WarmHarbor","Basic",("Chapter 10 · A new season","第十章·霜灯港的新季节"),
        ("The team is gathering to remember the winter harbor in a lantern-lit tableau. Your actual game date and season are preserved.","大家聚在提灯下，用一段冬夜场景回望港口的故事。游戏实际日期和季节照常保留。"),
        ("Enter the town between 18:00 and midnight to join the six residents' lantern finale.","18点至午夜之间进入小镇，参加六位居民的灯火结尾。"),
        "", "-1", 500,
        ("We made it through the season together. Tomorrow the boats, field notes, and daily work continue.","我们一起走过了这个季节。明天，船只、野外笔记和日常工作仍会继续。"))
    patch("EditData", "Data/Quests", Entries=quest_data)
    patch("EditData", "Characters/Dialogue/ArcticPassage_Mira", Entries={"ArcticPassage_StormRoute":"{{i18n:story.routeConfirm}}"})
    patch("Load", "Maps/ArcticPassage_FinaleWinter", FromFile="assets/maps/Town_winter.tmx")
    actors = "farmer 29 23 0 ArcticPassage_Nora 30 23 2 ArcticPassage_Roan 32 24 0 ArcticPassage_Ada 33 23 2 ArcticPassage_Mira 31 24 0 ArcticPassage_Levin 35 23 2 ArcticPassage_Amma 34 24 0"
    scene = "continue/30 23/"+actors+"/skippable/changeToTemporaryMap ArcticPassage_FinaleWinter/viewport 30 23/pause 700"
    for npc,key in [("Nora","nora"),("Roan","roan"),("Ada","ada"),("Mira","mira"),("Levin","levin"),("Amma","amma"),("Nora","end")]:
        scene += '/speak ArcticPassage_'+npc+' "{{i18n:story.finale.'+key+'}}"/pause 200'
    scene += "/pause 800/end"
    patch("EditData", "Data/Events/ArcticPassage_Town", Entries={
        "ArcticPassage_HarborHomecoming/m ArcticPassage_FinaleReady/t 1800 2400":scene
    })

    patch("EditData", "Data/mail", Entries={
        REPORT_MAIL:"{{i18n:story.mail.field}}",
        FINALE_MAIL:"{{i18n:story.mail.finale}}",
        ICE_REWARD_MAIL:"{{i18n:story.mail.iceModel}}",
        ROUTE_REWARD_MAIL:"{{i18n:story.mail.windbreak}}",
    })
    # First trade and the permanent buyer upgrade reuse Ada's existing counter.
    # Every offer is guarded by a shared saved receipt flag, including stale menus.
    for change in content["Changes"]:
        shop = change.get("Entries", {}).get("ArcticPassage_Orders") if change.get("Target") == "Data/Shops" else None
        if not shop:
            continue
        shop["Items"] = [item for item in shop["Items"] if not item.get("Id", "").startswith(("StoryExport_", "LongExport_"))]
        for fish,pay in [("AtlanticCod",250),("PolarCod",180),("Capelin",140)]:
            for first in (True,False):
                flag = "ArcticPassage_PortTradeComplete" if first else "ArcticPassage_Order_Export_{{Year}}_{{Season}}_{{Day}}"
                condition = ("PLAYER_HAS_MAIL Current ArcticPassage_PortOrderUnlocked, !PLAYER_HAS_MAIL Current ArcticPassage_PortTradeComplete" if first else
                             "PLAYER_HAS_MAIL Current ArcticPassage_PortTradeComplete, !PLAYER_HAS_MAIL Current " + flag)
                shop["Items"].append({"Id":("StoryExport_" if first else "LongExport_")+fish,
                    "ItemId":"(O)ArcticPassage_"+("PortTradeReceipt" if first else "ExportReceipt"),
                    "Condition":condition,"TradeItemId":"(O)ArcticPassage_Dried"+fish,"TradeItemAmount":1,
                    "Price":0,"AvailableStock":1,"AvailableStockLimit":"Player",
                    "ActionsOnPurchase":["AddMoney "+str(pay),"AddMail Current "+flag+" received"]})
    patch("EditData", "Data/SpecialOrders", Entries={"ArcticPassage_ExportBoxes":{
        "Name":"{{i18n:story.export.name}}","Requester":"ArcticPassage_Ada","Duration":"Week","Repeatable":True,
        "Condition":"PLAYER_HAS_MAIL Current ArcticPassage_PortTradeComplete","OrderType":"ArcticPassage_Weekly",
        "Text":"{{i18n:story.export.desc}}",
        "Objectives":[{"Type":"Donate","Text":"{{i18n:story.export.objective}}","RequiredCount":"4",
            "Data":{"AcceptedContextTags":"arcticpassage_fish_product","DropBox":"ArcticPassage_FishCrate",
                    "DropBoxGameLocation":"ArcticPassage_CommunityHouse","DropBoxIndicatorLocation":"3 5","MinimumCapacity":"9"}}],
        "Rewards":[{"Type":"Money","Data":{"Amount":"750"}}]
    }})
    path.write_text(json.dumps(content, ensure_ascii=False, indent=2)+"\n")
    for lang in locale:
        (PACK / f"i18n/{lang}.json").write_text(json.dumps(locale[lang], ensure_ascii=False, indent=2)+"\n")
    print("Connected chapters 6–10; the year-round town epilogue follows the fish order without requiring festival attendance.")

if __name__ == "__main__":
    main()
