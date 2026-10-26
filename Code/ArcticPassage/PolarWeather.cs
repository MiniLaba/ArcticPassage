using Microsoft.Xna.Framework;
using Microsoft.Xna.Framework.Graphics;
using StardewModdingAPI;
using StardewModdingAPI.Events;
using StardewValley;

namespace ArcticPassage.Runtime;

/// <summary>Forecasts and travel safeguards for the custom coast and winter trail.</summary>
internal sealed class PolarWeather
{
    private static readonly HashSet<string> ExteriorMaps =
    [
        "ArcticPassage_Town", "ArcticPassage_Harbor", "ArcticPassage_Icefjord", "ArcticPassage_Tundra",
        "ArcticPassage_WinterCamp", "ArcticPassage_Airstrip", "ArcticPassage_SledTrail", "ArcticPassage_Glacier"
    ];

    private readonly IModHelper helper;
    private readonly IMonitor monitor;
    private int gustPhase;

    internal static PolarCondition Today => PolarForecast.ForDate(Game1.year, Game1.currentSeason, Game1.dayOfMonth);

    internal PolarWeather(IModHelper helper, IMonitor monitor)
    {
        this.helper = helper;
        this.monitor = monitor;
        GameLocation.RegisterTileAction("ArcticPassageFjordOutbound", Outbound);
        GameLocation.RegisterTileAction("ArcticPassageFjordReturn", Return);
        helper.Events.GameLoop.UpdateTicked += (_, _) => gustPhase = (gustPhase + 2) % 4096;
        helper.Events.Display.RenderedWorld += DrawGusts;
    }

    private bool Outbound(GameLocation location, string[] args, Farmer who, Point tile)
    {
        if (who != Game1.player || location.Name != "ArcticPassage_Harbor" || tile != new Point(43, 24)) return false;
        if (!who.mailReceived.Contains("ArcticPassage_Boat"))
        {
            Game1.drawObjectDialogue(helper.Translation.Get("weather.boatLocked"));
            return true;
        }
        PolarCondition condition = Today;
        if (PolarForecast.BlocksFjordDeparture(condition))
        {
            Game1.drawObjectDialogue(helper.Translation.Get("weather.fjordClosed"));
            monitor.Log($"WEATHER safe hold: fjord departure suspended for {condition}; no time or inventory changed", LogLevel.Info);
            return true;
        }
        Game1.warpFarmer("ArcticPassage_Icefjord", 35, 34, false);
        monitor.Log("WEATHER fjord departure allowed under calm conditions", LogLevel.Trace);
        return true;
    }

    private bool Return(GameLocation location, string[] args, Farmer who, Point tile)
    {
        if (who != Game1.player || location.Name != "ArcticPassage_Icefjord" || tile != new Point(8, 28)) return false;
        // The landing post always returns the player safely, even during a gale.
        Game1.warpFarmer("ArcticPassage_Harbor", 42, 24, false);
        monitor.Log("WEATHER safe return allowed from fjord under all conditions", LogLevel.Trace);
        return true;
    }

    private void DrawGusts(object? sender, RenderedWorldEventArgs e)
    {
        if (!Context.IsWorldReady || !ExteriorMaps.Contains(Game1.currentLocation.Name)) return;
        PolarCondition condition = Today;
        if (condition == PolarCondition.Calm) return;

        int width = Game1.viewport.Width;
        int height = Game1.viewport.Height;
        int count = condition == PolarCondition.Blizzard ? 42 : 18;
        int length = condition == PolarCondition.Blizzard ? 22 : 15;
        Color color = condition == PolarCondition.Blizzard ? new Color(226, 242, 245) * 0.28f : new Color(195, 218, 224) * 0.18f;
        for (int i = 0; i < count; i++)
        {
            int y = (i * 67 + gustPhase * (condition == PolarCondition.Blizzard ? 2 : 1)) % Math.Max(1, height);
            int x = (i * 137 - gustPhase * 3) % Math.Max(1, width + length);
            if (x < 0) x += width + length;
            e.SpriteBatch.Draw(Game1.staminaRect, new Vector2(x - length, y), null, color,
                -0.12f, Vector2.Zero, new Vector2(length, condition == PolarCondition.Blizzard ? 2 : 1),
                SpriteEffects.None, 0.99f);
        }
    }
}
