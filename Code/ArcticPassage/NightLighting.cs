using Microsoft.Xna.Framework;
using StardewModdingAPI;
using StardewModdingAPI.Events;
using StardewValley;
using StardewValley.Mods;

namespace ArcticPassage.Runtime;

// Native lightmap colours subtract light. Keep this override within its draw
// step, so the Valley, interior lighting and other locations retain theirs.
internal sealed class NightLighting
{
    private const string Prefix = "WhiteBay.ArcticPassage/Night/";
    private static readonly HashSet<string> OutdoorRegions =
    [
        "ArcticPassage_Town", "ArcticPassage_Harbor", "ArcticPassage_Icefjord", "ArcticPassage_Tundra",
        "ArcticPassage_WinterCamp", "ArcticPassage_Airstrip", "ArcticPassage_SledTrail", "ArcticPassage_Glacier"
    ];
    private readonly Dictionary<string, LampAnchor[]> anchors;
    private readonly Dictionary<string, LightSource> lights = [];
    private readonly IMonitor monitor;
    private string? scene;
    private string? lastTrace;
    private Color savedAmbient, savedOutdoor;
    private bool overriding;

    internal NightLighting(IModHelper helper, IMonitor monitor)
    {
        this.monitor = monitor;
        anchors = helper.Data.ReadJsonFile<Dictionary<string, LampAnchor[]>>("lighting.json")
            ?? throw new InvalidOperationException("Missing Arctic lighting anchors");
        helper.Events.Display.RenderingStep += BeginLightmap;
        helper.Events.Display.RenderedStep += (_, e) => { if (e.Step == RenderSteps.World_RenderLightmap) Restore(); };
        helper.Events.Display.Rendered += (_, _) => Restore();
        helper.Events.Player.Warped += (_, e) => { if (e.IsLocalPlayer) Clear(); };
        helper.Events.GameLoop.ReturnedToTitle += (_, _) => Clear();
    }

    private void BeginLightmap(object? sender, RenderingStepEventArgs e)
    {
        if (e.Step != RenderSteps.World_RenderLightmap) return;
        Restore();
        var location = Game1.currentLocation;
        if (!Context.IsWorldReady || location == null || !location.IsOutdoors)
        { Clear(); return; }
        string anchorMap = FestivalMap(location) ?? location.Name;
        if (!OutdoorRegions.Contains(anchorMap))
        { Clear(); return; }
        string sceneKey = location.Name + "|" + anchorMap;
        if (scene != sceneKey)
        {
            Clear(); scene = sceneKey;
            int index = 0;
            foreach (var anchor in anchors.GetValueOrDefault(anchorMap, []))
            {
                string id = Prefix + sceneKey + "/" + index++;
                lights[id] = new LightSource(id, LightSource.lantern,
                    new Vector2(anchor.X * 4, anchor.Y * 4), anchor.Radius,
                    new Color(8, 65, 130), default, 0, location.Name);
            }
        }
        // Treat each frame continuously while leaving the native clock alone.
        float fraction = Math.Clamp((float)Game1.gameTimeInterval /
            Math.Max(1, Game1.realMilliSecondsPerGameMinute + location.ExtraMillisecondsPerInGameMinute), 0, 10);
        float elapsedMinutes = Game1.timeOfDay / 100 * 60 + Game1.timeOfDay % 100 + fraction;
        bool finale = StoryChapterRuntime.FinaleActive;
        var sample = finale ? PolarPhotoperiod.AtMinute("winter", 21, 22 * 60)
            : PolarPhotoperiod.AtMinute(Game1.currentSeason, Game1.dayOfMonth, elapsedMinutes);
        float darkness = sample.Darkness;
        float nightBlend = Math.Clamp((darkness - sample.WinterDayBlue) / Math.Max(.01f, 1f - sample.WinterDayBlue), 0f, 1f);
        var day = location.IsRainingHere() ? new Color(28, 24, 20) : Color.Black;
        var winterBlue = new Color(25, 38, 60);
        var night = Game1.currentSeason == "winter" ? new Color(145, 160, 192) : new Color(150, 160, 188);
        var tint = Color.Lerp(Color.Lerp(day, winterBlue, sample.WinterDayBlue), night, nightBlend);
        savedAmbient = Game1.ambientLight; savedOutdoor = Game1.outdoorLight; overriding = true;
        Game1.ambientLight = Game1.outdoorLight = tint;
        foreach (var pair in lights)
        {
            float lamp = Math.Clamp((nightBlend - .18f) / .58f, 0f, 1f);
            lamp = lamp * lamp * (3f - 2f * lamp);
            pair.Value.color.Value = new Color(8, 65, 130, (int)(255 * lamp));
            Game1.currentLightSources[pair.Key] = pair.Value;
        }
        string trace = scene + ":" + Game1.currentSeason + ":" + (int)(darkness * 10);
        if (lastTrace != trace)
        {
            lastTrace = trace;
            monitor.Log($"POLAR LIGHTMAP {scene} season={Game1.currentSeason} day={Game1.dayOfMonth} time={Game1.timeOfDay} darkness={darkness:F2} winterBlue={sample.WinterDayBlue:F2} tint={tint} lamps={lights.Count}", LogLevel.Trace);
        }
    }

    private static string? FestivalMap(GameLocation location)
    {
        if (StoryChapterRuntime.FinaleActive) return "ArcticPassage_Town";
        if (location.Name != "Temp") return null;
        return FestivalRuntime.FestivalForEvent(location.currentEvent) switch
        {
            "spring" => "ArcticPassage_Harbor",
            "summer" => "ArcticPassage_Icefjord",
            "winter" => "ArcticPassage_Town",
            _ => null
        };
    }
    private void Restore()
    {
        if (!overriding) return;
        Game1.ambientLight = savedAmbient; Game1.outdoorLight = savedOutdoor; overriding = false;
    }
    private void Clear()
    {
        Restore();
        foreach (string id in lights.Keys) Game1.currentLightSources.Remove(id);
        lights.Clear(); scene = null; lastTrace = null;
    }
}

internal sealed class LampAnchor
{
    public int X { get; set; }
    public int Y { get; set; }
    public float Radius { get; set; } = 1.5f;
}
