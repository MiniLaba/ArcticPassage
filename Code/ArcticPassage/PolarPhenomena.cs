using Microsoft.Xna.Framework;
using Microsoft.Xna.Framework.Graphics;
using StardewModdingAPI;
using StardewModdingAPI.Events;
using StardewValley;

namespace ArcticPassage.Runtime;

/// <summary>Four dated natural observations tied to the existing light and weather rules.</summary>
internal sealed class PolarPhenomena
{
    internal const string Prefix = "WhiteBay.ArcticPassage/FieldGuide/phenomenon_";
    internal static readonly string[] Ids = ["midnightSun", "polarNight", "aurora", "blizzard"];
    private readonly IModHelper helper;
    private readonly IMonitor monitor;

    internal PolarPhenomena(IModHelper helper, IMonitor monitor)
    {
        this.helper = helper;
        this.monitor = monitor;
        helper.Events.Display.RenderedWorld += DrawAurora;
    }

    internal static int Count => Ids.Count(Has);
    internal static bool Has(string id) => Context.IsWorldReady && Game1.player.modData.ContainsKey(Prefix + id);
    internal static bool AuroraActive => Available("aurora");

    internal static bool Available(string id)
    {
        if (!Context.IsWorldReady || Game1.currentLocation == null || !Game1.currentLocation.IsOutdoors) return false;
        string location = Game1.currentLocation.Name;
        bool lanternFestival = FestivalRuntime.CurrentFestival() == "winter";
        bool arcticOutdoor = location.StartsWith("ArcticPassage_")
            || lanternFestival;
        if (!arcticOutdoor) return false;
        int time = Game1.timeOfDay;
        switch (id)
        {
            case "midnightSun":
                return Game1.currentSeason == "summer" && time is >= 2200 and <= 2600
                    && location is "ArcticPassage_Tundra" or "ArcticPassage_Glacier"
                    && PolarPhotoperiod.At(Game1.currentSeason, Game1.dayOfMonth, time).Darkness < .30f;
            case "polarNight":
                return Game1.currentSeason == "winter" && time is >= 1100 and <= 1400
                    && PolarPhotoperiod.At(Game1.currentSeason, Game1.dayOfMonth, time).Darkness < .50f;
            case "aurora":
                bool auroraHour = time is >= 2000 and <= 2600
                    || lanternFestival && time is >= 1800 and <= 2600;
                return Game1.currentSeason == "winter" && auroraHour
                    && Game1.dayOfMonth % 4 == 1 && PolarWeather.Today == PolarCondition.Calm
                    && (location is "ArcticPassage_Icefjord" or "ArcticPassage_Glacier"
                        || lanternFestival);
            case "blizzard":
                return PolarWeather.Today == PolarCondition.Blizzard && time is >= 600 and <= 2200
                    && location is "ArcticPassage_Tundra" or "ArcticPassage_Glacier";
            default: return false;
        }
    }

    internal static bool IsNearby(int index)
    {
        if (index < 0 || index >= Ids.Length || !Available(Ids[index])) return false;
        Point tile = index switch
        {
            0 => new Point(25, 4),
            1 => new Point(25, 25),
            2 when Game1.currentLocation.Name == "Temp" => new Point(37, 25),
            2 => Game1.currentLocation.Name == "ArcticPassage_Icefjord" ? new Point(35, 34) : new Point(31, 27),
            _ => new Point(25, 4)
        };
        return Vector2.Distance(Game1.player.Tile, tile.ToVector2()) <= (index == 2 ? 5f : 3.5f);
    }

    internal bool Record(int index, out string message)
    {
        message = "";
        if (index < 0 || index >= Ids.Length) return false;
        string id = Ids[index];
        if (!IsNearby(index)) { message = helper.Translation.Get("guide.phenomena.tooFar"); return false; }
        if (Has(id)) { message = helper.Translation.Get("guide.already"); return false; }
        string stamp = $"{Game1.year}|{Game1.currentSeason}|{Game1.dayOfMonth}|{Game1.timeOfDay}";
        Game1.player.modData[Prefix + id] = stamp;
        Game1.playSound("newArtifact");
        message = helper.Translation.Get("guide.recorded") + " " + helper.Translation.Get("guide.phenomena." + id + ".name");
        monitor.Log($"PHENOMENON RECORD {id} stamp={stamp} location={Game1.currentLocation.Name} tile={Game1.player.Tile} total={Count}", LogLevel.Info);
        return true;
    }

    internal static string Stamp(IModHelper helper, string id)
    {
        if (!Game1.player.modData.TryGetValue(Prefix + id, out string? raw)) return helper.Translation.Get("guide.unseen");
        string[] p = raw.Split('|');
        if (p.Length != 4 || !int.TryParse(p[3], out int time)) return helper.Translation.Get("guide.seen");
        return $"{helper.Translation.Get("guide.seen")} · {p[0]} / {p[1]} {p[2]} · {time / 100:00}:{time % 100:00}";
    }

    private void DrawAurora(object? sender, RenderedWorldEventArgs e)
    {
        if (!AuroraActive && !StoryChapterRuntime.FinaleActive) return;
        int width = Game1.viewport.Width;
        float phase = (float)Game1.currentGameTime.TotalGameTime.TotalSeconds;
        Color[] colors = [new(52, 200, 145, 58), new(74, 188, 171, 44), new(122, 191, 152, 38)];
        for (int ribbon = 0; ribbon < colors.Length; ribbon++)
        {
            int pieces = 20;
            Vector2 previous = new(0, 33 + ribbon * 12 + MathF.Sin(phase * .19f + ribbon) * 7);
            for (int i = 1; i <= pieces; i++)
            {
                float x = width * i / (float)pieces;
                float swell = MathF.Sin(x / Math.Max(1, width) * MathF.PI * 2 + phase * .28f + ribbon * .9f);
                Vector2 next = new(x, 33 + ribbon * 12 + swell * (9 + ribbon * 2));
                Vector2 delta = next - previous;
                e.SpriteBatch.Draw(Game1.staminaRect, previous, null, colors[ribbon], MathF.Atan2(delta.Y, delta.X),
                    Vector2.Zero, new Vector2(delta.Length(), 2.5f + ribbon * .4f), SpriteEffects.None, .995f);
                previous = next;
            }
        }
    }
}
