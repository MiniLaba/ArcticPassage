using Microsoft.Xna.Framework;
using StardewModdingAPI;
using StardewModdingAPI.Events;
using StardewValley;
using StardewValley.Menus;

namespace ArcticPassage.Runtime;

/// <summary>Optional keyboard navigation for the bay's native shop menus.</summary>
internal sealed class KeyboardCounters
{
    private readonly IModHelper helper;
    private readonly IMonitor monitor;
    private ShopMenu? menu;
    private bool enabled;
    private bool inventory;
    private int slot;
    private int offer;
    private static readonly HashSet<string> Shops = ["ArcticPassage_Market", "ArcticPassage_Supplies", "ArcticPassage_Orders"];

    internal KeyboardCounters(IModHelper helper, IMonitor monitor)
    {
        this.helper = helper; this.monitor = monitor;
        helper.Events.Display.MenuChanged += (_, _) => { menu = null; enabled = false; slot = offer = 0; };
        helper.Events.Input.ButtonPressed += OnButton;
        helper.Events.Display.RenderedActiveMenu += OnDraw;
    }

    private ShopMenu? Current()
    {
        if (Game1.activeClickableMenu is not ShopMenu shop || !Shops.Contains(shop.ShopId) || shop.GetChildMenu() != null) return null;
        if (!ReferenceEquals(menu, shop)) { menu = shop; enabled = false; slot = offer = 0; }
        return shop;
    }

    private void OnButton(object? sender, ButtonPressedEventArgs e)
    {
        var shop = Current();
        if (shop == null || e.IsSuppressed()) return;
        if (e.Button == SButton.MouseLeft || e.Button == SButton.MouseRight) { enabled = false; return; }
        if (e.Button == SButton.Tab)
        {
            inventory = !enabled ? shop.forSale.Count == 0 : !inventory;
            if (shop.forSale.Count == 0) inventory = true;
            enabled = true; helper.Input.Suppress(e.Button); return;
        }
        if (!enabled) return;
        int delta = e.Button switch { SButton.Left => -1, SButton.Right => 1, SButton.Up => inventory ? -12 : -1, SButton.Down => inventory ? 12 : 1, _ => 0 };
        if (delta != 0)
        {
            if (inventory) slot = Math.Clamp(slot + delta, 0, Math.Min(Game1.player.MaxItems, shop.inventory.inventory.Count) - 1);
            else offer = Math.Clamp(offer + delta, 0, Math.Max(0, shop.forSale.Count - 1));
            helper.Input.Suppress(e.Button); return;
        }
        if (e.Button != SButton.Enter) return;
        helper.Input.Suppress(e.Button);
        var bounds = Selection(shop);
        if (bounds == null) return;
        int gold = Game1.player.Money;
        string item = inventory ? Game1.player.Items.ElementAtOrDefault(slot)?.QualifiedItemId ?? "empty" : shop.forSale.ElementAtOrDefault(offer)?.QualifiedItemId ?? "empty";
        // Use the public native interaction path: its stock, recipe, price,
        // sale eligibility, trade and inventory-capacity rules all still run.
        shop.receiveLeftClick(bounds.Value.Center.X, bounds.Value.Center.Y, true);
        monitor.Log($"KEYBOARD COUNTER {shop.ShopId} {(inventory ? "inventory" : "offer")} {item}: gold {gold} -> {Game1.player.Money}", LogLevel.Trace);
        slot = Math.Clamp(slot, 0, Math.Max(0, Game1.player.MaxItems - 1));
        offer = Math.Clamp(offer, 0, Math.Max(0, shop.forSale.Count - 1));
    }

    private Rectangle? Selection(ShopMenu shop)
    {
        if (inventory)
        {
            if (slot >= shop.inventory.inventory.Count || slot >= Game1.player.MaxItems) return null;
            return shop.inventory.inventory[slot].bounds;
        }
        if (shop.forSale.Count == 0 || shop.forSaleButtons.Count == 0) return null;
        offer = Math.Clamp(offer, 0, shop.forSale.Count - 1);
        int rows = shop.forSaleButtons.Count;
        if (offer < shop.currentItemIndex) shop.currentItemIndex = offer;
        if (offer >= shop.currentItemIndex + rows) shop.currentItemIndex = offer - rows + 1;
        return shop.forSaleButtons[offer - shop.currentItemIndex].bounds;
    }

    private void OnDraw(object? sender, RenderedActiveMenuEventArgs e)
    {
        var shop = Current(); if (shop == null) return;
        if (enabled && Selection(shop) is Rectangle rect)
        {
            Color color = new(156, 222, 218);
            foreach (var edge in new[] { new Rectangle(rect.X, rect.Y, rect.Width, 3), new Rectangle(rect.X, rect.Bottom - 3, rect.Width, 3), new Rectangle(rect.X, rect.Y, 3, rect.Height), new Rectangle(rect.Right - 3, rect.Y, 3, rect.Height) })
                e.SpriteBatch.Draw(Game1.staminaRect, edge, color);
        }
        string key = !enabled ? "counter.start" : inventory ? "counter.sell" : shop.ShopId == "ArcticPassage_Orders" ? "counter.trade" : "counter.buy";
        string text = helper.Translation.Get(key);
        text = Game1.parseText(text, Game1.smallFont, Math.Max(160, Game1.uiViewport.Width - 48));
        Vector2 size = Game1.smallFont.MeasureString(text);
        var panel = new Rectangle((Game1.uiViewport.Width - (int)size.X) / 2 - 12, Math.Max(24, shop.yPositionOnScreen - (int)size.Y - 24), (int)size.X + 24, (int)size.Y + 16);
        e.SpriteBatch.Draw(Game1.staminaRect, panel, new Color(20, 43, 54) * 0.95f);
        e.SpriteBatch.DrawString(Game1.smallFont, text, new Vector2(panel.X + 12, panel.Y + 8), new Color(224, 241, 238));
    }
}
