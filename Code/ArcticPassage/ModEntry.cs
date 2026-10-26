using HarmonyLib;
using Microsoft.Xna.Framework;
using StardewModdingAPI;
using StardewValley;
using StardewValley.Objects;

namespace ArcticPassage.Runtime;

public sealed class ModEntry : Mod
{
    internal const string ChestTag = "WhiteBay.ArcticPassage.Runtime/RecoveryChest";
    private const string NoticeId = "ArcticPassage_RecoveredGear";
    private static readonly string[] Coasts = ["Town", "Harbor", "Icefjord", "Tundra"];
    private static IMonitor? runtimeMonitor;
    private bool pending;
    private int retryDelay;
    private bool warnedFull;
    private readonly Dictionary<string, string> mapSeasons = [];

    public override void Entry(IModHelper helper)
    {
        runtimeMonitor = Monitor;
        _ = new KeyboardStart(helper, Monitor);
        _ = new AirTravel(helper, Monitor);
        _ = new KeyboardCounters(helper, Monitor);
        _ = new KeyboardJournal(helper, Monitor);
        _ = new FishingTrace(helper, Monitor);
        _ = new NightLighting(helper, Monitor);
        _ = new FieldGuide(helper, Monitor);
        _ = new KeyboardNotices(helper, Monitor);
        _ = new PolarWeather(helper, Monitor);
        _ = new KeyboardRoutes(helper, Monitor);
        _ = new WeeklyOrders(helper, Monitor);
        _ = new FestivalRuntime(helper, Monitor);
        // CP refreshes season tokens after native overnight object updates.
        // Read the real new date at the fish-type boundary so winter 1 never
        // inherits autumn shrimp. Native bait, RNG and catch handling remain.
        var harmony = new Harmony(ModManifest.UniqueID);
        _ = new DailyOrders(helper, Monitor, harmony);
        _ = new IceFishing(helper, Monitor, harmony);
        _ = new SledTravel(helper, Monitor);
        _ = new SnowShelterLesson(helper, Monitor);
        _ = new StoryChapterRuntime(helper, Monitor, harmony);
        // Native spring critters are independent of random-ambience settings.
        // Keep native cloud shadows, but reserve wildlife for authored Arctic species.
        foreach (string method in new[] { "addButterflies", "addBirdies", "addBunnies", "addSquirrels", "addWoodpecker", "addOpossums", "addOwl" })
            harmony.Patch(AccessTools.Method(typeof(GameLocation), method),
                prefix: new HarmonyMethod(typeof(ModEntry), nameof(AllowValleyCritters)));
        harmony.Patch(AccessTools.Method(typeof(GameLocation), nameof(GameLocation.getFish)),
            postfix: new HarmonyMethod(typeof(ModEntry), nameof(CoastalTutorialFallback)));
        harmony.Patch(
            AccessTools.Method(typeof(GameLocation), nameof(GameLocation.GetCrabPotFishForTile)),
            postfix: new HarmonyMethod(typeof(ModEntry), nameof(CurrentCoastTrapTypes)));
        helper.Events.Content.AssetRequested += (_, e) =>
        {
            if (e.NameWithoutLocale.IsEquivalentTo("Data/mail"))
                e.Edit(asset => asset.AsDictionary<string, string>().Data[NoticeId] = helper.Translation.Get("recovery.letter"));
        };
        helper.Events.GameLoop.SaveLoaded += (_, _) => Request();
        helper.Events.GameLoop.DayStarted += (_, _) => { warnedFull = false; Request(); };
        helper.Events.Player.Warped += (_, e) =>
        {
            if (e.IsLocalPlayer && e.NewLocation.Name.StartsWith("ArcticPassage_")) Request();
        };
        helper.Events.Display.MenuChanged += (_, e) =>
        {
            if (e.OldMenu != null && e.NewMenu == null) Request();
        };
        helper.Events.GameLoop.ReturnedToTitle += (_, _) => { pending = false; warnedFull = false; mapSeasons.Clear(); };
        helper.Events.GameLoop.OneSecondUpdateTicked += (_, _) =>
        {
            if (!pending || !Context.IsWorldReady || !Context.IsMainPlayer) return;
            if (retryDelay-- > 0) return;
            try { RecoverNow(); }
            catch (Exception ex)
            {
                Monitor.Log($"Gear recovery deferred without discarding stranded objects: {ex}", LogLevel.Error);
                pending = true; retryDelay = 10;
            }
        };
    }

