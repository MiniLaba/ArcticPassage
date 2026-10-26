using HarmonyLib;
using StardewModdingAPI;
using StardewValley;
using StardewValley.Quests;
using StardewValley.Tools;

namespace ArcticPassage.Runtime;

/// <summary>Connects native community orders and authored camp interactions to the chapter quests.</summary>
internal sealed class StoryChapterRuntime
{
    private const string ShelterQuest = "ArcticPassage_ShelterLesson";
    private const string IceCatchQuest = "ArcticPassage_IceCatch";
    private const string WaterCatchPrefix = "WhiteBay.ArcticPassage/Chapter9Catch/";
    private const string RouteFriendshipKey = "WhiteBay.ArcticPassage/Chapter7MiraThanks";
    private const string CompletedPrefix = "WhiteBay.ArcticPassage/QuestComplete/";
    internal const string FinaleEvent = "ArcticPassage_HarborHomecoming";
    internal static bool FinaleActive => Context.IsWorldReady && Game1.currentLocation?.currentEvent?.id == FinaleEvent;
    private static StoryChapterRuntime? instance;
    private static readonly System.Reflection.MethodInfo BobberTile = AccessTools.Method(typeof(FishingRod), "calculateBobberTile");
    private sealed record CatchReceipt(string Item, string Location, int Day, bool IceHole);
    private CatchReceipt? pendingCatch;
    private readonly IMonitor monitor;

    internal StoryChapterRuntime(IModHelper helper, IMonitor monitor, Harmony harmony)
    {
        this.monitor = monitor;
        instance = this;
        harmony.Patch(AccessTools.Method(typeof(Quest), nameof(Quest.questComplete)),
            postfix: new HarmonyMethod(typeof(StoryChapterRuntime), nameof(QuestCompleted)));
        harmony.Patch(AccessTools.Method(typeof(Farmer), nameof(Farmer.caughtFish)),
            postfix: new HarmonyMethod(typeof(StoryChapterRuntime), nameof(FishCaught)));
        harmony.Patch(AccessTools.Method(typeof(NPC), nameof(NPC.checkAction)),
            prefix: new HarmonyMethod(typeof(StoryChapterRuntime), nameof(MiraInteraction)));
        helper.Events.GameLoop.SaveLoaded += (_, _) => { MigrateStoryQuests(); Check(); };
        helper.Events.GameLoop.UpdateTicked += (_, e) => { if (e.IsMultipleOf(30)) Check(); };
        helper.Events.Player.InventoryChanged += (_, e) => OnInventoryChanged(e);
        helper.Events.Player.Warped += (_, e) => { if (e.IsLocalPlayer) pendingCatch = null; };
        helper.Events.GameLoop.DayStarted += (_, _) => pendingCatch = null;
        helper.Events.GameLoop.ReturnedToTitle += (_, _) => pendingCatch = null;
    }

    private static Quest? Active(string id)
        => Context.IsWorldReady
            ? Game1.player.questLog.OfType<Quest>().FirstOrDefault(q => q.id.Value == id && !q.completed.Value)
            : null;

    internal static bool WasCompleted(string id) => Context.IsWorldReady
        && (Game1.player.modData.ContainsKey(CompletedPrefix + id)
            || Game1.player.questLog.Any(q => q.id.Value == id && q.completed.Value));

    private static void QuestCompleted(Quest __instance)
    {
        if (!Context.IsWorldReady || !Context.IsMainPlayer || !__instance.completed.Value
            || !__instance.id.Value.StartsWith("ArcticPassage_", StringComparison.Ordinal)) return;
        instance?.RecordCompletion(__instance.id.Value);
    }

    private void QueueMail(string mail)
    {
        if (!Game1.player.mailReceived.Contains(mail) && !Game1.player.mailbox.Contains(mail)
            && !Game1.player.mailForTomorrow.Contains(mail)) Game1.player.mailbox.Add(mail);
    }

