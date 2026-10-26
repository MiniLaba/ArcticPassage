using Microsoft.Xna.Framework;
using StardewModdingAPI;
using StardewModdingAPI.Events;
using StardewValley;
using StardewValley.Menus;
using StardewValley.SpecialOrders;

namespace ArcticPassage.Runtime;

/// <summary>Local access to the native team board; engine owns acceptance, objectives and rewards.</summary>
internal sealed class WeeklyOrders
{
    internal const string BoardType = "ArcticPassage_Weekly";
    internal const string StoryBoardType = "ArcticPassage_Story";
    private const string WeekKey = "WhiteBay.ArcticPassage/ContractWeek";
    private readonly IModHelper helper;
    private readonly IMonitor monitor;
    private SpecialOrdersBoard? opened;
    private QuestContainerMenu? crate;
    private bool waitingForCrate;
    private int crateSlot;
    private int choice;
    internal WeeklyOrders(IModHelper helper, IMonitor monitor)
    {
        this.helper = helper; this.monitor = monitor;
        GameLocation.RegisterTileAction("ArcticPassageWeekly", Open);
        GameLocation.RegisterTileAction("ArcticPassageFishCrate", OpenCrate);
        helper.Events.GameLoop.SaveLoaded += (_, _) => Refresh();
        helper.Events.GameLoop.DayStarted += (_, _) => Refresh();
        helper.Events.Input.ButtonPressed += OnButton;
        helper.Events.Display.MenuChanged += (_, e) => {
            if (!ReferenceEquals(e.NewMenu, opened)) opened = null;
            // The native donation mutex opens its menu on a later update, including in single player.
            if (waitingForCrate && e.NewMenu is QuestContainerMenu box && Game1.currentLocation?.Name == "ArcticPassage_CommunityHouse")
            {
                crate = box; crateSlot = 0; waitingForCrate = false;
                monitor.Log("WEEKLY native fish crate opened after lock", LogLevel.Trace);
            }
            else if (e.NewMenu != null) waitingForCrate = false;
            if (!ReferenceEquals(e.NewMenu, crate)) crate = null;
        };
        helper.Events.GameLoop.ReturnedToTitle += (_, _) => { waitingForCrate = false; crate = null; opened = null; };
        helper.Events.Player.Warped += (_, e) => { if (e.IsLocalPlayer) waitingForCrate = false; };
        helper.Events.Display.RenderedActiveMenu += Draw;
    }
    private void Refresh()
    {
        if (!Context.IsWorldReady || !Context.IsMainPlayer || !Game1.MasterPlayer.mailReceived.Contains("ArcticPassage_Shed")) return;
        string week = (Game1.Date.TotalDays / 7).ToString(System.Globalization.CultureInfo.InvariantCulture);
        bool changed = !Game1.MasterPlayer.modData.TryGetValue(WeekKey, out string? old) || old != week;
        // Refresh only our board. Never clear Valley/Qi offers or their accepted types.
        SpecialOrder.UpdateAvailableSpecialOrders(BoardType, changed);
        if (!changed) return;
        Game1.player.team.acceptedSpecialOrderTypes.Remove(BoardType);
        Game1.player.team.acceptedSpecialOrderTypes.Remove(StoryBoardType);
        Game1.MasterPlayer.modData[WeekKey] = week;
        monitor.Log($"WEEKLY refreshed native Arctic board week={week}", LogLevel.Trace);
    }
    private bool Open(GameLocation location, string[] args, Farmer who, Point tile)
    {
        if (location.Name != "ArcticPassage_CommunityHouse" || tile != new Point(5, 5)) return false;
        if (!Game1.MasterPlayer.mailReceived.Contains("ArcticPassage_Shed"))
        { Game1.drawObjectDialogue(helper.Translation.Get("weekly.locked")); return true; }
        Refresh();
        bool story = (who.mailReceived.Contains("ArcticPassage_StormSuppliesUnlocked")
            && !who.mailReceived.Contains("ArcticPassage_StormSuppliesComplete"))
            || (who.mailReceived.Contains("ArcticPassage_StormFishUnlocked")
                && !who.mailReceived.Contains("ArcticPassage_StormFishComplete"));
        if (story) SpecialOrder.UpdateAvailableSpecialOrders(StoryBoardType, true);
        var board = new SpecialOrdersBoard(story ? StoryBoardType : BoardType);
        choice = 0; Game1.activeClickableMenu = board; opened = board;
        monitor.Log("WEEKLY opened native board; no contract accepted on opening", LogLevel.Trace);
        return true;
    }
    private bool OpenCrate(GameLocation location, string[] args, Farmer who, Point tile)
    {
        if (location.Name != "ArcticPassage_CommunityHouse" || tile != new Point(3, 5)) return false;
        string dropBox = who.team.specialOrders.Any(o => o.UsesDropBox("ArcticPassage_StormSupplies"))
            ? "ArcticPassage_StormSupplies"
            : who.team.specialOrders.Any(o => o.UsesDropBox("ArcticPassage_FishCrate"))
                ? "ArcticPassage_FishCrate" : "";
        if (dropBox.Length == 0)
        { Game1.drawObjectDialogue(helper.Translation.Get("weekly.crate.empty")); return true; }
        waitingForCrate = true;
        crateSlot = 0;
        location.performAction("DropBox " + dropBox, who, new xTile.Dimensions.Location(3, 5));
        monitor.Log($"WEEKLY requested native drop box lock id={dropBox}", LogLevel.Trace);
        return true;
    }
    private void OnButton(object? sender, ButtonPressedEventArgs e)
    {
        if (crate != null && ReferenceEquals(Game1.activeClickableMenu, crate) && crate.GetChildMenu() == null && !e.IsSuppressed())
        {
            int count = Math.Min(Game1.player.MaxItems, crate.inventory.inventory.Count);
            if (count == 0) return;
            if (e.Button is SButton.Left or SButton.Right or SButton.Up or SButton.Down)
            {
                int delta = e.Button == SButton.Left ? -1 : e.Button == SButton.Right ? 1 : e.Button == SButton.Up ? -12 : 12;
                crateSlot = (crateSlot + delta + count) % count;
                helper.Input.Suppress(e.Button); return;
            }
            if (e.Button == SButton.Enter)
            {
                helper.Input.Suppress(e.Button);
                var slot = crate.inventory.inventory[crateSlot];
                // Native handler validates the tags/capacity and transfers only what the contract still needs.
                crate.receiveLeftClick(slot.bounds.Center.X, slot.bounds.Center.Y, true);
                monitor.Log($"WEEKLY native crate selected backpack slot={crateSlot}", LogLevel.Trace);
            }
            return;
        }
        if (opened == null || !ReferenceEquals(Game1.activeClickableMenu, opened) || opened.GetChildMenu() != null || e.IsSuppressed()) return;
        if (e.Button is SButton.Left or SButton.Right or SButton.Tab)
        { choice = e.Button == SButton.Left ? 0 : e.Button == SButton.Right ? 1 : 1-choice; helper.Input.Suppress(e.Button); return; }
        if (e.Button != SButton.Enter) return;
        helper.Input.Suppress(e.Button);
        var button = choice == 0 ? opened.acceptLeftQuestButton : opened.acceptRightQuestButton;
        if (button == null || !button.visible) return;
        int before = Game1.player.team.specialOrders.Count;
        opened.receiveLeftClick(button.bounds.Center.X, button.bounds.Center.Y, true);
        monitor.Log($"WEEKLY native accept choice={choice} active={before}->{Game1.player.team.specialOrders.Count}", LogLevel.Trace);
    }
    private void Draw(object? sender, RenderedActiveMenuEventArgs e)
    {
        if (crate != null && ReferenceEquals(Game1.activeClickableMenu, crate))
        {
            e.SpriteBatch.DrawString(Game1.smallFont,helper.Translation.Get("weekly.crate.keys"),new Vector2(24,60),new Color(240,235,215));
            Rectangle b = crate.inventory.inventory[crateSlot].bounds;
            e.SpriteBatch.Draw(Game1.staminaRect,new Rectangle(b.X,b.Bottom-4,b.Width,4),new Color(149,214,207));
            return;
        }
        if (opened == null || !ReferenceEquals(Game1.activeClickableMenu, opened)) return;
        string text = helper.Translation.Get("weekly.keys");
        Vector2 size = Game1.smallFont.MeasureString(text);
        int x = Math.Max(16, (Game1.uiViewport.Width-(int)size.X)/2);
        e.SpriteBatch.Draw(Game1.staminaRect, new Rectangle(x-10, 52, (int)size.X+20, (int)size.Y+16), new Color(22,45,57)*.94f);
        e.SpriteBatch.DrawString(Game1.smallFont,text,new Vector2(x,60),new Color(240,235,215));
        var button = choice == 0 ? opened.acceptLeftQuestButton : opened.acceptRightQuestButton;
        if (button == null || !button.visible) return;
        Rectangle a=button.bounds;
        foreach (var line in new[]{new Rectangle(a.X-3,a.Y-3,a.Width+6,3),new Rectangle(a.X-3,a.Bottom,a.Width+6,3),new Rectangle(a.X-3,a.Y,3,a.Height),new Rectangle(a.Right,a.Y,3,a.Height)})
            e.SpriteBatch.Draw(Game1.staminaRect,line,new Color(149,214,207));
    }
}