    private static bool AllowValleyCritters(GameLocation __instance)
        => __instance.Name != "ArcticPassage_Town" && __instance.Name != "ArcticPassage_Harbor"
            && __instance.Name != "ArcticPassage_Icefjord" && __instance.Name != "ArcticPassage_Tundra"
            && __instance.Name != "ArcticPassage_WinterCamp" && __instance.Name != "ArcticPassage_Airstrip"
            && __instance.Name != "ArcticPassage_SledTrail" && __instance.Name != "ArcticPassage_Glacier";

    // The engine returns a sunfish if both tutorial pool passes fail. Replace
    // only that fallback before the normal rod/minigame/award pipeline runs.
    // Do not change ordinary catches, the Valley, or a player's fishing record.
    private static void CoastalTutorialFallback(GameLocation __instance, Farmer who, ref Item __result)
    {
        if (__result?.QualifiedItemId != "(O)145" || who?.fishCaught == null || who.fishCaught.Length != 0) return;
        if (__instance.Name != "ArcticPassage_Harbor" && __instance.Name != "ArcticPassage_Icefjord") return;
        string starter = Game1.currentSeason switch
        {
            "spring" or "summer" => "Capelin",
            "fall" => "AtlanticCod",
            "winter" => "PolarCod",
            _ => ""
        };
        if (starter.Length == 0) return;
        __result = ItemRegistry.Create("(O)ArcticPassage_" + starter);
        runtimeMonitor?.Log($"TUTORIAL coastal fallback {__instance.Name}/{Game1.currentSeason}: sunfish -> {starter}; native minigame retained", LogLevel.Trace);
    }

    private static void CurrentCoastTrapTypes(GameLocation __instance, ref IList<string> __result)
    {
        string name = __instance.Name;
        if (name != "ArcticPassage_Harbor" && name != "ArcticPassage_Icefjord") return;
        string season = Game1.currentSeason;
        string kind = name == "ArcticPassage_Harbor" && season != "winter" ? "shrimp" : "crab";
        // Preserve types contributed by other mods; replace only our own tags.
        var types = __result.Where(t => !t.StartsWith("ap_shrimp_") && !t.StartsWith("ap_crab_")).ToList();
        types.Add($"ap_{kind}_{season}");
        __result = types;
    }

    private void Request() { pending = true; retryDelay = 0; }
    public override object GetApi() => new RecoveryApi(this);

    internal int RecoverNow()
    {
        if (!Context.IsWorldReady || !Context.IsMainPlayer) return 0;
        int returned = 0; bool blocked = false;
        var fishery = Game1.getLocationFromName("ArcticPassage_Fishery");
        if (fishery == null) return 0;
        foreach (string name in Coasts)
        {
            var coast = Game1.getLocationFromName("ArcticPassage_" + name);
            if (coast == null || !coast.objects.Values.OfType<CrabPot>().Any(p => p.ItemId == "710")) continue;
            // Use the current CP map, not the previous season's cached coastline.
            if (!mapSeasons.TryGetValue(name, out string? season) || season != Game1.currentSeason)
            {
                coast.reloadMap(); mapSeasons[name] = Game1.currentSeason;
            }
            var reachable = ReachableShore(coast);
            foreach (var pair in coast.objects.Pairs.Where(p => p.Value is CrabPot && p.Value.ItemId == "710").ToArray())
            {
                var pot = (CrabPot)pair.Value;
                if (CanReach(coast, pair.Key, reachable)) continue;
                var chest = FindChest(fishery);
                if (chest == null) { blocked = true; Warn("recovery.space"); continue; }
                var gear = ItemRegistry.Create("(O)710");
                foreach (var field in pot.modData.Pairs) gear.modData[field.Key] = field.Value;
                var contents = new List<Item> { gear };
                if (pot.heldObject.Value is Item catchItem) contents.Add(Clone(catchItem));
                else if (pot.bait.Value is Item bait) contents.Add(Clone(bait));
                // Full storage leaves the source untouched, including bait and catch.
                if (!TryStore(chest, contents)) { blocked = true; Warn("recovery.full"); continue; }
                coast.objects.Remove(pair.Key);
                try { pot.performRemoveAction(); }
                catch (Exception ex) { Monitor.Log($"Recovered pot overlay cleanup: {ex.Message}", LogLevel.Warn); }
                returned++;
                Monitor.Log($"Recovered icebound pot from {coast.Name} {pair.Key}; preserved {contents.Count - 1} attached item(s).", LogLevel.Trace);
            }
        }
        pending = blocked; retryDelay = 10;
        if (returned > 0)
        {
            Game1.addHUDMessage(new HUDMessage(Helper.Translation.Get("recovery.returned", new { count = returned }), 2));
            if (!Game1.player.mailReceived.Contains(NoticeId) && !Game1.player.mailbox.Contains(NoticeId)) Game1.player.mailbox.Add(NoticeId);
        }
        return returned;
    }

