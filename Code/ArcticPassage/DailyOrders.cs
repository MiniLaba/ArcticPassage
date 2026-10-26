using HarmonyLib;
using StardewModdingAPI;
using StardewValley;
using StardewValley.Menus;

namespace ArcticPassage.Runtime;

/// <summary>Quality-sensitive trades within the existing native daily counter.</summary>
internal sealed class DailyOrders
{
    private const string Shop = "ArcticPassage_Orders";
    private static IModHelper helper = null!;
    private static IMonitor monitor = null!;
    [ThreadStatic] private static Purchase? current;

    private sealed record Purchase(ShopMenu Menu, string Kind, string Fish, string Flag, Purchase? Previous);

    internal DailyOrders(IModHelper modHelper, IMonitor modMonitor, Harmony harmony)
    {
        helper = modHelper; monitor = modMonitor;
        harmony.Patch(AccessTools.Method(typeof(ShopMenu), "tryToPurchaseItem"),
            prefix: new HarmonyMethod(typeof(DailyOrders), nameof(Begin)),
            postfix: new HarmonyMethod(typeof(DailyOrders), nameof(Completed)),
            finalizer: new HarmonyMethod(typeof(DailyOrders), nameof(End)));
        harmony.Patch(AccessTools.Method(typeof(ShopMenu), "HasTradeItem"),
            prefix: new HarmonyMethod(typeof(DailyOrders), nameof(HasQualityFish)));
        harmony.Patch(AccessTools.Method(typeof(ShopMenu), "ConsumeTradeItem"),
            prefix: new HarmonyMethod(typeof(DailyOrders), nameof(ConsumeQualityFish)));
    }

    private static IEnumerable<QualityTrade.Lot> Inventory()
        => Game1.player.Items.Select((item, slot) => new QualityTrade.Lot(slot,
            item?.QualifiedItemId ?? "", item?.Quality ?? 0, item?.Stack ?? 0));

    private static bool Begin(ShopMenu __instance, ISalable __0, ref bool __result, out Purchase? __state)
    {
        __state = null;
        if (!Context.IsWorldReady || __instance.ShopId != Shop) return true;
        string? kind = __0.QualifiedItemId switch
        {
            "(O)ArcticPassage_RegularReceipt" => "Regular",
            "(O)ArcticPassage_RestaurantReceipt" => "Restaurant",
            "(O)ArcticPassage_ResearchReceipt" => "Research",
            "(O)ArcticPassage_PortTradeReceipt" => "PortTrade",
            "(O)ArcticPassage_ExportReceipt" => "Export",
            _ => null
        };
        if (kind == null || !__instance.itemPriceAndStock.TryGetValue(__0, out var stock)) return true;
        string flag = kind == "PortTrade" ? "ArcticPassage_PortTradeComplete"
            : $"ArcticPassage_Order_{kind}_{Game1.year}_{Game1.currentSeason}_{Game1.dayOfMonth}";
        // Reject a stale menu after a date change and stale stock after a paid
        // delivery. The original dated mail keys remain the save authority.
        if (Game1.player.mailReceived.Contains(flag)
            || stock.ActionsOnPurchase?.Contains("AddMail Current " + flag + " received") != true)
        {
            Game1.showRedMessage(helper.Translation.Get("daily.reopen"));
            __result = false; return false;
        }
        if (kind == "Restaurant" && (stock.TradeItemCount != 2
            || QualityTrade.Plan(Inventory(), stock.TradeItem, 2) == null))
        {
            Game1.showRedMessage(helper.Translation.Get("daily.quality"));
            __result = false; return false;
        }
        __state = new(__instance, kind, stock.TradeItem, flag, current);
        current = __state;
        return true;
    }

    private static bool IsRestaurant(ShopMenu menu, string id)
        => current is { Kind: "Restaurant" } p && ReferenceEquals(p.Menu, menu) && p.Fish == id;

    private static bool HasQualityFish(ShopMenu __instance, string __0, int __1, ref bool __result)
    {
        if (!IsRestaurant(__instance, __0)) return true;
        __result = QualityTrade.Plan(Inventory(), __0, __1) != null;
        return false;
    }

    private static bool ConsumeQualityFish(ShopMenu __instance, string __0, int __1)
    {
        if (!IsRestaurant(__instance, __0)) return true;
        var plan = QualityTrade.Plan(Inventory(), __0, __1)
            ?? throw new InvalidOperationException("Restaurant stock changed during native purchase; refusing partial delivery.");
        foreach (var take in plan)
        {
            var item = Game1.player.Items[take.Slot];
            item.Stack -= take.Count;
            if (item.Stack == 0) Game1.player.Items[take.Slot] = null;
        }
        return false;
    }

    private static void Completed(Purchase? __state)
    {
        // Only the native successful purchase can create this date's receipt.
        // Stock/price, gold, receipt item and daily mail are still native.
        if (__state == null || !Game1.player.mailReceived.Contains(__state.Flag)) return;
        if (__state.Kind == "Restaurant")
        {
            var mira = Game1.getCharacterFromName("ArcticPassage_Mira");
            if (mira != null)
            {
                // A visitor can deliver to the counter before speaking to
                // Mira. Native changeFriendship ignores unknown friends.
                if (!Game1.player.friendshipData.ContainsKey(mira.Name))
                    Game1.player.friendshipData.Add(mira.Name, new Friendship(0));
                Game1.player.changeFriendship(25, mira);
            }
        }
        else if (__state.Kind == "Research")
        {
            // A delivered sample is a real source for the later research book;
            // it doesn't grant observation entries, points or research rewards.
            string key = "WhiteBay.ArcticPassage/ResearchSample/" + __state.Fish;
            if (!Game1.player.modData.ContainsKey(key))
                Game1.player.modData[key] = $"{Game1.year}|{Game1.currentSeason}|{Game1.dayOfMonth}";
        }
        monitor.Log($"DAILY native {__state.Kind} delivery {__state.Fish}; dated receipt={__state.Flag}", LogLevel.Trace);
    }

    private static Exception? End(Exception? __exception, Purchase? __state)
    {
        if (__state != null) current = __state.Previous;
        return __exception;
    }
}
