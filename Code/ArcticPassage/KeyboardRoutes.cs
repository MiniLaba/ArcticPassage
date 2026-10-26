using Microsoft.Xna.Framework;
using StardewModdingAPI;
using StardewModdingAPI.Events;
using StardewValley;

namespace ArcticPassage.Runtime;

/// <summary>Use existing bay routes and service counters without positioning the mouse.</summary>
internal sealed class KeyboardRoutes
{
    internal KeyboardRoutes(IModHelper helper, IMonitor monitor)
    {
        helper.Events.Input.ButtonPressed += (_, e) =>
        {
            if (e.Button != SButton.X || e.IsSuppressed() || !Context.IsWorldReady
                || Game1.activeClickableMenu != null || Game1.eventUp || Game1.dialogueUp
                || !Game1.player.CanMove || Game1.player.UsingTool) return;
            Point origin = Game1.player.TilePoint;
            Point tile = origin + (Game1.player.FacingDirection switch
            {
                0 => new Point(0, -1), 1 => new Point(1, 0),
                2 => new Point(0, 1), _ => new Point(-1, 0)
            });
            var location = Game1.currentLocation;
            string? expected = location.Name switch
            {
                "ArcticPassage_Harbor" when tile == new Point(43, 24)
                    => "ArcticPassageFjordOutbound",
                "ArcticPassage_Icefjord" when tile == new Point(8, 28)
                    => "ArcticPassageFjordReturn",
                "ArcticPassage_Harbor" when tile == new Point(16, 21)
                    => "OpenShop ArcticPassage_Supplies",
                "ArcticPassage_Harbor" when tile == new Point(8, 21)
                    => "OpenShop ArcticPassage_Orders",
                "ArcticPassage_Fishery" when tile == new Point(8, 6)
                    => "OpenShop ArcticPassage_Market",
                "ArcticPassage_Fishery" when tile == new Point(15, 6)
                    => "OpenShop ArcticPassage_Orders",
                "ArcticPassage_Town" when tile == new Point(18, 21)
                    => "Warp 12 14 ArcticPassage_Guesthouse",
                "ArcticPassage_Town" when tile == new Point(33, 21)
                    => "Warp 12 14 ArcticPassage_Fishery",
                _ => null
            };
            if (expected == null) return;
            string? actual = location.doesTileHaveProperty(tile.X, tile.Y, "Action", "Buildings");
            monitor.Log($"ROUTE input {location.Name} tile={origin} facing={Game1.player.FacingDirection} action={actual}", LogLevel.Trace);
            // The map remains authoritative: do not turn a locked notice or a
            // different mod's replacement action into an unconditional warp.
            if (actual != expected || (expected == "ArcticPassageFjordOutbound"
                && !Game1.player.mailReceived.Contains("ArcticPassage_Boat"))) return;
            helper.Input.Suppress(e.Button);
            location.performAction(actual, Game1.player, new xTile.Dimensions.Location(tile.X, tile.Y));
        };
    }
}
