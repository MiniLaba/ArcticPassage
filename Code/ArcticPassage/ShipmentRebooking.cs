using StardewModdingAPI;
using StardewValley;
using StardewValley.Quests;

namespace ArcticPassage.Runtime;

/// <summary>Optional replacement of an out-of-season, unfulfilled first order.</summary>
internal static class ShipmentRebooking
{
    private const string Prefix = "ArcticPassage_FirstCatch_";
    private static readonly Dictionary<string, string> Fish = new()
    {
        ["spring"] = "Capelin", ["summer"] = "Capelin",
        ["fall"] = "AtlanticCod", ["winter"] = "PolarCod"
    };
    private static readonly Dictionary<string, string[]> Seasons = new()
    {
        ["Capelin"] = ["spring", "summer"], ["AtlanticCod"] = ["summer", "fall"],
        ["PolarCod"] = ["winter", "spring"]
    };
    internal static string SeasonalFish => Fish.GetValueOrDefault(Game1.currentSeason, "Capelin");

    private static ItemDeliveryQuest? Pending()
    {
        if (!Context.IsWorldReady || !Game1.currentLocation.Name.StartsWith("ArcticPassage_")
            || Game1.eventUp || !Fish.ContainsKey(Game1.currentSeason)) return null;
        var family = Game1.player.questLog.Where(q => q.id.Value.StartsWith(Prefix)).ToArray();
        // Fail closed on duplicate or already completed orders, including
        // completed orders whose native journal reward hasn't been collected.
        if (family.Length != 1 || family[0] is not ItemDeliveryQuest q || q.completed.Value || q.destroy.Value) return null;
        string season = q.id.Value[Prefix.Length..];
        if (!Fish.TryGetValue(season, out string? fish) || Seasons[fish].Contains(Game1.currentSeason)) return null;
        if (!Standard(q, fish) || Game1.player.questLog.Any(other =>
            other.id.Value is "ArcticPassage_Shed" or "ArcticPassage_BoatRepair" or "ArcticPassage_FjordVisit" or "ArcticPassage_DeepCatch")
            || Game1.player.mailReceived.Contains("ArcticPassage_WoodDelivered")
            || Game1.player.mailReceived.Contains("ArcticPassage_Shed")) return null;
        return q;
    }

    private static bool Standard(ItemDeliveryQuest q, string fish)
        => q.target.Value == "ArcticPassage_Ada" && q.ItemId.Value == "(O)ArcticPassage_" + fish
            && q.number.Value == 3 && q.moneyReward.Value == 400 && !q.dailyQuest.Value
            && !q.canBeCancelled.Value && q.nextQuests.SequenceEqual(["ArcticPassage_Shed"]);

    internal static bool CanChange() => Pending() != null;

    internal static string Change(IMonitor monitor)
    {
        ItemDeliveryQuest? old = Pending();
        if (old == null) return "changeUnavailable";
        string id = Prefix + Game1.currentSeason;
        if (Quest.getQuestFromId(id) is not ItemDeliveryQuest replacement || !Standard(replacement, SeasonalFish))
            return "changeFailed";
        // Construct and validate the full native replacement before touching
        // the log. Replace exactly one slot, leaving money/items/other quests
        // and completed rewards untouched. No questComplete/reward call here.
        replacement.accepted.Value = old.accepted.Value;
        replacement.dayQuestAccepted.Value = old.dayQuestAccepted.Value;
        replacement.daysLeft.Value = old.daysLeft.Value;
        foreach (var pair in old.modData.Pairs) replacement.modData[pair.Key] = pair.Value;
        replacement.modData["WhiteBay.ArcticPassage/RebookedFrom"] = old.id.Value;
        int index = Game1.player.questLog.IndexOf(old);
        if (index < 0) return "changeUnavailable";
        Game1.player.questLog[index] = replacement;
        monitor.Log($"SHIPMENT REBOOK {old.id.Value} -> {id}; native order, 3 fish, 400 reward, no inventory or wallet change", LogLevel.Info);
        return "changed";
    }
}
