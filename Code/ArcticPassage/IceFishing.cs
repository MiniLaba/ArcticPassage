using HarmonyLib;
using Microsoft.Xna.Framework;
using Microsoft.Xna.Framework.Graphics;
using StardewModdingAPI;
using StardewModdingAPI.Events;
using StardewValley;
using StardewValley.Tools;

namespace ArcticPassage.Runtime;

/// <summary>A surveyed opening beside the fixed fjord platform. Terrain collision stays native.</summary>
internal sealed class IceFishing
{
    internal const string Location = "ArcticPassage_Icefjord";
    internal const string DayKey = "WhiteBay.ArcticPassage/IceFishingDay";
    internal static readonly Rectangle Opening = new(41, 34, 3, 2);
    private readonly IModHelper helper;
    private readonly IMonitor monitor;
    private Texture2D? sealedIce, openIce, marker;
    private Farmer? working;
    private int remaining, workDay;

    internal static bool IsOpen => Context.IsWorldReady && Game1.currentSeason == "winter"
        && Game1.MasterPlayer.modData.TryGetValue(DayKey, out string? day)
        && day == Game1.Date.TotalDays.ToString(System.Globalization.CultureInfo.InvariantCulture);

    internal IceFishing(IModHelper helper, IMonitor monitor, Harmony harmony)
    {
        this.helper = helper; this.monitor = monitor;
        GameLocation.RegisterTileAction("ArcticPassageIceFishing", Open);
        foreach (string name in new[] { nameof(GameLocation.isTileFishable), nameof(GameLocation.isTileBuildingFishable) })
            harmony.Patch(AccessTools.Method(typeof(GameLocation), name, [typeof(int), typeof(int)]),
                postfix: new HarmonyMethod(typeof(IceFishing), nameof(Fishable)));
        helper.Events.GameLoop.UpdateTicked += Update;
        helper.Events.Input.ButtonPressed += (_, e) =>
        {
            // The native pointer can remain over a distant tile after keyboard travel.
            // At this one marker, X explicitly invokes its real map action from the safe approach.
            if (e.Button != SButton.X || e.IsSuppressed() || !Context.IsWorldReady
                || Game1.activeClickableMenu != null || Game1.eventUp || Game1.dialogueUp
                || !Game1.player.CanMove || Game1.player.UsingTool || Game1.currentLocation.Name != Location
                || Game1.player.TilePoint != new Point(40,34) || Game1.player.FacingDirection != 2) return;
            string action = Game1.currentLocation.doesTileHaveProperty(40,35,"Action","Buildings");
            if (action != "ArcticPassageIceFishing") return;
            helper.Input.Suppress(e.Button);
            Game1.currentLocation.performAction(action,Game1.player,new xTile.Dimensions.Location(40,35));
        };
        helper.Events.Display.RenderedWorld += Draw;
        helper.Events.GameLoop.ReturnedToTitle += (_, _) => { working = null; remaining = 0; };
        helper.Events.GameLoop.DayStarted += (_, _) => { working = null; remaining = 0; };
    }

    private static void Fishable(GameLocation __instance, int __0, int __1, ref bool __result)
    {
        if (Context.IsWorldReady && Game1.currentSeason == "winter" && __instance.Name == Location && Opening.Contains(__0, __1))
            __result = IsOpen;
    }

    private bool Open(GameLocation location, string[] args, Farmer who, Point tile)
    {
        if (location.Name != Location || tile != new Point(40, 35)) return false;
        string? message = Game1.currentSeason != "winter" ? "ice.season"
            : !who.mailReceived.Contains("ArcticPassage_Boat") ? "ice.locked"
            : IsOpen ? "ice.ready"
            : !Context.IsMainPlayer ? "ice.host"
            : who.CurrentTool is not Pickaxe ? "ice.tool" : null;
        if (message != null) { Game1.drawObjectDialogue(helper.Translation.Get(message)); return true; }
        if (working != null) return true;
        // Work is explicit, consumes no materials, and never moves anyone onto sea ice.
        working = who; remaining = 84; workDay = Game1.Date.TotalDays;
        who.faceDirection(1); who.freezePause = Math.Max(who.freezePause, 1400);
        location.localSound("hammer");
        monitor.Log($"ICE surveyed-site clearing started day={workDay}; collision unchanged", LogLevel.Trace);
        return true;
    }

    private void Update(object? sender, UpdateTickedEventArgs e)
    {
        if (working == null) return;
        if (!Context.IsWorldReady || Game1.currentSeason != "winter" || Game1.Date.TotalDays != workDay
            || working.currentLocation?.Name != Location)
        { working = null; remaining = 0; return; }
        if (Game1.activeClickableMenu != null || Game1.eventUp) return;
        if (--remaining is 56 or 28) working.currentLocation.localSound("hammer");
        if (remaining > 0) return;
        Game1.MasterPlayer.modData[DayKey] = workDay.ToString(System.Globalization.CultureInfo.InvariantCulture);
        working = null;
        Game1.addHUDMessage(new HUDMessage(helper.Translation.Get("ice.opened"), HUDMessage.newQuest_type));
        monitor.Log($"ICE opening ready day={workDay}; exact 3x2 native fishing target, no walkable ice added", LogLevel.Info);
    }

    private void Draw(object? sender, RenderedWorldEventArgs e)
    {
        if (!Context.IsWorldReady || Game1.currentSeason != "winter" || Game1.currentLocation.Name != Location) return;
        sealedIce ??= helper.ModContent.Load<Texture2D>("assets/ice/sealed.png");
        openIce ??= helper.ModContent.Load<Texture2D>("assets/ice/open.png");
        marker ??= helper.ModContent.Load<Texture2D>("assets/ice/marker.png");
        Vector2 origin = Game1.GlobalToLocal(Game1.viewport, new Vector2(Opening.X * 64, Opening.Y * 64));
        e.SpriteBatch.Draw(IsOpen ? openIce : sealedIce, origin, null, Color.White, 0, Vector2.Zero, 4, SpriteEffects.None, 1);
        e.SpriteBatch.Draw(marker, origin + new Vector2(-64,64), null, Color.White, 0, Vector2.Zero, 4, SpriteEffects.None, 1);
        if (working == null) return;
        float t = (84 - remaining) / 84f;
        for (int i = 0; i < 7; i++)
        {
            float phase = (t * 3 + i * .14f) % 1;
            Vector2 chip = origin + new Vector2(30 + i * 18, 55 - MathF.Sin(phase * MathF.PI) * 48);
            e.SpriteBatch.Draw(Game1.staminaRect, new Rectangle((int)chip.X, (int)chip.Y, 5, 4), new Color(225, 242, 250) * (1-phase));
        }
    }
}
