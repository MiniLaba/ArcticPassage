using StardewModdingAPI;
using StardewModdingAPI.Events;
using StardewValley;
using StardewValley.Quests;

namespace ArcticPassage.Runtime;

/// <summary>Read-only collection progress and one native-mail reward for completed fieldwork.</summary>
internal sealed class FieldResearch
{
    internal const string SamplePrefix = "WhiteBay.ArcticPassage/ResearchSample/";
    internal const string RewardMail = "ArcticPassage_ResearchDisplay";
    internal static readonly string[] Fish =
    ["Capelin", "NorthernShrimp", "PolarCod", "AtlanticCod", "ArcticChar", "SnowCrab", "Wolffish", "Halibut", "GoldenRedfish"];
    private readonly IModHelper helper;
    private readonly IMonitor monitor;

    internal FieldResearch(IModHelper helper, IMonitor monitor)
    {
        this.helper = helper;
        this.monitor = monitor;
        helper.Events.GameLoop.OneSecondUpdateTicked += (_, _) => CheckReward();
    }

    internal static int FishCount => Fish.Count(HasFishEvidence);
    internal static int AnimalCount => WildlifeSightings.All.Take(8).Count(s => WildlifeSightings.Has(s.Id));
    internal static int LandformCount => FieldGuide.Sites.Take(4).Count(s => Game1.player.modData.ContainsKey(FieldGuide.Prefix + s.Id));
    internal static int SampleCount => Context.IsWorldReady
        ? Game1.player.modData.Keys.Where(k => k.StartsWith(SamplePrefix, StringComparison.Ordinal))
            .Select(k => k[SamplePrefix.Length..].Replace("(O)", "", StringComparison.Ordinal))
            .Distinct(StringComparer.Ordinal).Count() : 0;
    internal static int PhenomenonCount => PolarPhenomena.Count;
    internal static bool Complete => Context.IsWorldReady && FishCount == Fish.Length
        && AnimalCount == 8 && LandformCount == 4 && PhenomenonCount == 4 && SampleCount >= 3;

    internal static bool HasFishEvidence(string fish)
    {
        if (!Context.IsWorldReady) return false;
        string id = "ArcticPassage_" + fish;
        if (Game1.player.modData.ContainsKey(SamplePrefix + id)
            || Game1.player.modData.ContainsKey(SamplePrefix + "(O)" + id)) return true;
        return Game1.player.fishCaught.Keys.Any(key => key == id || key == "(O)" + id
            || key.EndsWith("/" + id, StringComparison.Ordinal)
            || key.EndsWith(":" + id, StringComparison.Ordinal));
    }

    private void CheckReward()
    {
        CheckFieldReport();
        if (!Context.IsWorldReady || !Context.IsMainPlayer || !Complete
            || Game1.player.mailReceived.Contains(RewardMail) || Game1.player.mailbox.Contains(RewardMail)) return;
        Game1.player.mailbox.Add(RewardMail);
        monitor.Log($"RESEARCH complete: fish={FishCount}/{Fish.Length}, animals={AnimalCount}/8, phenomena={PhenomenonCount}/4, landforms={LandformCount}/4, samples={SampleCount}; native reward letter queued", LogLevel.Info);
    }

    private void CheckFieldReport()
    {
        const string mail = "ArcticPassage_FieldReportLetter";
        if (!Context.IsWorldReady || !Context.IsMainPlayer
            || Game1.player.mailReceived.Contains(mail) || Game1.player.mailbox.Contains(mail)
            || !StoryChapterRuntime.WasCompleted("ArcticPassage_DeepCatch")
            || AnimalCount < 3 || LandformCount < 1 || !WildlifeSightings.Has("whale")) return;
        Game1.player.mailbox.Add(mail);
        monitor.Log($"STORY chapter 6 unlocked: completed deep-water shipment and recorded {AnimalCount} animals, {LandformCount} landforms, and a distant marine sighting", LogLevel.Info);
    }
}
