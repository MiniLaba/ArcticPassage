using Microsoft.Xna.Framework;
using StardewModdingAPI;
using StardewModdingAPI.Events;
using StardewValley;
using StardewValley.Menus;
using StardewValley.Quests;
using StardewValley.SpecialOrders;

namespace ArcticPassage.Runtime;

/// <summary>Open a completed bay quest in the native journal; native clicks own payment.</summary>
internal sealed class KeyboardJournal
{
    private static KeyboardJournal? instance;
    private readonly IModHelper helper;
    private readonly IMonitor monitor;
    private QuestLog? opened;

    internal static bool HasReward => Context.IsWorldReady && (Game1.player.questLog.Any(IsReward) || Game1.player.team.specialOrders.Any(IsReward));
    private static bool IsReward(IQuest q) => q switch
    {
        Quest quest => quest.id.Value.StartsWith("ArcticPassage_") && quest.completed.Value && quest.HasReward(),
        SpecialOrder order => order.orderType.Value is WeeklyOrders.BoardType or WeeklyOrders.StoryBoardType && order.HasReward(),
        _ => false
    };

    internal KeyboardJournal(IModHelper helper, IMonitor monitor)
    {
        this.helper = helper; this.monitor = monitor; instance = this;
        helper.Events.Input.ButtonPressed += OnButton;
        helper.Events.Display.MenuChanged += (_, e) =>
        { if (!ReferenceEquals(e.NewMenu, opened)) opened = null; };
        helper.Events.Display.RenderedActiveMenu += (_, e) =>
        {
            if (opened == null || !ReferenceEquals(Game1.activeClickableMenu, opened)) return;
            string text = helper.Translation.Get("journal.keys");
            Vector2 size = Game1.smallFont.MeasureString(text);
            int x = Math.Max(16, (Game1.uiViewport.Width - (int)size.X) / 2);
            e.SpriteBatch.Draw(Game1.staminaRect, new Rectangle(x - 10, 64, (int)size.X + 20, (int)size.Y + 16), new Color(22, 45, 57) * .94f);
            e.SpriteBatch.DrawString(Game1.smallFont, text, new Vector2(x, 72), new Color(240, 235, 215));
        };
    }

    internal static bool OpenReward() => instance?.Open() == true;

    private bool Open()
    {
        IQuest? reward = (IQuest?)Game1.player.questLog.FirstOrDefault(IsReward) ?? Game1.player.team.specialOrders.FirstOrDefault(IsReward);
        if (reward == null || Game1.eventUp) return false;
        var journal = new QuestLog();
        var pages = helper.Reflection.GetField<List<List<IQuest>>>(journal, "pages").GetValue();
        for (int page = 0; page < pages.Count; page++)
        {
            int row = pages[page].FindIndex(q => ReferenceEquals(q, reward));
            if (row < 0) continue;
            var buttons = helper.Reflection.GetField<List<ClickableComponent>>(journal, "questLogButtons").GetValue();
            if (row >= buttons.Count) return false;
            helper.Reflection.GetField<int>(journal, "currentPage").SetValue(page);
            opened = journal;
            Game1.activeClickableMenu = journal;
            var bounds = buttons[row].bounds;
            journal.receiveLeftClick(bounds.Center.X, bounds.Center.Y, true);
            monitor.Log($"JOURNAL opened native reward page for {RewardId(reward)}; no payment on opening", LogLevel.Trace);
            return true;
        }
        return false;
    }

    private void OnButton(object? sender, ButtonPressedEventArgs e)
    {
        if (e.Button != SButton.Enter || e.IsSuppressed() || !Context.IsWorldReady || opened == null
            || !ReferenceEquals(Game1.activeClickableMenu, opened) || opened.GetChildMenu() != null) return;
        // Only the journal opened explicitly from our guide, with our completed
        // money quest actually shown. No direct money/reward/removal mutations.
        if (helper.Reflection.GetField<IQuest?>(opened, "_shownQuest").GetValue() is not IQuest quest || !IsReward(quest)
            || !helper.Reflection.GetMethod(opened, "HasMoneyReward").Invoke<bool>()) return;
        var box = helper.Reflection.GetField<ClickableTextureComponent>(opened, "rewardBox").GetValue();
        if (box == null) return;
        helper.Input.Suppress(e.Button);
        int before = Game1.player.Money;
        opened.receiveLeftClick(box.bounds.Center.X, box.bounds.Center.Y, true);
        monitor.Log($"JOURNAL native reward click {RewardId(quest)}: wallet {before}->{Game1.player.Money}", LogLevel.Info);
    }
    private static string RewardId(IQuest q) => q is Quest quest ? quest.id.Value : ((SpecialOrder)q).questKey.Value;
}
