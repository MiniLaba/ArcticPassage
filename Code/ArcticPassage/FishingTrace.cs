using StardewModdingAPI;
using StardewValley;
using StardewValley.Tools;

namespace ArcticPassage.Runtime;

/// <summary>Read-only trace of native fishing for support and reproducible play records.</summary>
internal sealed class FishingTrace
{
    private string previous = "";
    internal FishingTrace(IModHelper helper, IMonitor monitor)
    {
        bool Local() => Context.IsWorldReady && Game1.currentLocation.Name is
            "ArcticPassage_Harbor" or "ArcticPassage_Icefjord" or "ArcticPassage_Tundra";
        helper.Events.Input.ButtonPressed += (_, e) =>
        {
            if (!Local() || e.Button is not (SButton.C or SButton.MouseLeft) || Game1.player.CurrentTool is not FishingRod rod) return;
            monitor.Log($"FISHING input {e.Button} suppressed={e.IsSuppressed()} fishing={rod.isFishing} nibble={rod.isNibbling} menu={Game1.activeClickableMenu?.GetType().Name ?? "none"}", LogLevel.Trace);
        };
        helper.Events.GameLoop.UpdateTicked += (_, e) =>
        {
            if (!e.IsMultipleOf(6) || !Local() || Game1.player.CurrentTool is not FishingRod rod) return;
            string state = $"fishing={rod.isFishing} nibble={rod.isNibbling} hit={rod.hit} reeling={rod.isReeling} caught={rod.fishCaught} pull={rod.pullingOutOfWater} timing={rod.isTimingCast} inAir={rod.castedButBobberStillInAir}";
            if (state == previous) return;
            previous = state;
            monitor.Log($"FISHING native {state} tile={Game1.player.Tile} facing={Game1.player.FacingDirection} power={rod.castingPower:0.00}", LogLevel.Trace);
        };
        helper.Events.Display.MenuChanged += (_, e) =>
        {
            if (Local() && Game1.player.CurrentTool is FishingRod)
                monitor.Log($"FISHING native menu {e.OldMenu?.GetType().Name} -> {e.NewMenu?.GetType().Name}", LogLevel.Trace);
        };
        helper.Events.Player.InventoryChanged += (_, e) =>
        {
            if (!e.IsLocalPlayer || !Local()) return;
            foreach (var item in e.Added.Where(i => i.ItemId.StartsWith("ArcticPassage_")))
                monitor.Log($"FISHING inventory added {item.QualifiedItemId} x{item.Stack}; native recorded species={Game1.player.fishCaught.Length}", LogLevel.Trace);
        };
        helper.Events.GameLoop.ReturnedToTitle += (_, _) => previous = "";
    }
}
