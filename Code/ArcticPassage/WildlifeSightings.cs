using Microsoft.Xna.Framework;
using Microsoft.Xna.Framework.Graphics;
using StardewModdingAPI;
using StardewModdingAPI.Events;
using StardewValley;

namespace ArcticPassage.Runtime;

/// <summary>Non-interactive, distant wildlife observations; all records live in the native farmer save.</summary>
internal sealed class WildlifeSightings
{
    internal const string Prefix = "WhiteBay.ArcticPassage/FieldGuide/animal_";
    internal readonly record struct Species(string Id, string Location, Point Tile, int Sprite,
        string Seasons, int Start, int End, float Radius, int DayModulo = 0, int DayRemainder = 0);

    // Greenland species are staged only in suitable coastal/tundra/ice settings.
    // Rare marine and polar-bear views use a deterministic calendar window so a save can find them.
    internal static readonly Species[] All =
    [
        new("bear", "ArcticPassage_Glacier", new(44, 13), 0, "winter", 800, 1700, 18, 7, 0),
        new("fox", "ArcticPassage_Tundra", new(18, 33), 1, "spring summer fall winter", 700, 2200, 4),
        new("caribou", "ArcticPassage_Tundra", new(25, 19), 2, "spring summer fall", 700, 1900, 7, 3, 0),
        new("seal", "ArcticPassage_Icefjord", new(16, 24), 3, "spring fall winter", 800, 1800, 7, 3, 0),
        new("walrus", "ArcticPassage_Harbor", new(42, 13), 4, "summer fall", 800, 1800, 6, 4, 2),
        new("owl", "ArcticPassage_Tundra", new(25, 5), 5, "fall winter", 800, 1800, 5, 2, 1),
        new("kittiwake", "ArcticPassage_Harbor", new(37, 8), 6, "spring summer fall", 600, 2000, 5),
        new("sleddog", "ArcticPassage_SledTrail", new(25, 25), 7, "winter", 800, 2000, 5),
        new("whale", "ArcticPassage_Icefjord", new(48, 33), 8, "summer", 1200, 1900, 16, 4, 0),
        new("shark", "ArcticPassage_Icefjord", new(51, 37), 9, "fall winter", 900, 1700, 16, 6, 0)
    ];

    private readonly IModHelper helper;
    private readonly IMonitor monitor;
    private Texture2D? atlas;

    internal WildlifeSightings(IModHelper helper, IMonitor monitor)
    {
        this.helper = helper;
        this.monitor = monitor;
        helper.Events.Display.RenderedWorld += Draw;
        helper.Events.Player.Warped += (_, e) =>
        {
            if (e.IsLocalPlayer && e.NewLocation.Name == "ArcticPassage_Glacier" && PolarBearActive)
            {
                Game1.addHUDMessage(new HUDMessage(T("safety"), 2));
                monitor.Log("WILDLIFE distant polar bear day; field-deck warning shown; no walking route closed", LogLevel.Info);
            }
        };
    }

    private string T(string key) => helper.Translation.Get("guide.wildlife." + key);
    internal static bool Has(string id) => Context.IsWorldReady && Game1.player.modData.ContainsKey(Prefix + id);
    internal static int Count => All.Count(s => Has(s.Id));
    internal static bool PolarBearActive => Context.IsWorldReady && InWindow(All[0]);

    internal static bool Available(Species species)
    {
        if (!Context.IsWorldReady || Game1.currentLocation.Name != species.Location || !InWindow(species)) return false;
        if (species.Id is "owl" or "whale" && Has(species.Id)) return false;
        return true;
    }

    private static bool InWindow(Species species)
    {
        if (!Context.IsWorldReady || !species.Seasons.Split(' ').Contains(Game1.currentSeason)
            || Game1.timeOfDay < species.Start || Game1.timeOfDay > species.End) return false;
        if (species.Id == "sleddog" && !Game1.player.mailReceived.Contains("ArcticPassage_Shed")) return false;
        return species.DayModulo == 0 || Game1.dayOfMonth % species.DayModulo == species.DayRemainder;
    }

    internal static int Nearby()
    {
        if (!Context.IsWorldReady) return -1;
        for (int i = 0; i < All.Length; i++)
        {
            Species species = All[i];
            if (Available(species) && Vector2.Distance(Game1.player.Tile, species.Tile.ToVector2()) <= species.Radius)
                return i;
        }
        return -1;
    }

