using Microsoft.Xna.Framework;
using StardewModdingAPI;
using StardewModdingAPI.Events;
using StardewValley;
using StardewValley.Mods;

namespace ArcticPassage.Runtime;

// Native lightmap colours subtract light. Keep this override within its draw
// step, so outdoor climate, interior lighting and other locations retain theirs.
internal sealed class NightLighting
{
    private const string Prefix = "WhiteBay.ArcticPassage/Night/";
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
        if (!Context.IsWorldReady || location == null || !location.IsOutdoors || !anchors.ContainsKey(location.Name))
        { Clear(); return; }
        if (scene != location.Name)
        {
            Clear(); scene = location.Name;
            int index = 0;
            foreach (var anchor in anchors[scene])
            {
                string id = Prefix + scene + "/" + index++;
                lights[id] = new LightSource(id, LightSource.lantern,
                    new Vector2(anchor.X * 4, anchor.Y * 4), anchor.Radius,
                    new Color(8, 65, 130), default, 0, scene);
            }
        }
        int start = Minutes(Game1.getStartingToGetDarkTime(location));
        int end = Minutes(Game1.getTrulyDarkTime(location));
        // Clock stays native; this is dusk treatment, not polar photoperiod.
        float fraction = Math.Clamp((float)Game1.gameTimeInterval /
            Math.Max(1, Game1.realMilliSecondsPerGameMinute + location.ExtraMillisecondsPerInGameMinute), 0, 10);
        float dusk = Math.Clamp((Minutes(Game1.timeOfDay) + fraction - start) / Math.Max(1f, end - start), 0, 1);
        dusk = dusk * dusk * (3 - 2 * dusk);
        var day = location.IsRainingHere() ? new Color(28, 24, 20) : new Color(0, 0, 0);
        var tint = Color.Lerp(day, new Color(175, 155, 135), dusk);
        savedAmbient = Game1.ambientLight; savedOutdoor = Game1.outdoorLight; overriding = true;
        Game1.ambientLight = Game1.outdoorLight = tint;
        foreach (var pair in lights)
        {
            pair.Value.color.Value = new Color(8, 65, 130, (int)(255 * dusk));
            Game1.currentLightSources[pair.Key] = pair.Value;
        }
        string trace = scene + ":" + (int)(dusk * 4);
        if (lastTrace != trace)
        {
            lastTrace = trace;
            monitor.Log($"NIGHT LIGHTMAP {scene} time={Game1.timeOfDay} dusk={dusk:F2} tint={tint} lamps={lights.Count}", LogLevel.Trace);
        }
    }

    private static int Minutes(int time) => time / 100 * 60 + time % 100;
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
