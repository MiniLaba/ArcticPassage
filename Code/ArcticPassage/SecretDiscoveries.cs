using Microsoft.Xna.Framework;
using Microsoft.Xna.Framework.Graphics;
using StardewModdingAPI;
using StardewModdingAPI.Events;
using StardewValley;

namespace ArcticPassage.Runtime;

/// <summary>Seven authored exploration discoveries from the frozen scope.</summary>
internal sealed class SecretDiscoveries
{
    internal const string Prefix = "WhiteBay.ArcticPassage/Secrets/";
    internal const string ShipModelMail = "ArcticPassage_OldShipModelMail";
    internal static readonly (string Id, string Location, Point Tile, string Seasons, int Start, int End, int DayModulo, int DayRemainder)[] All =
    [
        ("foxTracks", "ArcticPassage_Tundra", new(25, 33), "winter", 600, 1000, 0, 0),
        ("icebergLookout", "ArcticPassage_Icefjord", new(11, 21), "spring summer fall winter", 800, 1900, 4, 2),
        ("midnightSun", "ArcticPassage_Tundra", new(25, 4), "summer", 2200, 2600, 0, 0),
        ("snowyOwl", "ArcticPassage_Tundra", new(25, 5), "fall winter", 800, 1800, 2, 1),
        ("whaleShadow", "ArcticPassage_Icefjord", new(48, 33), "summer", 1200, 1900, 4, 0),
        ("polarNightLights", "ArcticPassage_Town", new(24, 15), "winter", 2000, 2600, 0, 0),
        ("oldShipLog", "ArcticPassage_Harbor", Point.Zero, "spring summer fall winter", 600, 2200, 0, 0)
    ];

    private readonly IModHelper helper;
    private readonly IMonitor monitor;
    private readonly WildlifeSightings wildlife;
    private readonly PolarPhenomena phenomena;

    internal SecretDiscoveries(IModHelper helper, IMonitor monitor, WildlifeSightings wildlife, PolarPhenomena phenomena)
    {
        this.helper = helper;
        this.monitor = monitor;
        this.wildlife = wildlife;
        this.phenomena = phenomena;
        helper.Events.Display.RenderedWorld += DrawClues;
    }

    internal static int Count => All.Count(entry => Has(entry.Id));
    internal static bool Has(string id) => Context.IsWorldReady && Game1.player.modData.ContainsKey(Prefix + id);
    private string T(string key) => helper.Translation.Get("guide.secret." + key);

    internal static bool Available(int index)
    {
        if (!Context.IsWorldReady || index < 0 || index >= All.Length) return false;
        var entry = All[index];
        if (Game1.currentLocation.Name != entry.Location
            || !entry.Seasons.Split(' ').Contains(Game1.currentSeason)
            || Game1.timeOfDay < entry.Start || Game1.timeOfDay > entry.End
            || (entry.DayModulo > 0 && Game1.dayOfMonth % entry.DayModulo != entry.DayRemainder)) return false;

        return entry.Id switch
        {
            "foxTracks" => YesterdayWasSnowy(),
            "midnightSun" => PolarPhenomena.Available("midnightSun"),
            "snowyOwl" => WildlifeSightings.Available(WildlifeSightings.All[5]),
            "whaleShadow" => WildlifeSightings.Available(WildlifeSightings.All[8]),
            "polarNightLights" => PolarPhotoperiod.At(Game1.currentSeason, Game1.dayOfMonth, Game1.timeOfDay).Darkness > .35f,
            "oldShipLog" => RoanCanShareLog(),
            _ => true
        };
    }

    internal static bool IsNearby(int index)
    {
        if (!Available(index)) return false;
        var entry = All[index];
        if (entry.Id == "oldShipLog")
        {
            var roan = Game1.currentLocation.characters.FirstOrDefault(npc => npc.Name == "ArcticPassage_Roan");
            return roan != null && Vector2.Distance(Game1.player.Tile, roan.Tile) <= 3.25f;
        }
        if (entry.Id == "midnightSun") return PolarPhenomena.IsNearby(0);
        if (entry.Id == "snowyOwl") return WildlifeSightings.IsNearby(5);
        if (entry.Id == "whaleShadow") return WildlifeSightings.IsNearby(8);
        if (entry.Id == "polarNightLights" && Game1.currentLocation.Name == "ArcticPassage_Harbor")
            return Vector2.Distance(Game1.player.Tile, new Vector2(21, 7)) <= 3.5f;
        return Vector2.Distance(Game1.player.Tile, entry.Tile.ToVector2()) <= (entry.Id == "whaleShadow" ? 16f : 3.5f);
    }

    internal bool Record(int index, out string message)
    {
        message = "";
        if (index < 0 || index >= All.Length) return false;
        var entry = All[index];
        if (!IsNearby(index)) { message = T("tooFar"); return false; }
        if (Has(entry.Id)) { message = helper.Translation.Get("guide.already"); return false; }

        // Finding the secret also fills the matching field observation, so one
        // genuine encounter cannot be accidentally split into two checklists.
        if (entry.Id == "midnightSun" && !PolarPhenomena.Has("midnightSun"))
            phenomena.Record(0, out _);
        if (entry.Id == "snowyOwl" && !WildlifeSightings.Has("owl"))
            wildlife.Record(5, out _);
        if (entry.Id == "whaleShadow" && !WildlifeSightings.Has("whale"))
            wildlife.Record(8, out _);

        string stamp = Game1.year + "|" + Game1.currentSeason + "|" + Game1.dayOfMonth + "|" + Game1.timeOfDay;
        Game1.player.modData[Prefix + entry.Id] = stamp;
        if (entry.Id == "oldShipLog" && !Game1.player.mailReceived.Contains(ShipModelMail)
            && !Game1.player.mailbox.Contains(ShipModelMail))
            Game1.player.mailbox.Add(ShipModelMail);
        Game1.playSound("newArtifact");
        message = T("recorded") + " " + T(entry.Id + ".name");
        monitor.Log("SECRET RECORD " + entry.Id + " stamp=" + stamp + " location=" + Game1.currentLocation.Name
            + " tile=" + Game1.player.Tile + "; total=" + Count, LogLevel.Info);
        return true;
    }