    private void RecordCompletion(string id)
    {
        if (!Game1.player.modData.ContainsKey(CompletedPrefix + id))
            Game1.player.modData[CompletedPrefix + id] = Game1.Date.TotalDays.ToString(System.Globalization.CultureInfo.InvariantCulture);
        switch (id)
        {
            case "ArcticPassage_StormReadiness":
                Game1.player.mailReceived.Add("ArcticPassage_StormSuppliesUnlocked");
                break;
            case "ArcticPassage_StormSupplies":
                Game1.player.mailReceived.Add("ArcticPassage_StormSuppliesComplete");
                Game1.player.mailReceived.Add("ArcticPassage_StormFishUnlocked");
                break;
            case "ArcticPassage_StormFish":
                Game1.player.mailReceived.Add("ArcticPassage_StormFishComplete");
                Game1.player.mailReceived.Add("ArcticPassage_StormRouteUnlocked");
                break;
            case "ArcticPassage_StormRoute": QueueMail("ArcticPassage_StormRouteReward"); break;
            case "ArcticPassage_IceCatch": QueueMail("ArcticPassage_IceLessonReward"); break;
            case "ArcticPassage_MultiWaterCatch": Game1.player.mailReceived.Add("ArcticPassage_PortOrderUnlocked"); break;
            case "ArcticPassage_DriedOrder": QueueMail("ArcticPassage_Chapter10Letter"); break;
            case "ArcticPassage_FinalePreparation": Game1.player.mailReceived.Add("ArcticPassage_FinaleReady"); break;
        }
    }

    private void Check()
    {
        if (!Context.IsWorldReady || !Context.IsMainPlayer) return;
        foreach (var quest in Game1.player.questLog.Where(q => q.completed.Value
            && q.id.Value.StartsWith("ArcticPassage_", StringComparison.Ordinal)).ToArray())
            RecordCompletion(quest.id.Value);
        CompleteOrderStep("StormSupplies", "ArcticPassage_StormSupplies",
            "ArcticPassage_StormSuppliesComplete", "ArcticPassage_StormFishUnlocked");
        CompleteOrderStep("StormFish", "ArcticPassage_StormFish",
            "ArcticPassage_StormFishComplete", "ArcticPassage_StormRouteUnlocked");
        if (Active("ArcticPassage_DriedOrder") is { } trade && Game1.player.mailReceived.Contains("ArcticPassage_PortTradeComplete"))
            Game1.player.completeQuest(trade.id.Value);
        if (Active("ArcticPassage_WarmHarbor") is { } finale && Game1.player.eventsSeen.Contains(FinaleEvent))
            Game1.player.completeQuest(finale.id.Value);

        if (WasCompleted("ArcticPassage_StormRoute")
            && !Game1.player.modData.ContainsKey(RouteFriendshipKey))
        {
            if (!Game1.player.friendshipData.TryGetValue("ArcticPassage_Mira", out Friendship? friendship))
            {
                friendship = new Friendship(0);
                Game1.player.friendshipData["ArcticPassage_Mira"] = friendship;
            }
            friendship.Points = Math.Min(2500, friendship.Points + 150);
            Game1.player.modData[RouteFriendshipKey] = Game1.Date.TotalDays.ToString(System.Globalization.CultureInfo.InvariantCulture);
            monitor.Log("STORY chapter 7: route confirmation awarded one-time Mira friendship; native relationship save retained", LogLevel.Info);
        }

        if (Active(ShelterQuest) is { } shelter
            && Game1.player.modData.ContainsKey(SnowShelterLesson.RecordKey))
        {
            Game1.player.completeQuest(shelter.id.Value);
            monitor.Log("STORY chapter 8: completed the native snow-block lesson quest from the saved shelter model record", LogLevel.Info);
        }

    }

    private void MigrateStoryQuests()
    {
        if (!Context.IsWorldReady || !Context.IsMainPlayer) return;
        string[] ids = ["DeepCatch", "FieldReport", "StormReadiness", "StormSupplies", "StormFish", "StormRoute",
            "CampVisit", "ShelterLesson", "IceCatch", "MultiWaterCatch", "DriedOrder", "FinalePreparation", "WarmHarbor"];
        for (int index = 0; index < Game1.player.questLog.Count; index++)
        {
            var old = Game1.player.questLog[index];
            if (old.completed.Value || !ids.Any(id => old.id.Value == "ArcticPassage_" + id)) continue;
            Quest fresh = Quest.getQuestFromId(old.id.Value);
            if (fresh == null) continue;
            fresh.accepted.Value = old.accepted.Value;
            fresh.dayQuestAccepted.Value = old.dayQuestAccepted.Value;
            foreach (var field in old.modData.Pairs) fresh.modData[field.Key] = field.Value;
            // Only unpaid, unfinished story entries are refreshed. Inventory,
            // money, completion receipts and unrelated quests are untouched.
            Game1.player.questLog[index] = fresh;
        }
        // A later active chapter is native evidence that its predecessor ended.
        if (Active("ArcticPassage_FieldReport") != null) RecordCompletion("ArcticPassage_DeepCatch");
        // Old versions had a terminal DeepCatch. It can still be in the log
        // awaiting its original reward, with no successor added by the engine.
        // Recover only from a completed native quest or our saved receipt.
        foreach (var quest in Game1.player.questLog.Where(q => q.completed.Value
            && q.id.Value.StartsWith(HarborProgress.Prefix, StringComparison.Ordinal)).ToArray())
            RecordCompletion(quest.id.Value);
        var complete = HarborProgress.Chapters.Where(id => WasCompleted(HarborProgress.Prefix + id)).ToHashSet();
        var present = Game1.player.questLog.Where(q => q.id.Value.StartsWith(HarborProgress.Prefix, StringComparison.Ordinal))
            .Select(q => q.id.Value[HarborProgress.Prefix.Length..]).ToHashSet();
        if (HarborProgress.MissingChapterSuccessor(complete, present) is { } next)
        {
            Game1.player.addQuest(HarborProgress.Prefix + next);
            monitor.Log($"STORY recovered missing successor {next} from native completion evidence; original reward left untouched", LogLevel.Info);
        }
    }

