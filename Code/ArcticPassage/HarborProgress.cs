namespace ArcticPassage.Runtime;

/// <summary>Read-only guidance for the existing harbor chain; never advances a quest or grants materials.</summary>
internal static class HarborProgress
{
    internal const string Prefix = "ArcticPassage_";
    internal static readonly string[] Chapters = ["DeepCatch", "FieldReport", "StormReadiness", "StormSupplies",
        "StormFish", "StormRoute", "CampVisit", "ShelterLesson", "IceCatch", "MultiWaterCatch",
        "DriedOrder", "FinalePreparation", "WarmHarbor"];

    internal static string? MissingChapterSuccessor(IReadOnlySet<string> completed, IReadOnlySet<string> present)
    {
        for (int i = Chapters.Length - 1; i >= 0; i--)
        {
            if (!completed.Contains(Chapters[i])) continue;
            if (i == Chapters.Length - 1 || Chapters.Skip(i + 1).Any(present.Contains)) return null;
            return Chapters[i + 1];
        }
        return null; // Wallet, fish collection and boat access cannot prove delivery.
    }

    internal static string NextStep(IEnumerable<string> activeQuests, IReadOnlySet<string> mail, bool hasReward)
    {
        // Delivery starts work tonight. The native DayStarted trigger opens the
        // facility tomorrow, even if its follow-up quest is already in the log.
        if (mail.Contains(Prefix + "IronDelivered") && !mail.Contains(Prefix + "Boat")) return "boatWait";
        if (mail.Contains(Prefix + "WoodDelivered") && !mail.Contains(Prefix + "Shed")) return "shedWait";
        foreach (string quest in activeQuests)
        {
            if (!quest.StartsWith(Prefix, StringComparison.Ordinal)) continue;
            string id = quest[Prefix.Length..];
            if (id is "Arrival" or "Shed" or "BoatRepair" or "FjordVisit" || Chapters.Contains(id)
                || id is "FirstCatch_spring" or "FirstCatch_summer" or "FirstCatch_fall" or "FirstCatch_winter") return id;
        }
        if (hasReward) return "claim";
        return mail.Contains(Prefix + "Boat") ? "free" : "start";
    }

    internal static int RemainingIronTrades(IReadOnlySet<string> mail)
        => !mail.Contains(Prefix + "Shed") || mail.Contains(Prefix + "IronDelivered") || mail.Contains(Prefix + "Boat")
            ? 0 : Enumerable.Range(1, 2).Count(n => !mail.Contains(Prefix + "LocalRepairIron_" + n));
}