    internal static bool IsNearby(int index)
    {
        if (index < 0 || index >= All.Length || !Available(All[index])) return false;
        if (All[index].Id == "bear")
            return Vector2.Distance(Game1.player.Tile, new Vector2(31, 27)) <= 4f;
        return Vector2.Distance(Game1.player.Tile, All[index].Tile.ToVector2()) <= All[index].Radius;
    }

    internal bool Record(int index, out string message)
    {
        message = "";
        if (index < 0 || index >= All.Length) return false;
        Species species = All[index];
        if (!IsNearby(index)) { message = T("tooFar"); return false; }
        if (Has(species.Id)) { message = T("already"); return false; }
        string stamp = $"{Game1.year}|{Game1.currentSeason}|{Game1.dayOfMonth}|{Game1.timeOfDay}";
        Game1.player.modData[Prefix + species.Id] = stamp;
        Game1.playSound("newArtifact");
        message = T("recorded") + " " + T(species.Id + ".name");
        monitor.Log($"WILDLIFE RECORD {species.Id} stamp={stamp} location={species.Location} tile={species.Tile} total={Count}", LogLevel.Info);
        return true;
    }

    internal static string Stamp(IModHelper helper, string id)
    {
        if (!Game1.player.modData.TryGetValue(Prefix + id, out string? raw)) return helper.Translation.Get("guide.unseen");
        string[] p = raw.Split('|');
        if (p.Length != 4 || !int.TryParse(p[3], out int time)) return helper.Translation.Get("guide.seen");
        return $"{helper.Translation.Get("guide.seen")} · {p[0]} / {p[1]} {p[2]} · {time / 100:00}:{time % 100:00}";
    }

    private void Draw(object? sender, RenderedWorldEventArgs e)
    {
        if (!Context.IsWorldReady) return;
        if (!All.Any(Available)) return;
        atlas ??= helper.ModContent.Load<Texture2D>("assets/wildlife/sightings.png");
        for (int index = 0; index < All.Length; index++)
        {
            Species species = All[index];
            if (Available(species)) DrawOne(e.SpriteBatch, species, index);
        }
    }

    private void DrawOne(SpriteBatch batch, Species species, int index)
    {
        float time = (float)Game1.currentGameTime.TotalGameTime.TotalSeconds;
        int frame = (int)(time * 1.15f + index) % 2;
        Vector2 world = new(species.Tile.X * 64 - 16, species.Tile.Y * 64 - 36);
        Vector2 local = Game1.GlobalToLocal(Game1.viewport, world);
        float bob = MathF.Sin(time * 2 + index) * (species.Id is "whale" or "shark" ? 1.5f : 2f);
        if (species.Id is not ("whale" or "shark" or "kittiwake"))
        {
            var shadow = new Rectangle((int)local.X + 16, (int)local.Y + 63, 64, 8);
            batch.Draw(Game1.staminaRect, shadow, new Color(58, 79, 91) * .25f);
        }
        var source = new Rectangle(species.Sprite * 32, frame * 24, 32, 24);
        Color tint = species.Id == "shark" ? new Color(150, 192, 202) * .68f : Color.White;
        if (species.Id == "sleddog")
        {
            // Three distinct silhouettes read as a resting work team beside the parked sled.
            for (int dog = 0; dog < 3; dog++)
                batch.Draw(atlas!, new Vector2(local.X - 34 + dog * 31, local.Y + 8 + bob + MathF.Sin(time * 2 + dog) * 1.2f),
                    source, Color.White, 0, Vector2.Zero, 1.9f, SpriteEffects.None, .92f);
        }
        else
            batch.Draw(atlas!, new Vector2(local.X, local.Y + bob), source, tint,
                0, Vector2.Zero, 3f, SpriteEffects.None, .92f);

        if (species.Id == "bear") DrawTracks(batch, local, time);
    }

    private static void DrawTracks(SpriteBatch b, Vector2 local, float time)
    {
        // Sparse paired impressions point toward the distant animal, beside the safe lookout.
        float fade = .75f + MathF.Sin(time) * .08f;
        foreach (var p in new[] { new Point(3, 47), new Point(16, 35), new Point(29, 23) })
        {
            var c = new Vector2(local.X + p.X, local.Y + p.Y);
            b.Draw(Game1.staminaRect, new Rectangle((int)c.X, (int)c.Y, 7, 4), new Color(116, 143, 151) * fade);
            b.Draw(Game1.staminaRect, new Rectangle((int)c.X + 6, (int)c.Y - 3, 2, 2), new Color(116, 143, 151) * fade);
        }
    }
}
