using Microsoft.Xna.Framework;
using StardewModdingAPI;
using StardewModdingAPI.Events;
using StardewValley;
using StardewValley.Menus;

namespace ArcticPassage.Runtime;

/// <summary>Opt-in access to native title and character-creation actions.</summary>
internal sealed class KeyboardStart
{
    private readonly IModHelper helper;
    private readonly IMonitor monitor;
    private bool enabled;
    private LoadGameMenu? loadMenu;
    private int loadSelection;

    internal KeyboardStart(IModHelper helper, IMonitor monitor)
    {
        this.helper = helper;
        this.monitor = monitor;
        helper.Events.Input.ButtonPressed += OnButton;
        helper.Events.Display.RenderedActiveMenu += OnDraw;
        helper.Events.GameLoop.SaveLoaded += (_, _) => enabled = false;
        helper.Events.GameLoop.ReturnedToTitle += (_, _) => enabled = false;
    }

    private static TitleMenu? Title()
        => !Context.IsWorldReady && Game1.activeClickableMenu is TitleMenu title ? title : null;

    private void OnButton(object? sender, ButtonPressedEventArgs e)
    {
        var title = Title();
        if (title == null || e.IsSuppressed()) return;
        if (e.Button == SButton.F2)
        {
            enabled = !enabled;
            helper.Input.Suppress(e.Button);
            return;
        }
        if (!enabled) return;
        if (TitleMenu.subMenu == null && helper.Reflection.GetMethod(title, "ShouldAllowInteraction").Invoke<bool>())
        {
            string? action = e.Button switch { SButton.N => "New", SButton.L => "Load", _ => null };
            if (action == null) return;
            helper.Input.Suppress(e.Button);
            title.performButtonAction(action);
            monitor.Log($"KEYBOARD START native title action {action}", LogLevel.Trace);
        }
        else if (TitleMenu.subMenu is LoadGameMenu load && !load.IsDoingTask()
            && !helper.Reflection.GetField<bool>(load, "deleteConfirmationScreen").GetValue())
        {
            if (!ReferenceEquals(loadMenu, load)) { loadMenu = load; loadSelection = 0; }
            int count = load.MenuSlots.Count;
            if (count == 0) return;
            if (e.Button is SButton.Up or SButton.Down)
            {
                helper.Input.Suppress(e.Button);
                loadSelection = Math.Clamp(loadSelection + (e.Button == SButton.Up ? -1 : 1), 0, count - 1);
                var index = helper.Reflection.GetField<int>(load, "currentItemIndex");
                index.SetValue(Math.Clamp(loadSelection - 1, 0, Math.Max(0, count - 4)));
            }
            else if (e.Button == SButton.Enter)
            {
                helper.Input.Suppress(e.Button);
                int index = helper.Reflection.GetField<int>(load, "currentItemIndex").GetValue();
                var buttons = helper.Reflection.GetField<List<ClickableComponent>>(load, "slotButtons").GetValue();
                int row = loadSelection - index;
                if (row < 0 || row >= buttons.Count) return;
                // Click the left side of the native save row, away from its delete button.
                var bounds = buttons[row].bounds;
                load.receiveLeftClick(bounds.X + 48, bounds.Center.Y, true);
                monitor.Log("KEYBOARD START native save-row load", LogLevel.Trace);
            }
        }
        else if (TitleMenu.subMenu is CharacterCustomization creation && creation.GetChildMenu() == null)
        {
            if (e.Button == SButton.Enter && (helper.Input.IsDown(SButton.LeftControl) || helper.Input.IsDown(SButton.RightControl)))
            {
                helper.Input.Suppress(e.Button);
                bool valid = creation.canLeaveMenu();
                // Native validation and the native creation/intro pipeline own all state.
                var button = helper.Reflection.GetField<ClickableTextureComponent>(creation, "okButton").GetValue();
                creation.receiveLeftClick(button.bounds.Center.X, button.bounds.Center.Y, true);
                monitor.Log($"KEYBOARD START native creation confirm; valid={valid}", LogLevel.Trace);
            }
            else if (e.Button == SButton.F3)
            {
                var button = helper.Reflection.GetField<ClickableTextureComponent>(creation, "skipIntroButton").GetValue();
                if (button == null) return;
                helper.Input.Suppress(e.Button);
                creation.receiveLeftClick(button.bounds.Center.X, button.bounds.Center.Y, true);
                monitor.Log("KEYBOARD START native skip-intro checkbox clicked", LogLevel.Trace);
            }
            // Native Tab already cycles name, farm name and favourite thing.
        }
    }

    private void OnDraw(object? sender, RenderedActiveMenuEventArgs e)
    {
        if (Title() == null) return;
        string key = !enabled ? "start.hint" : TitleMenu.subMenu switch
        {
            null => "start.title",
            CharacterCustomization => "start.create",
            LoadGameMenu => "start.load",
            _ => "start.hint"
        };
        string text = Game1.parseText(helper.Translation.Get(key), Game1.smallFont, Math.Max(160, Game1.uiViewport.Width - 64));
        Vector2 size = Game1.smallFont.MeasureString(text);
        var panel = new Rectangle((Game1.uiViewport.Width - (int)size.X) / 2 - 12, 64, (int)size.X + 24, (int)size.Y + 16);
        e.SpriteBatch.Draw(Game1.staminaRect, panel, new Color(20, 43, 54) * 0.92f);
        e.SpriteBatch.DrawString(Game1.smallFont, text, new Vector2(panel.X + 12, panel.Y + 8), new Color(224, 241, 238));
        if (enabled && TitleMenu.subMenu is LoadGameMenu load && ReferenceEquals(loadMenu, load) && !load.IsDoingTask())
        {
            var buttons = helper.Reflection.GetField<List<ClickableComponent>>(load, "slotButtons").GetValue();
            int row = loadSelection - helper.Reflection.GetField<int>(load, "currentItemIndex").GetValue();
            if (row >= 0 && row < buttons.Count)
            {
                var rect = buttons[row].bounds;
                e.SpriteBatch.Draw(Game1.staminaRect, new Rectangle(rect.X + 8, rect.Y + 8, 4, rect.Height - 16), new Color(156, 222, 218));
            }
        }
    }
}