    private static bool MiraInteraction(NPC __instance, Farmer __0, GameLocation __1, ref bool __result)
    {
        if (!Context.IsWorldReady || !Context.IsMainPlayer || __0 != Game1.player || Game1.eventUp
            || __instance.Name != "ArcticPassage_Mira" || __1.Name != "ArcticPassage_Tundra"
            || Active("ArcticPassage_StormRoute") == null) return true;
        var lines = Game1.content.Load<Dictionary<string, string>>("Characters/Dialogue/ArcticPassage_Mira");
        Game1.DrawDialogue(__instance, lines["ArcticPassage_StormRoute"]);
        Game1.player.completeQuest("ArcticPassage_StormRoute");
        __result = true;
        return false;
    }

    private void CompleteOrderStep(string questId, string orderId, string completeMail, string nextUnlockMail)
    {
        if (!Game1.player.team.completedSpecialOrders.Contains(orderId)) return;
        if (Active("ArcticPassage_" + questId) is not { } quest) return;
        Game1.player.mailReceived.Add(completeMail);
        Game1.player.mailReceived.Add(nextUnlockMail);
        Game1.player.team.acceptedSpecialOrderTypes.Remove(WeeklyOrders.StoryBoardType);
        Game1.player.completeQuest(quest.id.Value);
        monitor.Log($"STORY chapter 7: native order {orderId} completed; next quest unlocked without granting order progress", LogLevel.Info);
    }

    private static void FishCaught(Farmer __instance, string __0, bool __2)
    {
        if (instance == null || !Context.IsWorldReady || !Context.IsMainPlayer || __instance != Game1.player
            || __2 || __instance.CurrentTool is not FishingRod rod) return;
        string item = __0.StartsWith("(O)", StringComparison.Ordinal) ? __0 : "(O)" + __0;
        if (!item.StartsWith("(O)ArcticPassage_", StringComparison.Ordinal)) return;
        var tile = (Microsoft.Xna.Framework.Vector2)BobberTile.Invoke(rod, null)!;
        bool ice = __instance.currentLocation.Name == IceFishing.Location && IceFishing.IsOpen
            && IceFishing.Opening.Contains((int)tile.X, (int)tile.Y);
        instance.pendingCatch = new(item, __instance.currentLocation.Name, Game1.Date.TotalDays, ice);
    }

    private void OnInventoryChanged(StardewModdingAPI.Events.InventoryChangedEventArgs e)
    {
        if (!e.IsLocalPlayer || !Context.IsWorldReady || !Context.IsMainPlayer || pendingCatch is not { } receipt
            || receipt.Day != Game1.Date.TotalDays || receipt.Location != Game1.currentLocation.Name) return;
        var added = e.Added.Concat(e.QuantityChanged.Where(change => change.NewSize > change.OldSize).Select(change => change.Item));
        if (!added.Any(item => item.QualifiedItemId == receipt.Item)) return;
        pendingCatch = null;
        if (receipt.IceHole && Active(IceCatchQuest) is { } quest)
        {
            Game1.player.completeQuest(quest.id.Value);
            monitor.Log("STORY chapter 8: native catch from the exact opened ice-hole bobber tile entered inventory; fish retained", LogLevel.Info);
        }
        if (Active("ArcticPassage_MultiWaterCatch") != null
            && receipt.Location is "ArcticPassage_Harbor" or "ArcticPassage_Icefjord" or "ArcticPassage_Tundra")
        {
            Game1.player.modData[WaterCatchPrefix + receipt.Location] = receipt.Day + "|" + receipt.Item;
            if (Game1.player.modData.Keys.Count(key => key.StartsWith(WaterCatchPrefix, StringComparison.Ordinal)) >= 2)
                Game1.player.completeQuest("ArcticPassage_MultiWaterCatch");
        }
    }
}