    internal void MirrorFieldObservation(string id)
    {
        string? secret = id switch
        {
            "owl" => "snowyOwl",
            "whale" => "whaleShadow",
            "midnightSun" => "midnightSun",
            _ => null
        };
        if (secret == null || Has(secret)) return;
        string prefix = id is "owl" or "whale" ? WildlifeSightings.Prefix : PolarPhenomena.Prefix;
        Game1.player.modData[Prefix + secret] = Game1.player.modData.TryGetValue(prefix + id, out string? raw)
            ? raw : Game1.year + "|" + Game1.currentSeason + "|" + Game1.dayOfMonth + "|" + Game1.timeOfDay;
        monitor.Log("SECRET MATCH " + secret + " from recorded field observation", LogLevel.Trace);
    }

    internal static string Stamp(IModHelper helper, string id)
    {
        if (!Game1.player.modData.TryGetValue(Prefix + id, out string? raw)) return helper.Translation.Get("guide.unseen");
        string[] p = raw.Split('|');
        if (p.Length != 4 || !int.TryParse(p[3], out int time)) return helper.Translation.Get("guide.seen");
        return helper.Translation.Get("guide.seen") + " · " + p[0] + " / " + p[1] + " " + p[2]
            + " · " + (time / 100).ToString("00") + ":" + (time % 100).ToString("00");
    }

    private static bool RoanCanShareLog()
        => Game1.player.friendshipData.TryGetValue("ArcticPassage_Roan", out var friendship) && friendship.Points >= 500
            && Game1.currentLocation.characters.Any(npc => npc.Name == "ArcticPassage_Roan");

    private static bool YesterdayWasSnowy()
    {
        int day = Game1.dayOfMonth - 1, year = Game1.year;
        string season = Game1.currentSeason;
        if (day < 1)
        {
            day = 28;
            season = season switch { "spring" => "winter", "summer" => "spring", "fall" => "summer", _ => "fall" };
            if (Game1.currentSeason == "spring") year--;
        }
        return PolarForecast.ForDate(year, season, day) == PolarCondition.Blizzard;
    }

    private static bool FoxTracksVisible => Context.IsWorldReady && !Has("foxTracks")
        && Game1.currentLocation.Name == "ArcticPassage_Tundra" && Game1.currentSeason == "winter"
        && Game1.timeOfDay is >= 600 and <= 1000 && YesterdayWasSnowy();

    private static bool NightLightsVisible => Context.IsWorldReady && Game1.currentSeason == "winter"
        && Game1.timeOfDay is >= 2000 and <= 2600
        && Game1.currentLocation.Name is "ArcticPassage_Town" or "ArcticPassage_Harbor";

    private void DrawClues(object? sender, RenderedWorldEventArgs e)
    {
        if (!Context.IsWorldReady) return;
        if (FoxTracksVisible) DrawFoxTracks(e.SpriteBatch);
        if (NightLightsVisible) DrawNightLights(e.SpriteBatch);
    }

    private static void DrawFoxTracks(SpriteBatch batch)
    {
        float fade = .62f + MathF.Sin((float)Game1.currentGameTime.TotalGameTime.TotalSeconds * 1.2f) * .05f;
        foreach (var step in new[] { (25, 33, 0), (23, 33, 1), (21, 33, 0), (19, 33, 1) })
        {
            Vector2 world = new(step.Item1 * 64, step.Item2 * 64);
            Vector2 local = Game1.GlobalToLocal(Game1.viewport, world);
            var color = new Color(105, 129, 139) * fade;
            batch.Draw(Game1.staminaRect, new Rectangle((int)local.X + 24 + step.Item3 * 8, (int)local.Y + 28, 7, 5), color);
            batch.Draw(Game1.staminaRect, new Rectangle((int)local.X + 26 + step.Item3 * 8, (int)local.Y + 23, 3, 3), color);
        }
    }

    private static void DrawNightLights(SpriteBatch batch)
    {
        float pulse = .8f + MathF.Sin((float)Game1.currentGameTime.TotalGameTime.TotalSeconds * .7f) * .06f;
        Point[] anchors = Game1.currentLocation.Name == "ArcticPassage_Town"
            ? [new Point(24, 15), new Point(25, 17), new Point(27, 13)]
            : [new Point(21, 7), new Point(23, 12), new Point(19, 29)];
        foreach (Point tile in anchors)
        {
            Vector2 world = new(tile.X * 64, tile.Y * 64);
            Vector2 local = Game1.GlobalToLocal(Game1.viewport, world);
            batch.Draw(Game1.staminaRect, new Rectangle((int)local.X - 14, (int)local.Y - 18, 52, 52), new Color(251, 180, 105) * (.10f * pulse));
            batch.Draw(Game1.staminaRect, new Rectangle((int)local.X - 3, (int)local.Y - 5, 25, 30), new Color(255, 218, 151) * (.17f * pulse));
        }
    }
}