    private void Warn(string key)
    {
        if (warnedFull) return;
        warnedFull = true;
        Game1.addHUDMessage(new HUDMessage(Helper.Translation.Get(key), 2));
    }

    private static bool Standable(GameLocation location, Point tile)
    {
        var map = location.Map;
        return tile.X >= 0 && tile.Y >= 0 && tile.X < map.Layers[0].LayerWidth && tile.Y < map.Layers[0].LayerHeight
            && !location.isWaterTile(tile.X, tile.Y) && map.GetLayer("Back").Tiles[tile.X, tile.Y] != null
            && map.GetLayer("Buildings").Tiles[tile.X, tile.Y] == null;
    }

    private static IEnumerable<Point> Neighbors(Point p)
    {
        yield return new Point(p.X - 1, p.Y); yield return new Point(p.X + 1, p.Y);
        yield return new Point(p.X, p.Y - 1); yield return new Point(p.X, p.Y + 1);
    }

    private static HashSet<Point> ReachableShore(GameLocation location)
    {
        var arrival = location.GetData().DefaultArrivalTile
            ?? throw new InvalidOperationException($"Missing arrival tile for {location.Name}; refusing gear relocation");
        var start = new Point(arrival.X, arrival.Y);
        var seen = new HashSet<Point>(); var queue = new Queue<Point>();
        if (!Standable(location, start)) throw new InvalidOperationException($"Arrival tile is blocked in {location.Name}; refusing gear relocation");
        seen.Add(start); queue.Enqueue(start);
        while (queue.TryDequeue(out Point tile))
            foreach (Point next in Neighbors(tile))
                if (Standable(location, next) && seen.Add(next)) queue.Enqueue(next);
        return seen;
    }

    private static bool CanReach(GameLocation location, Vector2 tile, HashSet<Point> shore)
        => location.isWaterTile((int)tile.X, (int)tile.Y) && Neighbors(new Point((int)tile.X, (int)tile.Y)).Any(shore.Contains);

    private static Chest? FindChest(GameLocation fishery)
    {
        var existing = fishery.objects.Values.OfType<Chest>().FirstOrDefault(c => c.modData.ContainsKey(ChestTag));
        if (existing != null) return existing;
        foreach (var tile in new[] { new Point(14, 14), new Point(15, 14), new Point(14, 15), new Point(15, 15) })
        {
            var position = new Vector2(tile.X, tile.Y);
            if (!Standable(fishery, tile) || fishery.objects.ContainsKey(position)) continue;
            var chest = new Chest(true, position, "130") { Location = fishery };
            chest.modData[ChestTag] = "1";
            chest.playerChoiceColor.Value = new Color(72, 126, 140);
            fishery.objects.Add(position, chest);
            return chest;
        }
        return null;
    }

    private static Item Clone(Item item) { var copy = item.getOne(); copy.Stack = item.Stack; return copy; }

    private static bool TryStore(Chest target, List<Item> contents)
    {
        var before = target.Items.Select(item => item == null ? null : Clone(item)).ToArray();
        var trial = new Chest(true, "130");
        foreach (var item in before) if (item != null) trial.Items.Add(Clone(item));
        foreach (var item in contents) if (trial.addItem(Clone(item)) != null) return false;
        try
        {
            foreach (var item in contents)
                if (target.addItem(Clone(item)) != null) throw new InvalidOperationException("Recovery chest changed during transfer");
            return true;
        }
        catch
        {
            target.Items.Clear(); foreach (var item in before) target.Items.Add(item);
            throw;
        }
    }
}

public sealed class RecoveryApi(ModEntry mod)
{
    public int RecoverNow() => mod.RecoverNow();
    public bool CanChangeShipment() => ShipmentRebooking.CanChange();
    public string ChangeShipment() => ShipmentRebooking.Change(mod.Monitor);
}
