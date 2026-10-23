using StardewModdingAPI;
using StardewModdingAPI.Events;
using StardewValley;
using StardewValley.Menus;

namespace ArcticPassage.Runtime;

/// <summary>Explicit keyboard advance for this pack's own local plain notices.</summary>
internal sealed class KeyboardNotices
{
    private readonly IModHelper helper;
    private readonly IMonitor monitor;
    private static readonly Dictionary<string, string[]> Keys = new()
    {
        ["ArcticPassage_Town"] = ["TownGuide", "InnGuide"],
        ["ArcticPassage_Harbor"] = ["BoatLocked", "Fishing", "Workshop", "WorkshopReady"],
        ["ArcticPassage_Icefjord"] = ["DeepWater", "WhaleNote"],
        ["ArcticPassage_Tundra"] = ["TundraGuide", "Char", "Safety"],
        ["ArcticPassage_Guesthouse"] = ["Lodging"],
        ["ArcticPassage_WinterCamp"] = ["CampRoute", "SnowShelter"],
        ["ArcticPassage_ResearchStation"] = ["CampDesk"],
        ["ArcticPassage_Airstrip"] = ["Airport"],
        ["ArcticPassage_SledTrail"] = ["SledRoute", "SledPending"],
        ["ArcticPassage_Glacier"] = ["GlacierSafety", "Geology"],
        ["ArcticPassage_CommunityHouse"] = ["Community"]
    };

    internal KeyboardNotices(IModHelper helper, IMonitor monitor)
    {
        this.helper = helper; this.monitor = monitor;
        helper.Events.Input.ButtonPressed += OnButton;
    }

    private void OnButton(object? sender, ButtonPressedEventArgs e)
    {
        if (e.Button != SButton.Enter || e.IsSuppressed() || !Context.IsWorldReady || Game1.eventUp
            || !Keys.TryGetValue(Game1.currentLocation.Name, out var keys)
            || Game1.activeClickableMenu is not DialogueBox box || box.isQuestion || box.characterDialogue != null) return;
        string page = box.getCurrentString();
        if (string.IsNullOrWhiteSpace(page) || !keys.Any(key =>
            Game1.content.LoadString("Strings\\StringsFromMaps:ArcticPassage_" + key).Contains(page, StringComparison.Ordinal))) return;
        helper.Input.Suppress(e.Button);
        // Use native page/typing/safety/outro handling. Never force-close a
        // question, NPC conversation, vanilla dialogue, or another mod's text.
        box.receiveLeftClick(0, 0, true);
        monitor.Log("NOTICE native keyboard advance " + Game1.currentLocation.Name, LogLevel.Trace);
    }
}
